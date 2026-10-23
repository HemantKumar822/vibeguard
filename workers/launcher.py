"""Trusted coordinator-only Docker boundary. No uploaded command or configuration."""
import json
import re
import subprocess
import threading
import time
from scripts.scanner_readiness import locate_docker
from pathlib import Path

class Launcher:
    def __init__(self):
        evidence=json.loads((Path(__file__).resolve().parents[1]/'contracts/scanner-readiness.json').read_text())
        self.docker=locate_docker('docker') or 'docker'
        self.images={s['name']:s['digest'] for s in evidence['scanners'] if s['status']=='verified'}

    def command(self, tool, source, name):
        if tool not in {'gitleaks','semgrep'} or not re.fullmatch(r'vg-[a-f0-9]{32}-(gitleaks|semgrep)',name):
            raise ValueError('Unapproved worker')
        image=self.images[tool]
        if not re.fullmatch(r'[a-z0-9./-]+@sha256:[a-f0-9]{64}',image): raise ValueError('Unpinned image')
        # Version probes are diagnostic only; never translate them into scan coverage.
        args=['version'] if tool=='gitleaks' else ['semgrep','--version']
        return [self.docker,'run','--name',name,'--label','vibeguard.worker=1','--pull=never','--read-only','--network=none','--user=65532:65532','--cap-drop=ALL','--security-opt=no-new-privileges','--cpus=2','--memory=2g','--memory-swap=2g','--pids-limit=128','--tmpfs=/tmp:rw,noexec,nosuid,size=268435456','--log-driver=none','--env=HOME=/tmp','--env=SEMGREP_ENABLE_VERSION_CHECK=0','--env=SEMGREP_SEND_METRICS=off','--mount',f'type=bind,src={Path(source).resolve()},dst=/source,readonly',image,*args]

    def stop(self, scan_id):
        if not re.fullmatch(r'[a-f0-9]{32}',scan_id): raise RuntimeError('Invalid worker identity')
        for tool in ('gitleaks','semgrep'):
            name=f'vg-{scan_id}-{tool}'
            result=subprocess.run([self.docker,'container','inspect',name],capture_output=True,text=True,timeout=10)
            if result.returncode:
                if 'No such container' not in result.stderr and 'No such object' not in result.stderr:
                    raise RuntimeError('Worker cleanup could not be verified')
                # Distinguish missing containers from an unavailable daemon.
                subprocess.run([self.docker,'info','--format','{{.ServerVersion}}'],capture_output=True,timeout=10,check=True)
                continue
            subprocess.run([self.docker,'rm','--force',name],capture_output=True,timeout=10,check=True)

    def probe(self, tool, source, scan_id, timeout=90):
        # Drain through a fixed buffer, discard all vendor output, and stop at
        # the cap. No raw scanner text is persisted or returned to the API.
        name=f'vg-{scan_id}-{tool}'
        process=None
        exceeded=threading.Event()
        def drain():
            total=0
            while chunk := process.stdout.read(65536):
                total += len(chunk)
                if total > 5*1024*1024:
                    exceeded.set()
                    return
        try:
            process=subprocess.Popen(self.command(tool,source,name),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            reader=threading.Thread(target=drain,daemon=True); reader.start()
            deadline=time.monotonic()+min(timeout,90)
            while process.poll() is None:
                if time.monotonic()>=deadline or exceeded.is_set():
                    raise RuntimeError('Worker deadline/output limit')
                time.sleep(.02)
            reader.join(timeout=1)
            if reader.is_alive() or exceeded.is_set() or process.returncode:
                raise RuntimeError('Worker unavailable or output limit')
        finally:
            try:
                self.stop(scan_id)
            finally:
                if process is not None:
                    if process.poll() is None: process.kill()
                    process.wait(timeout=10)
                    if process.stdout: process.stdout.close()
