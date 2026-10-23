"""Trusted container entrypoint: passive HAR import only, no network replay."""
import hashlib
import json
import os
import socket
from pathlib import Path
import subprocess
import time
from urllib.parse import urlencode
from urllib.request import build_opener, ProxyHandler


def main():
    if os.getuid()==0 or Path('/var/run/docker.sock').exists(): raise RuntimeError('unsafe_worker')
    if {path.name for path in Path('/sys/class/net').iterdir()}!={'lo'}: raise RuntimeError('network_bypass')
    status=Path('/proc/self/status').read_text()
    if 'NoNewPrivs:\t1' not in status or 'CapEff:\t0000000000000000' not in status: raise RuntimeError('unsafe_worker')
    for destination in (('1.1.1.1',443),('2606:4700:4700::1111',443)):
        family=socket.AF_INET6 if ':' in destination[0] else socket.AF_INET
        with socket.socket(family,socket.SOCK_STREAM) as sock:
            sock.settimeout(.5)
            try: sock.connect(destination)
            except OSError: pass
            else: raise RuntimeError('direct_egress_available')
    for name in ('/forbidden','/capture/forbidden'):
        try: Path(name).write_text('restriction-probe')
        except OSError: pass
        else: raise RuntimeError('writable_restricted_mount')
    cgroup=Path('/sys/fs/cgroup')
    if (cgroup/'memory.max').read_text().strip()!='2147483648' or (cgroup/'pids.max').read_text().strip()!='128': raise RuntimeError('unbounded_worker')
    quota,period=map(int,(cgroup/'cpu.max').read_text().split())
    scratch=os.statvfs('/tmp')
    if quota/period!=2 or scratch.f_blocks*scratch.f_frsize>268435456: raise RuntimeError('unbounded_worker')
    deadline=time.monotonic()+165
    opener=build_opener(ProxyHandler({}))
    def api(component,kind,method,**parameters):
        url=f'http://127.0.0.1:8090/JSON/{component}/{kind}/{method}/?'+urlencode(parameters)
        with opener.open(url,timeout=min(8,max(.1,deadline-time.monotonic()))) as response:
            raw=response.read(5*1024*1024+1)
        if len(raw)>5*1024*1024: raise ValueError('report_limit')
        value=json.loads(raw)
        if 'code' in value: raise ValueError('zap_api_failure')
        return value
    process=subprocess.Popen(['/zap/zap.sh','-daemon','-host','127.0.0.1','-port','8090',
        '-dir','/tmp/zap','-config','api.disablekey=true','-config','autoupdate.checkOnStart=false',
        '-config','autoupdate.checkAddonUpdates=false','-config','autoupdate.downloadNewRelease=false'],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        while True:
            if process.poll() is not None: raise RuntimeError('zap_startup_failed')
            try:
                version=api('core','view','version')['version']; break
            except Exception:
                if time.monotonic()>deadline-90: raise TimeoutError('zap_startup_timeout')
                time.sleep(.5)
        api('core','action','setMode',mode='safe')
        api('pscan','action','setScanOnlyInScope',onlyInScope='false')
        api('pscan','action','enableAllScanners')
        # Import recorded responses. Never use importHar's sendRequests/replay operation.
        imported=api('exim','action','importHar',filePath='/capture/capture.har')
        if imported.get('Result')!='OK': raise ValueError('har_import_failed')
        stable=0
        while stable<3:
            if time.monotonic()>deadline: raise TimeoutError('passive_scan_timeout')
            remaining=int(api('pscan','view','recordsToScan')['recordsToScan'])
            stable=stable+1 if remaining==0 else 0
            time.sleep(.5)
        messages=int(api('core','view','numberOfMessages')['numberOfMessages'])
        captured=json.loads(Path('/capture/capture.har').read_text())['log']['entries']
        expected=len(captured)
        if messages<expected or expected==0: raise ValueError('incomplete_har_import')
        urls={url.rstrip('/') for url in api('core','view','urls')['urls']}
        if any(entry['request']['url'].rstrip('/') not in urls for entry in captured): raise ValueError('incomplete_har_urls')
        alerts=api('core','view','alerts',start=0,count=1001)['alerts']
        plugins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/zap/plugin').glob('*.zap')
                 if p.name.startswith(('pscan','exim','network'))}
        print(json.dumps({'version':version,'alerts':alerts,'messages':messages,'expected':expected,
                          'plugins':plugins,'mode':'offline-passive-har','isolation_verified':True}),flush=True)
    finally:
        process.terminate()
        try: process.wait(timeout=5)
        except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=5)


if __name__=='__main__':
    try: main()
    except Exception:
        # Do not reveal raw HAR content, URLs, headers or vendor failure strings.
        print(json.dumps({'error':'zap_passive_execution_failed'}),flush=True)
        raise SystemExit(3)
