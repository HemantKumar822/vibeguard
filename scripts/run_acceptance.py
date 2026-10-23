"""Run real pinned scanners through API/worker boundaries. No submitted code executes.

Controlled repository retrieval and website capture are visibly labeled local seams,
never production runtime switches. --live additionally uses unchanged public transport.
"""
import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from backend.api.main import create_app
from backend.core.settings import Settings
from backend.core.lifecycle import Lifecycle
from backend.core.cleanup import Cleanup
from backend.evaluation.metrics import assert_sanitized, score, guidance, failed_rows, markdown, coverage_record
from workers.coordinator import run_once
from workers.launcher import Launcher
from workers import website

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / 'fixtures/acceptance'
SECRET = 'SyntheticCredential_1234567890'
URL = 'https://example.com/'


def capture(variant):
    body = (f'<html><script>const password = "{SECRET}";</script></html>' if variant == 'vulnerable'
            else '<!doctype html><html><body>Control</body></html>')
    # The public browser key is a negative credential control in every variant.
    body += '<script>const publicBrowserKey = "AIzaSyntheticPublicBrowserKey_123456789";</script>'
    headers = [('Content-Type', 'text/html')]
    if variant != 'vulnerable':
        headers += [('X-Content-Type-Options', 'nosniff'), ('X-Frame-Options', 'DENY'),
                    ('Content-Security-Policy', "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"),
                    ('Strict-Transport-Security', 'max-age=31536000; includeSubDomains'), ('Cache-Control', 'no-store')]
    return {'entries': [{'url': URL, 'status': 200, 'headers': headers, 'body': body.encode(), 'mime': 'text/html'}],
            'exclusions': [], 'complete': True, 'requests': 1, 'bytes': len(body.encode()), 'pages': 1, 'assets': 0}


def run(live=False, modes=('codebase', 'repository', 'website')):
    labels = json.loads((CORPUS / 'labels.json').read_text())
    launcher = Launcher()
    evidence = {'schema': 1, 'scanner_images': launcher.images, 'scanner_versions': launcher.versions,
                'corpus_sha256': hashlib.sha256(b''.join(p.read_bytes() for p in sorted(CORPUS.iterdir()) if p.suffix in {'.json', '.ts'})).hexdigest(),
                'policy_sha256': hashlib.sha256((ROOT / 'docs/PROJECT_RULES.md').read_bytes()).hexdigest(),
                'unsupported_website': labels['unsupported_website'], 'runs': [], 'comparisons': [],
                'release_blockers': ['Public labeled vulnerable/corrected deployments not available.',
                                     'Teammate prompt usefulness judgment unassessed.']}
    with tempfile.TemporaryDirectory(prefix='vg-acceptance-') as directory:
        app = create_app(Settings(Path(directory) / 'runtime', loopback_http=True))
        store = app.state.storage
        with TestClient(app) as client:
            origin = {'Origin': 'http://127.0.0.1:8000'}
            csrf = client.post('/api/v1/session', headers=origin).json()['csrf_token']
            for transport in (['controlled', 'live'] if live else ['controlled']):
                for mode in (['codebase', 'repository', 'website'] if transport == 'controlled' else ['repository', 'website']):
                    if mode not in modes: continue
                    baseline = None
                    for variant in (['vulnerable', 'corrected', 'clean'] if transport == 'controlled' else ['observation']):
                        data = (CORPUS / f'{variant}.ts').read_bytes() if transport == 'controlled' else b''
                        with ExitStack() as stack:
                            if transport == 'controlled' and mode == 'repository':
                                def retrieve(metadata, target):
                                    (target / 'f').write_bytes(data)
                                    (target / 'manifest.json').write_text(json.dumps({'files': [{'part_id': 'f', 'relative_path': 'app/src/main.ts'}]}))
                                    return ['app/src/main.ts'], [], 'https://github.com/fixture/acceptance', 'main', hashlib.sha1(data).hexdigest()
                                stack.enter_context(patch('backend.api.main.retrieve', retrieve))
                            if transport == 'controlled' and mode == 'website':
                                execute = website.execute
                                stack.enter_context(patch('workers.website.execute', lambda *args: execute(*args, capture_fn=lambda *_, **__: capture(variant))))
                            headers = {**origin, 'X-CSRF-Token': csrf, 'Idempotency-Key': f'{transport}-{mode}-{variant}'}
                            endpoint = '/api/v1/scans' + (f'/{baseline}/rescans' if baseline and variant == 'corrected' else '')
                            started = time.monotonic()
                            if mode == 'codebase':
                                metadata = {'mode': mode, 'authorization_confirmed': True, 'files': [{'part_id': 'f', 'relative_path': 'app/src/main.ts'}]}
                                response = client.post(endpoint, headers=headers, files=[('metadata', (None, json.dumps(metadata))), ('f', ('ignored', data))])
                            else:
                                body = {'mode': mode, 'authorization_confirmed': True}
                                body.update({'repository_url': 'https://github.com/HemantKumar822/vibeguard' if transport == 'live' else 'https://github.com/fixture/acceptance'} if mode == 'repository'
                                            else {'target_url': 'https://hemantkumar822.github.io/' if transport == 'live' else URL})
                                response = client.post(endpoint, headers=headers, json=body)
                            if response.status_code != 202:
                                evidence['runs'].append({'transport': transport, 'mode': mode, 'variant': variant, 'admission_status': response.status_code, 'error_code': response.json().get('error', {}).get('code'), 'completed': False})
                                continue
                            scan_id = response.json()['scan_id']
                            run_once(Lifecycle(store), Cleanup(store, launcher.stop), 'acceptance', launcher)
                            report = client.get('/api/v1/scans/' + scan_id).json()
                            assert_sanitized(report, [SECRET])
                            row = {'transport': transport, 'mode': mode, 'variant': variant,
                                   'elapsed_seconds': round(time.monotonic() - started, 3), 'status': report['status'],
                                   'completed': report['status'] == 'complete', 'input': report['input'],
                                   'coverage': coverage_record(report['coverage']),
                                   'tools': [{**tool, 'coverage': coverage_record(tool['coverage'])} for tool in report['tools']], 'guidance': guidance(report),
                                   'observed': [{'rule': f['rule_id'], 'location': f['location']} for f in report['findings']],
                                   'source_removed': not (store.staging / scan_id).exists()}
                            if transport == 'controlled': row['metrics'] = score(labels['website' if mode == 'website' else 'source'][variant], report['findings'])
                            else: row['metrics'] = None  # No ground truth for unlabelled public targets.
                            evidence['runs'].append(row)
                            if variant == 'corrected' and baseline:
                                comparison = client.get(f'/api/v1/scans/{baseline}/comparisons/{scan_id}')
                                result = comparison.json()
                                if comparison.status_code == 200:
                                    for key in ('baseline_coverage', 'new_coverage'): result[key] = coverage_record(result[key])
                                evidence['comparisons'].append({'mode': mode, 'http_status': comparison.status_code, 'result': result})
                            if variant == 'vulnerable': baseline = scan_id
                            if variant != 'vulnerable':
                                client.delete('/api/v1/scans/' + scan_id, headers=headers)
                                Cleanup(store, launcher.stop).sweep()
                    # Baseline must survive until its paired comparison has been read.
                    if baseline:
                        client.delete('/api/v1/scans/' + baseline, headers=headers)
                        Cleanup(store, launcher.stop).sweep()
            Cleanup(store, launcher.stop).sweep()
            evidence['remaining_source_directories'] = len(list(store.staging.iterdir()))
    assert_sanitized(evidence, [SECRET])
    if any(not row['completed'] for row in evidence['runs']):
        evidence['release_blockers'].append('One or more executed modes did not complete with intended coverage; inspect individual rows.')
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--live', action='store_true', help='Also scan the two existing authorized public team targets')
    parser.add_argument('--modes', nargs='+', choices=['codebase', 'repository', 'website'], default=['codebase', 'repository', 'website'])
    args = parser.parse_args()
    if args.output.suffix.lower() != '.json': parser.error('--output must end in .json (a sibling .md summary is also written)')
    evidence = run(args.live, args.modes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + '\n')
    args.output.with_suffix('.md').write_text(markdown(evidence), encoding='utf-8')
    failures = failed_rows(evidence)
    print(json.dumps({'runs': len(evidence['runs']), 'failed_checks': failures, 'output': str(args.output)}))
    return int(bool(failures))


if __name__ == '__main__': raise SystemExit(main())
