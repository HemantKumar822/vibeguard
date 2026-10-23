"""Incremental multipart staging. Untrusted names never become disk paths."""
import hashlib
import asyncio
import json
import re
import unicodedata
from pathlib import PurePosixPath
from python_multipart import MultipartParser
from python_multipart.multipart import parse_options_header
from pydantic import ValidationError
from backend.api.session import IntakeError
from backend.core.contracts import CodebaseMetadata
from backend.core.policy import LIMITS

RESERVED = re.compile(r'^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?$', re.I)
PART = re.compile(r'^[A-Za-z0-9_-]{1,64}$')
SOURCE = {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.json', '.yaml', '.yml', '.toml', '.html', '.css', '.scss'}
CONFIG = {'.env', '.gitignore', '.npmrc', '.nvmrc', 'Dockerfile', 'yarn.lock', 'pnpm-lock.yaml', 'package-lock.json'}
EXCLUDED = {'node_modules', 'vendor', 'dist', 'build', '.git', '.next', 'coverage'}
TOTAL_UPLOAD_SECONDS = 120
IDLE_UPLOAD_SECONDS = 15


def exclusion_reason(relative_path, content):
    path=PurePosixPath(relative_path)
    if content.startswith(b'version https://git-lfs.github.com/spec/v1\n'): return 'git_lfs_pointer_not_retrieved'
    if any(p.casefold() in EXCLUDED for p in path.parts): return 'vendor_or_build_output'
    if path.suffix.casefold() not in SOURCE and path.name not in CONFIG and not path.name.startswith('.env.'):
        return 'unsupported_file_type'
    try:
        if '\x00' in content.decode('utf-8'): return 'binary_content'
    except UnicodeDecodeError: return 'binary_content'
    return None

def safe_paths(metadata):
    paths, ids = set(), set()
    for item in metadata.files:
        value = item.relative_path
        parts = value.split('/')
        if (not value or len(value.encode('utf-8')) > LIMITS['path_bytes'] or len(parts) > LIMITS['path_depth']
            or any(p in {'', '.', '..'} or p.endswith((' ', '.')) or RESERVED.fullmatch(p) for p in parts)
            or any(ord(c) < 32 or ord(c) == 127 or c in '\\:<>"|?*' for c in value)
            or unicodedata.normalize('NFKC', value) != value
            or re.search(r'(?:AKIA[A-Z0-9]{16}|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,})', value)):
            raise IntakeError(422, 'unsafe_path', 'files')
        key = value.casefold()
        if not PART.fullmatch(item.part_id) or RESERVED.fullmatch(item.part_id) or item.part_id in ids or key in paths:
            raise IntakeError(422, 'duplicate_mapping', 'files')
        ids.add(item.part_id)
        paths.add(key)
    for key in paths:
        if any('/'.join(key.split('/')[:i]) in paths for i in range(1, len(key.split('/')))):
            raise IntakeError(422, 'path_conflict', 'files')

async def receive(request, directory):
    kind, options = parse_options_header(request.headers.get('content-type', ''))
    boundary = options.get(b'boundary', b'')
    if kind != b'multipart/form-data' or not boundary or len(boundary) > 70:
        raise IntakeError(400, 'multipart_required')
    state = {'file_total': 0, 'total': 0, 'count': 0, 'ended': False, 'parts': {}, 'metadata': None}
    def begin():
        state.update(headers={}, field=bytearray(), value=bytearray(), header_size=0, size=0, handle=None, name=None, data=bytearray(), digest=hashlib.sha256())
        state['count'] += 1
        if state['count'] > LIMITS['files'] + 1:
            raise IntakeError(413, 'too_many_parts')
    def header_piece(target, data, start, end):
        state['header_size'] += end - start
        if state['header_size'] > LIMITS['header_bytes']:
            raise IntakeError(413, 'headers_too_large')
        state[target].extend(data[start:end])
    def header_end():
        key = bytes(state['field']).lower()
        if key in state['headers']:
            raise IntakeError(400, 'duplicate_header')
        state['headers'][key] = bytes(state['value'])
        state['field'].clear(); state['value'].clear()
    def headers_done():
        disposition, params = parse_options_header(state['headers'].get(b'content-disposition', b''))
        name = params.get(b'name', b'').decode('ascii', errors='replace')
        if disposition != b'form-data' or RESERVED.fullmatch(name) or (name != 'metadata' and not PART.fullmatch(name)):
            raise IntakeError(400, 'invalid_part')
        if name in state['parts'] or name == 'metadata' and state['metadata'] is not None:
            raise IntakeError(400, 'duplicate_part')
        mime, _ = parse_options_header(state['headers'].get(b'content-type', b''))
        if mime.lower() in {b'application/x-symlink', b'inode/symlink', b'inode/blockdevice', b'inode/chardevice'}:
            raise IntakeError(422, 'unsupported_part_type')
        state['name'] = name
        if name != 'metadata':
            state['handle'] = (directory / name).open('xb')
    def data(data, start, end):
        piece = data[start:end]
        state['size'] += len(piece)
        state['total'] += len(piece)
        cap = LIMITS['metadata_bytes'] if state['name'] == 'metadata' else LIMITS['file_bytes']
        if state['size'] > cap or state['total'] > LIMITS['aggregate_bytes'] + LIMITS['metadata_bytes']:
            raise IntakeError(413, 'upload_too_large')
        if state['name'] == 'metadata':
            state['data'].extend(piece)
        else:
            state['file_total'] += len(piece)
            if state['file_total'] > LIMITS['aggregate_bytes']:
                raise IntakeError(413, 'upload_too_large')
            state['handle'].write(piece)
            state['digest'].update(piece)
    def end():
        if state['handle']:
            state['handle'].close(); state['handle'] = None
        if state['name'] == 'metadata':
            state['metadata'] = bytes(state['data'])
        else:
            state['parts'][state['name']] = (state['size'], state['digest'].hexdigest())
    parser = MultipartParser(boundary, {'on_part_begin': begin, 'on_header_field': lambda d,s,e: header_piece('field',d,s,e),
        'on_header_value': lambda d,s,e: header_piece('value',d,s,e), 'on_header_end': header_end,
        'on_headers_finished': headers_done, 'on_part_data': data, 'on_part_end': end,
        'on_end': lambda: state.update(ended=True)})
    wire = 0
    try:
        deadline = asyncio.get_running_loop().time() + TOTAL_UPLOAD_SECONDS
        stream = request.stream().__aiter__()
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise TimeoutError
            try:
                chunk = await asyncio.wait_for(anext(stream), min(IDLE_UPLOAD_SECONDS, remaining))
            except StopAsyncIteration:
                break
            if asyncio.get_running_loop().time() >= deadline:
                raise TimeoutError
            wire += len(chunk)
            if wire > LIMITS['aggregate_bytes'] + LIMITS['metadata_bytes'] + (LIMITS['files'] + 1) * LIMITS['header_bytes']:
                raise IntakeError(413, 'upload_too_large')
            for offset in range(0, len(chunk), 65536):
                parser.write(chunk[offset:offset + 65536])
        parser.finalize()
        if not state['ended'] or state['metadata'] is None:
            raise IntakeError(400, 'incomplete_multipart')
        try:
            raw = json.loads(state['metadata'])
            if not isinstance(raw, dict) or raw.get('authorization_confirmed') is not True:
                raise IntakeError(403, 'permission_required', 'authorization_confirmed')
            metadata = CodebaseMetadata.model_validate(raw)
        except (ValueError, ValidationError):
            raise IntakeError(422, 'invalid_metadata', 'metadata') from None
        if len(metadata.files) > LIMITS['files']:
            raise IntakeError(413, 'too_many_files')
        safe_paths(metadata)
        if {f.part_id for f in metadata.files} != state['parts'].keys():
            raise IntakeError(400, 'part_mapping_mismatch', 'files')
        if sum(v[0] for v in state['parts'].values()) > LIMITS['aggregate_bytes']:
            raise IntakeError(413, 'upload_too_large')
        accepted, exclusions = [], []
        for item in metadata.files:
            reason = exclusion_reason(item.relative_path, (directory / item.part_id).read_bytes())
            if reason:
                exclusions.append({'resource_key': item.relative_path, 'reason': reason})
                (directory / item.part_id).unlink()
            else:
                accepted.append(item.relative_path)
        if not accepted:
            raise IntakeError(422, 'no_reviewable_source', 'files')
        canonical_metadata = metadata.model_dump()
        canonical_metadata['files'] = sorted(canonical_metadata['files'], key=lambda item: item['part_id'])
        canonical = {'metadata': canonical_metadata, 'parts': state['parts']}
        digest = hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()
        # Publish the validated manifest separately; opaque staged filenames prevent OS alias tricks.
        (directory / 'manifest.json').write_text(json.dumps({'files': [f.model_dump() for f in metadata.files if f.relative_path in accepted]}))
        return metadata, accepted, exclusions, digest
    except IntakeError:
        raise
    except TimeoutError:
        raise IntakeError(400, 'upload_deadline_exceeded') from None
    except Exception:
        raise IntakeError(400, 'invalid_multipart') from None
    finally:
        if state.get('handle'):
            state['handle'].close()



