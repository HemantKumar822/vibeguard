from scripts.scanner_readiness import probe
import os
from pathlib import Path
from types import SimpleNamespace
import subprocess


def test_missing_docker_is_a_blocking_result_without_invented_versions():
    result = probe(find_docker=lambda _: None)
    assert result['ready'] is False
    assert result['status'] == 'blocked'
    assert result['reason_code'] == 'docker_not_found'
    assert len(result['scanners']) == 3
    assert all(s['digest'] is None and s['observed_version'] is None for s in result['scanners'])


def test_new_install_makes_sibling_credential_helpers_available(monkeypatch):
    executable = str(Path('C:/Docker/bin/docker.exe'))
    def command(args, **kwargs):
        assert kwargs['env']['PATH'].split(os.pathsep)[0] == str(Path(executable).parent)
        return SimpleNamespace(returncode=0 if 'info' in args else 1, stdout='29.9.2')
    monkeypatch.setattr('scripts.scanner_readiness.subprocess.run', command)
    result = probe(find_docker=lambda _: executable)
    assert result['ready'] is False
    assert result['reason_code'] == 'scanner_probe_failed'


def test_one_pull_timeout_does_not_skip_other_scanners(monkeypatch):
    def command(args, **kwargs):
        if 'info' in args:
            return SimpleNamespace(returncode=0, stdout='29.9.2')
        if 'semgrep/semgrep:1.182.1' in args:
            raise subprocess.TimeoutExpired(args, 180)
        return SimpleNamespace(returncode=1, stdout='')
    monkeypatch.setattr('scripts.scanner_readiness.subprocess.run', command)
    result = probe(find_docker=lambda _: 'docker')
    assert result['scanners'][1]['status'] == 'timed_out'
    assert result['scanners'][2]['status'] == 'pull_failed'
