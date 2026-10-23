"""Fail-closed website gate bound to the measured implementation and pinned images."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FILES=('backend/adapters/web_capture.py','backend/adapters/web_report.py','workers/website.py',
       'workers/zap_runner.py','workers/launcher.py','rules/gitleaks.toml','backend/core/policy.py')


def implementation():
    digest=hashlib.sha256()
    for name in FILES:
        digest.update(name.encode()); digest.update((ROOT/name).read_bytes().replace(b'\r\n',b'\n'))
    return digest.hexdigest()


def ready():
    try:
        proof=json.loads((ROOT/'contracts/website-readiness.json').read_text())
        scanners=json.loads((ROOT/'contracts/scanner-readiness.json').read_text())['scanners']
        images={item['name']:item['digest'] for item in scanners if item['status']=='verified'}
        return (proof.get('ready') is True and proof.get('implementation')==implementation()
                and proof.get('zap_image')==images['zap'] and proof.get('gitleaks_image')==images['gitleaks']
                and proof.get('network_mode')=='none' and proof.get('private_control') is True)
    except (OSError,ValueError,KeyError,TypeError): return False
