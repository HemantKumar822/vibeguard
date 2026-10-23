"""Fixed-provider retrieval. No git process, credentials, proxy or redirect following."""
import gzip
import hashlib
import http.client
import io
import ipaddress
import json
import re
import socket
import ssl
import tarfile
import time
import queue
import threading
from urllib.parse import quote, urlsplit
from backend.adapters.intake import exclusion_reason, safe_paths
from backend.api.session import IntakeError
from backend.core.contracts import CodebaseMetadata
from backend.core.policy import LIMITS

DOWNLOAD=25*1024*1024
UNPACKED=100*1024*1024
HOSTS={'api.github.com','codeload.github.com'}


def identity(url, ref):
    try:
        parsed=urlsplit(url)
        if parsed.scheme!='https' or parsed.netloc!='github.com' or parsed.query or parsed.fragment: raise ValueError
        match=re.fullmatch(r'/([A-Za-z0-9][A-Za-z0-9-]{0,38})/([A-Za-z0-9_.-]{1,100})/?',parsed.path)
        if not match: raise ValueError
        owner,repo=match.groups()
        repo=repo.removesuffix('.git')
        if repo in {'','.','..'}: raise ValueError
        if ref is not None and (not ref or len(ref.encode())>256 or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./~-]*',ref)
                                or '..' in ref or ref.endswith(('/', '.')) or '@{' in ref): raise ValueError
        return owner,repo
    except (ValueError,TypeError): raise IntakeError(422,'invalid_repository','repository_url') from None


def public_addresses(host,timeout=8):
    addresses=[]
    answer=queue.Queue(maxsize=1)
    def resolve():
        try: answer.put(socket.getaddrinfo(host,443,type=socket.SOCK_STREAM))
        except Exception as exc: answer.put(exc)
    threading.Thread(target=resolve,daemon=True).start()
    try: result=answer.get(timeout=timeout)
    except queue.Empty: raise TimeoutError('dns_timeout') from None
    if isinstance(result,Exception): raise OSError('dns_unavailable') from None
    for family,kind,proto,_,address in result:
        ip=ipaddress.ip_address(address[0])
        mapped=getattr(ip,'ipv4_mapped',None)
        if not ip.is_global or (mapped and not mapped.is_global): raise ValueError('blocked_destination')
        addresses.append((family,kind,proto,address))
    if not addresses: raise ValueError('unresolved_destination')
    return addresses


class PinnedHTTPS(http.client.HTTPSConnection):
    def connect(self):
        # Resolve exactly once, then connect to that numeric address. TLS still validates provider hostname.
        last=None
        deadline=time.monotonic()+self.timeout
        for family,kind,proto,address in public_addresses(self.host,min(8,self.timeout)):
            sock=socket.socket(family,kind,proto)
            try:
                remaining=deadline-time.monotonic()
                if remaining<=0: raise TimeoutError
                sock.settimeout(remaining); sock.connect(address)
                peer=ipaddress.ip_address(sock.getpeername()[0])
                if not peer.is_global or peer != ipaddress.ip_address(address[0]): raise ValueError('blocked_peer')
                sock.settimeout(max(.01,deadline-time.monotonic()))
                self.sock=self._context.wrap_socket(sock,server_hostname=self.host)
                return
            except Exception as exc:
                sock.close(); last=exc
        raise OSError('Provider connection unavailable') from last


def fetch(host, path, deadline, cap):
    if host not in HOSTS or not path.startswith('/') or '\r' in path or '\n' in path: raise ValueError('blocked_endpoint')
    remaining=deadline-time.monotonic()
    if remaining<=0: raise TimeoutError
    connection=PinnedHTTPS(host,443,timeout=min(8,remaining),context=ssl.create_default_context())
    def abort():
        try:
            if connection.sock: connection.sock.shutdown(socket.SHUT_RDWR)
        except OSError: pass
        connection.close()
    watchdog=threading.Timer(remaining,abort)
    watchdog.daemon=True
    watchdog.start()
    try:
        connection.request('GET',path,headers={'User-Agent':'VibeGuard-source-review','Accept':'application/vnd.github+json' if host=='api.github.com' else 'application/octet-stream','Accept-Encoding':'identity'})
        response=connection.getresponse()
        if response.status!=200 or response.getheader('Content-Encoding','identity')!='identity':
            raise ValueError('provider_rejected')
        if int(response.getheader('Content-Length','0'))>cap: raise ValueError('download_limit')
        output=bytearray()
        while True:
            remaining=deadline-time.monotonic()
            if remaining<=0: raise TimeoutError
            if connection.sock: connection.sock.settimeout(min(8,remaining))
            chunk=response.read1(min(65536,cap+1-len(output)))
            if not chunk: break
            output.extend(chunk)
            if len(output)>cap: raise ValueError('download_limit')
        return bytes(output)
    finally:
        watchdog.cancel()
        connection.close()


def extract(archive, directory, deadline):
    with gzip.GzipFile(fileobj=io.BytesIO(archive)) as compressed:
        # Bound decompression including tar headers and padding, before interpreting member paths.
        unpacked=compressed.read(min(UNPACKED,len(archive)*100)+1)
    if len(unpacked)>UNPACKED or len(unpacked)>len(archive)*100: raise ValueError('archive_expansion_limit')
    metadata=[]; accepted=[]; excluded=[]; bodies=[]
    root=None; total=0; entries=0
    with tarfile.open(fileobj=io.BytesIO(unpacked),mode='r:') as tar:
        for member in tar:
            entries+=1
            if time.monotonic()>deadline or entries>15000: raise ValueError('archive_limit')
            parts=member.name.split('/')
            if not parts[0] or any(part in {'.','..'} for part in parts): raise ValueError('unsafe_archive_path')
            if root is None: root=parts[0]
            if root!=parts[0]: raise ValueError('multiple_archive_roots')
            if len(parts)==1:
                if not member.isdir(): raise ValueError('invalid_archive_root')
                continue
            path='/'.join(parts[1:]).rstrip('/')
            if not path:
                if not member.isdir(): raise ValueError('invalid_archive_root')
                continue
            # Validate directories as well as files; no extraction APIs touch member names.
            safe_paths(CodebaseMetadata(mode='codebase',authorization_confirmed=True,files=[{'part_id':'check','relative_path':path}]))
            if member.isdir(): continue
            if not member.isfile() or member.issym() or member.islnk() or member.sparse: raise ValueError('archive_links_or_special')
            if member.size>LIMITS['file_bytes'] or member.size<0: raise ValueError('archive_file_limit')
            total+=member.size
            if total>LIMITS['aggregate_bytes'] or len(metadata)>=LIMITS['files']: raise ValueError('archive_source_limit')
            part_id=f'file_{len(metadata)}'
            metadata.append({'part_id':part_id,'relative_path':path})
            stream=tar.extractfile(member)
            if stream is None: raise ValueError('invalid_archive_member')
            content=stream.read(LIMITS['file_bytes']+1)
            if len(content)!=member.size: raise ValueError('invalid_archive_size')
            reason=exclusion_reason(path,content)
            if reason: excluded.append({'resource_key':path,'reason':reason})
            else: accepted.append(path); bodies.append((part_id,content))
    safe_paths(CodebaseMetadata(mode='codebase',authorization_confirmed=True,files=metadata))
    if not accepted: raise ValueError('no_reviewable_source')
    for part_id,content in bodies: (directory/part_id).write_bytes(content)
    (directory/'manifest.json').write_text(json.dumps({'files':[item for item in metadata if item['relative_path'] in accepted]}))
    return accepted,excluded


def retrieve(submission, directory):
    owner,repo=identity(submission.repository_url,submission.ref)
    deadline=time.monotonic()+60
    try:
        base=f'/repos/{owner}/{repo}'
        info=json.loads(fetch('api.github.com',base,deadline,1024*1024))
        if info.get('private') is not False or info.get('visibility','public')!='public': raise ValueError('public_only')
        requested=submission.ref or info['default_branch']
        identity(submission.repository_url,requested)
        commit=json.loads(fetch('api.github.com',base+'/commits/'+quote(requested,safe=''),deadline,1024*1024))['sha']
        if not isinstance(commit,str) or not re.fullmatch(r'[a-f0-9]{40}',commit): raise ValueError('invalid_commit')
        archive=fetch('codeload.github.com',f'/{owner}/{repo}/tar.gz/{commit}',deadline,DOWNLOAD)
        accepted,excluded=extract(archive,directory,deadline)
        if time.monotonic()>deadline: raise TimeoutError
        return accepted,excluded,f'https://github.com/{owner}/{repo}',requested,commit
    except Exception:
        # Never expose provider bodies, user URL values or source contents in errors/logs.
        raise IntakeError(422,'repository_retrieval_failed','repository_url') from None


def request_digest(submission):
    return hashlib.sha256(json.dumps(submission.model_dump(),sort_keys=True).encode()).hexdigest()
