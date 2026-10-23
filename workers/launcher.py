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
        self.versions={s['name']:s['observed_version'] for s in evidence['scanners'] if s['status']=='verified'}

    def command(self, tool, source, name, scanning=False):
        if tool not in {'gitleaks','semgrep'} or not re.fullmatch(r'vg-[a-f0-9]{32}-(gitleaks|semgrep)',name):
            raise ValueError('Unapproved worker')
        image=self.images[tool]
        if not re.fullmatch(r'[a-z0-9./-]+@sha256:[a-f0-9]{64}',image): raise ValueError('Unpinned image')
        # Version probes are diagnostic only; never translate them into scan coverage.
        args=['version'] if tool=='gitleaks' else ['semgrep','--version']
        mounts=[]
        if scanning:
            from backend.adapters.source import RULES
            mounts=['--mount',f'type=bind,src={RULES.resolve()},dst=/rules,readonly','--workdir=/tmp']
            args=(['dir','/source','--config=/rules/gitleaks.toml','--gitleaks-ignore-path=/rules/empty.ignore',
                   '--ignore-gitleaks-allow','--redact=100','--report-format=json','--report-path=/dev/stdout','--no-banner','--exit-code=1']
                  if tool=='gitleaks' else ['semgrep','scan','--config=/rules/semgrep.json','--json','--quiet',
                  '--disable-nosem','--no-git-ignore','--x-ignore-semgrepignore-files','--no-rewrite-rule-ids','--metrics=off',
                  '--disable-version-check','--error','--max-target-bytes=2097152','/source'])
        return [self.docker,'run','--name',name,'--label','vibeguard.worker=1','--pull=never','--read-only','--network=none','--user=65532:65532','--cap-drop=ALL','--security-opt=no-new-privileges','--cpus=2','--memory=2g','--memory-swap=2g','--pids-limit=128','--tmpfs=/tmp:rw,noexec,nosuid,size=268435456','--log-driver=none','--env=HOME=/tmp','--env=SEMGREP_ENABLE_VERSION_CHECK=0','--env=SEMGREP_SEND_METRICS=off','--mount',f'type=bind,src={Path(source).resolve()},dst=/source,readonly',*mounts,image,*args]

    def scan(self, tool, source, scan_id, active=lambda: True, timeout=90):
        """Bound stdout+stderr in memory; vendor text never reaches logs or disk."""
        process=None
        buffers=[bytearray(),bytearray()]
        exceeded=threading.Event()
        lock=threading.Lock()
        total=0
        def drain(stream, target):
            nonlocal total
            while chunk := stream.read(65536):
                with lock:
                    total += len(chunk)
                    if total > 5*1024*1024:
                        exceeded.set(); return
                    target.extend(chunk)
        try:
            process=subprocess.Popen(self.command(tool,source,f'vg-{scan_id}-{tool}',scanning=True),
                                     stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            readers=[threading.Thread(target=drain,args=(stream,buffers[index]),daemon=True)
                     for index,stream in enumerate((process.stdout,process.stderr))]
            for reader in readers: reader.start()
            deadline=time.monotonic()+min(timeout,90)
            next_check=0
            while process.poll() is None:
                if exceeded.is_set(): raise RuntimeError('output_limit')
                if time.monotonic()>=deadline: raise TimeoutError('tool_timeout')
                if time.monotonic()>=next_check:
                    if not active(): raise RuntimeError('job_cancelled')
                    next_check=time.monotonic()+.5
                time.sleep(.02)
            for reader in readers: reader.join(timeout=2)
            if exceeded.is_set() or any(reader.is_alive() for reader in readers): raise RuntimeError('output_limit')
            if process.returncode not in {0,1}: raise RuntimeError('tool_failed')
            if process.returncode==1:
                payload=json.loads(buffers[0])
                matches=payload if tool=='gitleaks' else payload.get('results')
                if not isinstance(matches,list) or not matches: raise RuntimeError('inconsistent_findings_exit')
            return bytes(buffers[0])
        finally:
            try: self.stop(scan_id)
            finally:
                if process is not None:
                    if process.poll() is None: process.kill()
                    process.wait(timeout=10)
                    if process.stdout: process.stdout.close()
                    if process.stderr: process.stderr.close()

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
