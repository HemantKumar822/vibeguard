"""Source boundary and integration checks; all credentials are synthetic controls."""
import json
import os
import uuid
from pathlib import Path
import pytest
from backend.adapters.source import normalize, fingerprint
from backend.core.lifecycle import Lifecycle
from backend.core.cleanup import Cleanup
from workers.coordinator import run_once
from workers.source import execute
from test_intake import runtime, upload

FAKE='SyntheticCredential_1234567890'


def leak(path='app/src/main.ts',line=1):
    return {'RuleID':'vg-secret-assignment','File':path,'StartLine':line,
            'Secret':FAKE,'Match':FAKE,'Unknown':{'nested':FAKE}}


def test_vendor_fields_never_cross_boundary(tmp_path):
    (tmp_path/'test.ts').write_text(f'const password = "{FAKE}"')
    findings,_=normalize('gitleaks',json.dumps([leak('test.ts')]),tmp_path)
    assert FAKE not in findings[0].model_dump_json()
    assert findings[0].location.line_start==1
    assert 'rotate' in findings[0].human_actions[0]
    assert len(fingerprint())==64


@pytest.mark.parametrize('report', ['invalid','{}','null',json.dumps([leak('../escape.ts')]),
    json.dumps([leak('/etc/passwd')]),json.dumps([leak('test.ts',0)]),json.dumps([leak('test.ts',99)])])
def test_bad_reports_are_execution_failures(tmp_path,report):
    (tmp_path/'test.ts').write_text('const x=1')
    with pytest.raises(ValueError): normalize('gitleaks',report,tmp_path)


def test_semgrep_errors_cannot_be_clean(tmp_path):
    with pytest.raises(ValueError): normalize('semgrep',json.dumps({'results':[],'errors':[{'message':FAKE}],'paths':{'scanned':[]}}),tmp_path)


def test_prompt_overflow_is_explicitly_partial():
    from backend.core.contracts import Scan
    from backend.core.repair import repair_for
    scan=Scan.model_validate(json.loads(Path('fixtures/contracts/source-baseline.json').read_text())['data'])
    scan.findings[0].explanation='Synthetic bounded control. '*6000
    result=repair_for(scan)
    assert len(result.prompt_redacted.encode())<=128*1024
    assert scan.status=='partial' and not scan.coverage.scope_complete
    assert any('prompt exceeded' in warning for warning in scan.warnings)


class StubScanner:
    versions={'gitleaks':'8.30.1','semgrep':'1.182.1'}
    def scan(self,tool,source,scan_id,active):
        assert active()
        if tool=='gitleaks': return json.dumps([leak()]).encode()
        return json.dumps({'results':[],'errors':[],'paths':{'scanned':['/source/app/src/main.ts']}}).encode()


def test_coordinator_commits_masked_report_and_cleans_source(runtime):
    client,headers,store=runtime
    scan=upload(client,headers,data=f'const password = "{FAKE}"'.encode()).json()
    stopped=[]
    run_once(Lifecycle(store),Cleanup(store,stopped.append),'test',StubScanner())
    report=client.get('/api/v1/scans/'+scan['scan_id']).json()
    assert report['status']=='complete'
    assert report['coverage']['completed_count']==2
    assert report['findings'][0]['location']['path']=='app/src/main.ts'
    assert 'rotate' in report['repair']['prompt_redacted']
    assert FAKE not in json.dumps(report)
    assert not (store.staging/scan['scan_id']).exists()


@pytest.mark.parametrize('failure',[TimeoutError,ValueError])
def test_partial_coverage_survives_tool_failure(runtime,failure):
    client,headers,store=runtime
    scan=upload(client,headers).json()
    class Broken(StubScanner):
        def scan(self,tool,*args,**kwargs):
            if tool=='semgrep': raise failure('Raw failure must not escape '+FAKE)
            return super().scan(tool,*args,**kwargs)
    run_once(Lifecycle(store),Cleanup(store,lambda _:None),'test',Broken())
    report=client.get('/api/v1/scans/'+scan['scan_id']).json()
    assert report['status']=='partial' and report['coverage']['completed_count']==1
    assert FAKE not in json.dumps(report)
    assert report['tools'][1]['status']==('timed_out' if failure is TimeoutError else 'failed')


def test_deletion_fences_late_results(runtime):
    client,headers,store=runtime
    scan=upload(client,headers).json()
    lifecycle=Lifecycle(store); lifecycle.lease('token'); claimed=lifecycle.claim('token')
    class Deleted(StubScanner):
        def scan(self,*args,**kwargs):
            Cleanup(store).delete(scan['scan_id'],client.cookies.get('vibeguard_session'))
            return b'[]'
    with pytest.raises(RuntimeError,match='job_cancelled'):
        execute(claimed,lifecycle,Deleted(),'token')
    assert client.get('/api/v1/scans/'+scan['scan_id']).status_code==404


@pytest.mark.skipif(os.environ.get('VIBEGUARD_DOCKER_TESTS')!='1',reason='Opt in to real scanner batch acceptance')
def test_real_scanners_categories_controls_and_suppressions(tmp_path):
    from workers.launcher import Launcher
    source=tmp_path/'source'; source.mkdir()
    content='\n'.join([f'const password = "{FAKE}"; // gitleaks:allow',
        'eval(req.query.code); // nosemgrep',
        'const options = { rejectUnauthorized: false };',
        'app.get("/admin", (req, res) => { res.send("admin"); });',
        'app.get("/protected", requireAuth, (req,res) => { res.send("ok"); });',
        'const publicBrowserKey = "AIzaSyntheticPublicBrowserKey_123456789";'])
    (source/'sample.ts').write_text(content)
    (source/'clean.ts').write_text('const safe = JSON.parse(input);\napp.get("/ok", requireAuth, (req,res)=>{res.send("ok")});')
    (source/'.gitignore').write_text('sample.ts\n')
    launcher=Launcher(); scan_id=uuid.uuid4().hex
    observed=[]
    for tool in ('gitleaks','semgrep'):
        raw=launcher.scan(tool,source,scan_id)
        findings,_=normalize(tool,raw,source)
        observed.extend(findings)
    by_rule={finding.rule_id:finding for finding in observed}
    assert {'vg-secret-assignment','vg-unsafe-eval','vg-tls-disabled','vg-access-candidate'}<=by_rule.keys()
    assert {finding.location.path for finding in observed}=={'sample.ts'}
    assert by_rule['vg-secret-assignment'].location.line_start==1
    assert by_rule['vg-unsafe-eval'].location.line_start==2
    assert by_rule['vg-tls-disabled'].location.line_start==3
    assert by_rule['vg-access-candidate'].location.line_start==4
    assert by_rule['vg-access-candidate'].confidence=='needs_review'
    assert FAKE not in json.dumps([finding.model_dump(mode='json') for finding in observed])
