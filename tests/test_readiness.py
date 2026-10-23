from scripts.scanner_readiness import probe
import os
from pathlib import Path
from types import SimpleNamespace
import subprocess
import json


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
        if 'rm' in args:
            return SimpleNamespace(returncode=0, stdout='', stderr='')
        if 'info' in args:
            return SimpleNamespace(returncode=0, stdout='29.9.2')
        if 'semgrep/semgrep:1.182.1' in args:
            raise subprocess.TimeoutExpired(args, 180)
        return SimpleNamespace(returncode=1, stdout='')
    monkeypatch.setattr('scripts.scanner_readiness.subprocess.run', command)
    result = probe(find_docker=lambda _: 'docker')
    assert result['scanners'][1]['status'] == 'timed_out'
    assert result['scanners'][2]['status'] == 'pull_failed'


def test_version_probes_use_writable_scratch_home_without_weakening_isolation(monkeypatch):
    versions = {'gitleaks': '8.30.1', 'semgrep': '1.182.1', 'zap.sh': '2.17.0'}

    def command(args, **kwargs):
        if 'rm' in args:
            return SimpleNamespace(returncode=0, stdout='', stderr='')
        if 'info' in args:
            return SimpleNamespace(returncode=0, stdout='29.9.2')
        if 'pull' in args:
            raise AssertionError('Cached immutable images must not require a registry refresh')
        if 'inspect' in args:
            return SimpleNamespace(returncode=0, stdout=json.dumps(['example/tool@sha256:' + 'a' * 64]))
        assert args[args.index('--env') + 1] == 'HOME=/tmp'
        assert args[args.index('--network') + 1] == 'none'
        assert '--read-only' in args
        assert args[args.index('--user') + 1] == '1000:1000'
        assert args[args.index('--tmpfs') + 1] == '/tmp:rw,nosuid,nodev,size=256m'
        assert args[args.index('--hostname') + 1] == 'vibeguard-probe'
        assert args[args.index('--add-host') + 1] == 'vibeguard-probe:127.0.0.1'
        tool = args[args.index('--entrypoint') + 1]
        if tool == 'semgrep':
            assert '--disable-version-check' in args and '--metrics=off' in args
        if tool == 'zap.sh':
            assert 'JAVA_TOOL_OPTIONS=-Duser.home=/tmp' in args
            assert args[-3:] == ['-dir', '/tmp/zap', '-version']
        return SimpleNamespace(returncode=0, stdout=versions[tool], stderr='')

    monkeypatch.setattr('scripts.scanner_readiness.subprocess.run', command)
    result = probe(find_docker=lambda _: 'docker')
    assert result['ready'] is True
    assert all(s['status'] == 'verified' for s in result['scanners'])


def test_version_text_with_fatal_startup_errors_is_not_verified(monkeypatch):
    versions = {'gitleaks': '8.30.1', 'semgrep': '1.182.1', 'zap.sh': '2.17.0'}
    def command(args, **kwargs):
        if 'rm' in args:
            return SimpleNamespace(returncode=0, stdout='', stderr='')
        if 'info' in args:
            return SimpleNamespace(returncode=0, stdout='29.9.2')
        if 'inspect' in args:
            return SimpleNamespace(returncode=0, stdout=json.dumps(['example/tool@sha256:' + 'a' * 64]))
        if 'pull' in args:
            return SimpleNamespace(returncode=0, stdout='')
        tool = args[args.index('--entrypoint') + 1]
        return SimpleNamespace(returncode=0, stdout=versions[tool],
            stderr='java.io.IOException: No space left on device' if tool == 'zap.sh' else '')
    monkeypatch.setattr('scripts.scanner_readiness.subprocess.run', command)
    result = probe(find_docker=lambda _: 'docker')
    assert result['ready'] is False
    assert result['scanners'][2]['status'] == 'startup_failed'


def test_timed_out_containers_are_removed_by_their_unique_name(monkeypatch):
    started, removed = [], []
    def command(args, **kwargs):
        if 'info' in args:
            return SimpleNamespace(returncode=0, stdout='29.9.2')
        if 'inspect' in args:
            return SimpleNamespace(returncode=0, stdout=json.dumps(['example/tool@sha256:' + 'a' * 64]))
        if 'rm' in args:
            removed.append(args[-1])
            return SimpleNamespace(returncode=0, stdout='', stderr='')
        if 'run' in args:
            started.append(args[args.index('--name') + 1] if '--name' in args else 'unnamed')
            raise subprocess.TimeoutExpired(args, 90)
        raise AssertionError('Unexpected command')
    monkeypatch.setattr('scripts.scanner_readiness.subprocess.run', command)
    result = probe(find_docker=lambda _: 'docker')
    assert len(started) == 3 and len(set(started)) == 3 and started == removed
    assert all(s['status'] == 'timed_out' for s in result['scanners'])
