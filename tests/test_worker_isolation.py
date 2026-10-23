"""Physical Linux Docker checks. Opt in with VIBEGUARD_DOCKER_TESTS=1."""
import json
import os
import subprocess
import uuid
import pytest
from workers.launcher import Launcher

LIVE = os.environ.get('VIBEGUARD_DOCKER_TESTS') == '1'


def diagnostic_command(launcher, source, scan_id, script):
    command=launcher.command('semgrep',source,f'vg-{scan_id}-semgrep')
    image=command.index(launcher.images['semgrep'])
    return command[:image]+['--entrypoint=python3',command[image],'-c',script]


@pytest.mark.skipif(not LIVE, reason='Requires local Linux Docker engine; explicitly enable integration checks')
def test_physical_isolation(tmp_path):
    launcher=Launcher(); scan_id=uuid.uuid4().hex
    (tmp_path/'source.ts').write_text('const example = 1')
    script='''
import os,socket,pathlib,json
assert os.getuid()!=0
for path in ('/source/forbidden','/forbidden'):
    try: pathlib.Path(path).write_text('x')
    except OSError: pass
    else: raise AssertionError('Writable restricted mount')
assert not pathlib.Path('/var/run/docker.sock').exists()
assert not any('SECRET' in key or key in {'DOCKER_HOST','AWS_ACCESS_KEY_ID'} for key in os.environ)
status=pathlib.Path('/proc/self/status').read_text()
assert 'NoNewPrivs:\\t1' in status
assert 'CapEff:\\t0000000000000000' in status
cg=pathlib.Path('/sys/fs/cgroup')
assert (cg/'memory.max').read_text().strip()=='2147483648'
assert (cg/'pids.max').read_text().strip()=='128'
quota,period=map(int,(cg/'cpu.max').read_text().split()); assert quota/period==2
fs=os.statvfs('/tmp'); assert fs.f_blocks*fs.f_frsize<=268435456
sock=socket.socket(); sock.settimeout(1)
try: sock.connect(('1.1.1.1',443))
except OSError: pass
else: raise AssertionError('External networking available')
assert pathlib.Path('/source/source.ts').read_text()=='const example = 1'
print('Physical isolation verified')
'''
    try:
        result=subprocess.run(diagnostic_command(launcher,tmp_path,scan_id,script),capture_output=True,text=True,timeout=30)
        assert result.returncode==0, result.stderr
    finally: launcher.stop(scan_id)
    inspected=subprocess.run([launcher.docker,'container','inspect',f'vg-{scan_id}-semgrep'],capture_output=True,text=True)
    assert inspected.returncode != 0 and 'No such' in inspected.stderr


@pytest.mark.skipif(not LIVE, reason='Requires local Linux Docker engine')
@pytest.mark.parametrize('script,timeout', [('import time;time.sleep(120)',.5), ('import sys;sys.stdout.write("x"*(6*1024*1024));sys.stdout.flush()',90)])
def test_physical_timeout_output_stop_and_cleanup(tmp_path, script, timeout):
    class Diagnostic(Launcher):
        def command(self, tool, source, name):
            command=super().command(tool,source,name)
            image=command.index(self.images[tool])
            return command[:image]+['--entrypoint=python3',command[image],'-c',script]
    launcher=Diagnostic(); scan_id=uuid.uuid4().hex
    with pytest.raises(RuntimeError): launcher.probe('semgrep',tmp_path,scan_id,timeout=timeout)
    result=subprocess.run([launcher.docker,'container','inspect',f'vg-{scan_id}-semgrep'],capture_output=True,text=True)
    assert result.returncode != 0 and 'No such' in result.stderr


def test_api_does_not_import_launcher():
    import ast
    from pathlib import Path
    for path in Path('backend').rglob('*.py'):
        tree=ast.parse(path.read_text())
        assert not any(isinstance(node,ast.ImportFrom) and (node.module or '').startswith('workers') for node in ast.walk(tree))
