import json
import os
import uuid
from pathlib import Path
import pytest
from backend.api.main import queued_scan
from backend.adapters.web_capture import write_har
from backend.adapters.web_report import zap_findings
from backend.core.lifecycle import Lifecycle
from backend.core.cleanup import Cleanup
from workers.coordinator import run_once
from tests.support.runtime import runtime

from tests.support.scanners import FAKE, URL, observed


def zap_report(resources,alerts=None):
    return json.dumps({'mode':'offline-passive-har','version':'2.17.0','isolation_verified':True,
        'plugins':{'pscanrules-release-76.zap':'a'*64},'messages':len(resources),'expected':len(resources),
        'alerts':alerts if alerts is not None else [{'pluginId':'10038','url':URL,'risk':'Medium','confidence':'High','evidence':FAKE,'unknown':FAKE}]}).encode()


def test_zap_raw_evidence_never_crosses_boundary():
    findings,rulehash=zap_findings(zap_report([URL]),{URL:{'key':'web-0000','display':URL}})
    assert findings[0].rule_id=='10038' and len(rulehash)==64
    assert FAKE not in findings[0].model_dump_json()
    assert findings[0].location.kind=='web'


@pytest.mark.parametrize('raw',[b'{}',b'{broken',b'[]',b'{"error":"failed"}'])
def test_invalid_zap_output_not_clean(raw):
    with pytest.raises(ValueError): zap_findings(raw,{URL:{'key':'web-0000','display':URL}})


def test_website_gate_closed_without_measured_proof(runtime,monkeypatch):
    client,headers,store=runtime
    monkeypatch.setattr('backend.api.main.website_ready',lambda:False)
    assert 'website' not in client.get('/api/v1/capabilities').json()['permitted_modes']
    response=client.post('/api/v1/scans',headers=headers,json={'mode':'website','target_url':URL,'authorization_confirmed':True})
    assert response.status_code==503 and response.json()['error']['code']=='website_safety_unverified'
    assert not list(store.staging.iterdir())


@pytest.mark.parametrize('url',['http://127.0.0.1/','https://example.com:8443/','https://example.com/?token=synthetic'])
def test_website_api_rejects_invalid_target_before_admission(runtime,monkeypatch,url):
    client,headers,store=runtime
    monkeypatch.setattr('backend.api.main.website_ready',lambda:True)
    response=client.post('/api/v1/scans',headers=headers,json={'mode':'website','target_url':url,'authorization_confirmed':True})
    assert response.status_code==422 and not list(store.staging.iterdir())


def test_website_proof_drift_disables_admission(tmp_path,monkeypatch):
    from backend.core import website_readiness as gate
    root=tmp_path/'contracts';root.mkdir()
    monkeypatch.setattr(gate,'ROOT',tmp_path)
    monkeypatch.setattr(gate,'implementation',lambda:'a'*64)
    (root/'scanner-readiness.json').write_text(json.dumps({'scanners':[{'name':'zap','digest':'zap-image','status':'verified'},{'name':'gitleaks','digest':'gitleaks-image','status':'verified'}]}))
    proof={'ready':True,'implementation':'a'*64,'zap_image':'zap-image','gitleaks_image':'gitleaks-image','network_mode':'none','private_control':True}
    file=root/'website-readiness.json';file.write_text(json.dumps(proof))
    assert gate.ready()
    file.write_text(json.dumps({**proof,'implementation':'b'*64}))
    assert not gate.ready()
    file.unlink()
    assert not gate.ready()


def submit(runtime,monkeypatch):
    client,headers,store=runtime
    monkeypatch.setattr('backend.api.main.website_ready',lambda:True)
    response=client.post('/api/v1/scans',headers=headers,json={'mode':'website','target_url':URL,'authorization_confirmed':True})
    assert response.status_code==202,response.text
    return response.json()




class Scanner:
    images={'zap':'zap@sha256:'+'a'*64,'gitleaks':'gitleaks@sha256:'+'b'*64}
    versions={'zap':'2.17.0','gitleaks':'8.30.1'}
    def website_available(self): pass
    def scan(self,name,source,scan_id,active,timeout):
        assert active()
        if name=='zap': return zap_report([URL])
        return json.dumps([{'RuleID':'vg-secret-assignment','File':'asset-0000.txt','StartLine':1,'Secret':FAKE}]).encode()


def test_api_website_report_assets_prompt_and_cleanup(runtime,monkeypatch):
    from workers import website
    client,headers,store=runtime
    scan=submit(runtime,monkeypatch)
    assert {tool['name'] for tool in scan['tools'] if tool['required']}=={'zap','asset_secrets'}
    assert scan['input']['target_redacted']==URL and scan['input']['observation_id']==scan['scan_id']
    # Default capture is substituted only in this test, never through a public runtime option.
    execute=website.execute
    monkeypatch.setattr(website,'execute',lambda *args:execute(*args,capture_fn=observed))
    run_once(Lifecycle(store),Cleanup(store,lambda _:None),'test',Scanner())
    report=client.get('/api/v1/scans/'+scan['scan_id']).json()
    assert report['status']=='complete' and report['coverage']['completed_count']==2
    assert {item['scanner'] for item in report['findings']}=={'zap','asset_secrets'}
    assert all(item['location']['kind']=='web' and item['location']['url_redacted']==URL for item in report['findings'])
    assert 'rotate' in report['repair']['prompt_redacted'] and FAKE not in json.dumps(report)
    assert not (store.staging/scan['scan_id']).exists()


def test_broken_zap_retains_asset_evidence_as_partial(runtime,monkeypatch):
    from workers.website import execute
    client,headers,store=runtime
    scan=submit(runtime,monkeypatch)
    lifecycle=Lifecycle(store); lifecycle.lease('test'); claimed=lifecycle.claim('test')
    class Broken(Scanner):
        def scan(self,name,*args,**kwargs):
            return b'broken' if name=='zap' else super().scan(name,*args,**kwargs)
    execute(claimed,lifecycle,Broken(),'test',capture_fn=observed)
    report=client.get('/api/v1/scans/'+scan['scan_id']).json()
    assert report['status']=='partial' and report['coverage']['completed_count']==1
    assert report['tools'][2]['status']=='failed'
    assert any(item['scanner']=='asset_secrets' for item in report['findings'])


@pytest.mark.skipif(os.environ.get('VIBEGUARD_DOCKER_TESTS')!='1',reason='Requires real network-disabled pinned ZAP and Gitleaks')
def test_real_passive_zap_isolation_and_visible_asset_controls(tmp_path):
    from workers.launcher import Launcher
    from backend.adapters.source import normalize
    from backend.adapters.web_report import asset_findings
    capture=tmp_path/'capture';capture.mkdir()
    records=observed(URL,lambda:True)['entries']
    corrected=URL+'corrected'
    records.append({'url':corrected,'status':200,'body':b'<!doctype html><html><body>Corrected control</body></html>','mime':'text/html',
        'headers':[('Content-Type','text/html'),('X-Content-Type-Options','nosniff'),('X-Frame-Options','DENY'),
                   ('Content-Security-Policy',"default-src 'none'; frame-ancestors 'none'; base-uri 'none'"),
                   ('Strict-Transport-Security','max-age=31536000; includeSubDomains'),('Cache-Control','no-store')]})
    write_har(records,capture/'capture.har')
    launcher=Launcher(); scan_id=uuid.uuid4().hex
    raw=launcher.scan('zap',capture,scan_id,timeout=180)
    envelope=json.loads(raw)
    assert envelope['isolation_verified'] is True
    findings,_=zap_findings(raw,{URL:{'key':'web-0000','display':URL},corrected:{'key':'web-0001','display':corrected}})
    assert {'10038','10020','10021'}<={finding.rule_id for finding in findings}
    assert not any(finding.location.url_redacted==corrected and finding.rule_id in {'10038','10020','10021','10035'} for finding in findings)
    assets=tmp_path/'assets';assets.mkdir()
    (assets/'visible.txt').write_text(f'const password = "{FAKE}";\nconst publicBrowserKey = "AIzaSyntheticBrowserKey_123456789";')
    secret_raw=launcher.scan('asset_secrets',assets,scan_id,timeout=30)
    candidates,_=normalize('gitleaks',secret_raw,assets)
    mapped=asset_findings(candidates,{'visible.txt':{'key':'web-0000','display':URL}})
    assert len(mapped)==1 and mapped[0].location.line_start==1
    assert mapped[0].scanner=='asset_secrets' and FAKE not in mapped[0].model_dump_json()
    for tool in ('zap','asset_secrets'):
        import subprocess
        inspected=subprocess.run([launcher.docker,'container','inspect',f'vg-{scan_id}-{tool}'],capture_output=True,text=True)
        assert inspected.returncode!=0 and 'No such' in inspected.stderr
