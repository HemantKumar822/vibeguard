"""Probe tools honestly; a version probe does not establish scan containment."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

TOOLS = [
    ('gitleaks', 'ghcr.io/gitleaks/gitleaks:v8.30.1', '8.30.1', 'gitleaks', ['version']),
    ('semgrep', 'semgrep/semgrep:1.182.1', '1.182.1', 'semgrep', ['--disable-version-check', '--metrics=off', '--version']),
    ('zap', 'ghcr.io/zaproxy/zaproxy:2.17.0', '2.17.0', 'zap.sh', ['-dir', '/tmp/zap', '-version']),
]


def locate_docker(name):
    found = shutil.which(name)
    if found:
        return found
    # Newly installed Windows applications may not be in this process's PATH.
    installed = Path(os.environ.get('ProgramFiles', 'C:/Program Files'))/'Docker/Docker/resources/bin/docker.exe'
    return str(installed) if os.name == 'nt' and installed.is_file() else None


def probe(find_docker=locate_docker, pull_timeout=180):
    result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'ready': False,
              'status': 'blocked', 'reason_code': 'docker_not_found',
              'containment_verified': False,
              'scanners': [{'name': n, 'requested_image': image, 'expected_version': version,
                            'digest': None, 'observed_version': None, 'status': 'not_checked'}
                           for n, image, version, _, _ in TOOLS]}
    docker = find_docker('docker')
    if not docker:
        return result
    environment = os.environ.copy()
    environment['PATH'] = str(Path(docker).parent) + os.pathsep + environment.get('PATH', '')
    result['reason_code'] = 'docker_engine_unavailable'
    try:
        engine = subprocess.run([docker, 'info', '--format', '{{.ServerVersion}}'], capture_output=True, text=True, timeout=20, env=environment)
        if engine.returncode:
            return result
        result['engine_version'] = engine.stdout.strip()
        for scanner, (_, image, version, command, args) in zip(result['scanners'], TOOLS):
            try:
                inspected = subprocess.run([docker, 'image', 'inspect', image, '--format', '{{json .RepoDigests}}'], capture_output=True, text=True, timeout=20, env=environment)
                if inspected.returncode:
                    scanner['status'] = 'pull_failed'
                    pulled = subprocess.run([docker, 'pull', image], capture_output=True, timeout=pull_timeout, env=environment)
                    if pulled.returncode:
                        continue
                    inspected = subprocess.run([docker, 'image', 'inspect', image, '--format', '{{json .RepoDigests}}'], capture_output=True, text=True, timeout=20, env=environment)
                digests = json.loads(inspected.stdout) if inspected.returncode == 0 else []
                if not digests or not re.fullmatch(r'[^\s]+@sha256:[a-f0-9]{64}', digests[0]):
                    scanner['status'] = 'digest_unavailable'
                    continue
                scanner['digest'] = digests[0]
                tool_env = ['--env', 'HOME=/tmp']
                if command == 'semgrep':
                    tool_env += ['--env', 'SEMGREP_ENABLE_VERSION_CHECK=0', '--env', 'SEMGREP_SEND_METRICS=off']
                elif command == 'zap.sh':
                    tool_env += ['--env', 'JAVA_TOOL_OPTIONS=-Duser.home=/tmp']
                checked = subprocess.run([docker, 'run', '--rm', '--network', 'none', '--read-only',
                    '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '1000:1000',
                    '--memory', '2g', '--cpus', '2', '--pids-limit', '128',
                    '--tmpfs', '/tmp:rw,nosuid,nodev,size=256m', '--hostname', 'vibeguard-probe',
                    '--add-host', 'vibeguard-probe:127.0.0.1', *tool_env, '--entrypoint', command,
                    digests[0], *args], capture_output=True, text=True, timeout=90, env=environment)
                output = checked.stdout + '\n' + checked.stderr
                observed = re.search(r'(?<!\d)' + re.escape(version) + r'(?![\d.])', output)
                scanner['observed_version'] = version if observed else None
                fatal_startup = re.search(r'No space left on device|Read-only file system|The home path is not writable|java\.io\.IOException|Traceback \(most recent call last\)', output)
                scanner['status'] = 'startup_failed' if fatal_startup else ('verified' if checked.returncode == 0 and observed else 'version_probe_failed')
            except subprocess.TimeoutExpired:
                scanner['status'] = 'timed_out'
            except (OSError, ValueError):
                scanner['status'] = 'probe_failed'
        result['ready'] = all(s['status'] == 'verified' for s in result['scanners'])
        result['status'] = 'tools_verified' if result['ready'] else 'blocked'
        result['reason_code'] = 'version_probes_only' if result['ready'] else 'scanner_probe_failed'
    except (subprocess.TimeoutExpired, OSError, ValueError):
        result['reason_code'] = 'probe_failed_or_timed_out'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--pull-timeout', type=int, default=180, choices=range(1, 601), metavar='1..600')
    args = parser.parse_args()
    result = probe(pull_timeout=args.pull_timeout)
    content = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding='utf-8')
    print(content)
    raise SystemExit(0 if result['ready'] else 1)
