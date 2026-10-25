"""Measure a real authorized capture, isolated ZAP and asset review before enabling URL admission."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import secrets
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from backend.api.main import queued_scan
from backend.adapters.web_capture import target,display
from backend.adapters.storage import Storage
from backend.core.settings import Settings
from backend.core.lifecycle import Lifecycle
from backend.core.cleanup import Cleanup
from backend.core.website_readiness import implementation
from workers.launcher import Launcher
from workers.coordinator import run_once


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',required=True)
    parser.add_argument('--authorization-confirmed',action='store_true',required=True)
    args=parser.parse_args()
    url=target(args.target)
    output=ROOT/'contracts/website-readiness.json'
    proof={'ready':False,'checked_at':datetime.now(timezone.utc).isoformat(),
           'implementation':implementation(),'network_mode':'none','private_control':True}
    output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    launcher=Launcher()
    with tempfile.TemporaryDirectory(prefix='vibeguard-website-proof-') as temporary:
        store=Storage(Settings(Path(temporary)/'runtime',loopback_http=True).validate())
        owner,_=store.new_session(); scan_id=secrets.token_hex(16)
        directory=store.staging/scan_id;directory.mkdir()
        (directory/'website.json').write_text(json.dumps({'target_url':url}),encoding='utf-8')
        scan=queued_scan(scan_id,[],[],mode='website')
        scan.input.target_redacted=display(url);scan.input.observation_id=scan_id;scan.input.display_name='Authorized website readiness check'
        lifecycle=Lifecycle(store);lifecycle.admit(scan,owner,'readiness','readiness',False)
        run_once(lifecycle,Cleanup(store,launcher.stop),'readiness',launcher)
        result=lifecycle.read(scan_id,owner)
        tools=[tool for tool in result.tools if tool.required]
        proof.update({'ready':all(tool.status=='complete' for tool in tools) and bool(result.coverage.inspected),
            'zap_image':launcher.images['zap'],'gitleaks_image':launcher.images['gitleaks'],
            'target_redacted':display(url),'scan_status':result.status,'observed_resources':len(result.coverage.inspected),
            'findings':len(result.findings),'tool_states':{tool.name:tool.status for tool in tools},
            'source_removed':not directory.exists(),
            'scope':'Connection-pinned bounded GET capture; offline passive ZAP and Gitleaks, never browser/active scanning.'})
        if not proof['source_removed']: proof['ready']=False
    output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(proof),flush=True)
    return 0 if proof['ready'] else 1


if __name__=='__main__': raise SystemExit(main())
