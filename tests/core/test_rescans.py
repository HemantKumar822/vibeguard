import json
import os
from fastapi.testclient import TestClient
import pytest
from backend.core.lifecycle import Lifecycle
from backend.core.cleanup import Cleanup
from workers.coordinator import run_once
from tests.support.runtime import runtime, upload
from tests.support.scanners import StubScanner


def repeat(client,headers,baseline,data=b'const safe = 1'):
    metadata={'mode':'codebase','authorization_confirmed':True,'files':[{'part_id':'f','relative_path':'app/src/main.ts'}]}
    return client.post(f'/api/v1/scans/{baseline}/rescans',headers=headers,files=[('metadata',(None,json.dumps(metadata))),('f',('ignored',data))])


def finish(runtime,scanner=None):
    client,headers,store=runtime
    return run_once(Lifecycle(store),Cleanup(store,lambda _:None),'repeat-test',scanner or StubScanner())


def test_real_new_job_replay_and_immutable_baseline(runtime):
    client,headers,store=runtime
    baseline=upload(client,headers).json();finish(runtime)
    before=client.get('/api/v1/scans/'+baseline['scan_id']).json()
    headers={**headers,'Idempotency-Key':'repeat'}
    new=repeat(client,headers,baseline['scan_id'])
    assert new.status_code==202,new.text
    scan=new.json()
    assert scan['scan_id']!=baseline['scan_id'] and scan['baseline_id']==baseline['scan_id']
    assert scan['status']=='queued' and not scan['findings']
    assert repeat(client,headers,baseline['scan_id']).json()['scan_id']==scan['scan_id']
    assert repeat(client,headers,baseline['scan_id'],b'changed').status_code==409
    finish(runtime)
    assert client.get('/api/v1/scans/'+baseline['scan_id']).json()==before
    response=client.get(f"/api/v1/scans/{baseline['scan_id']}/comparisons/{scan['scan_id']}")
    assert response.status_code==200
    assert response.json()['human_actions']


def test_repeat_inaccessible_nonterminal_mode_and_csrf(runtime):
    client,headers,store=runtime
    baseline=upload(client,headers).json();bid=baseline['scan_id']
    assert repeat(client,{**headers,'Idempotency-Key':'repeat'},bid).status_code==409
    finish(runtime)
    assert repeat(TestClient(client.app),headers,bid).status_code in {403,404}
    assert repeat(client,{**headers,'X-CSRF-Token':'bad'},bid).status_code==403
    response=client.post(f'/api/v1/scans/{bid}/rescans',headers={**headers,'Idempotency-Key':'wrong-mode'},json={'mode':'repository','repository_url':'https://github.com/team/project','authorization_confirmed':True})
    assert response.status_code==409
    client.delete('/api/v1/scans/'+bid,headers=headers)
    assert repeat(client,{**headers,'Idempotency-Key':'deleted'},bid).status_code==404


def test_deleted_between_intake_and_admission_is_fenced(runtime,monkeypatch):
    import backend.api.main as main
    client,headers,store=runtime
    baseline=upload(client,headers).json();finish(runtime);bid=baseline['scan_id']
    original=main.receive
    async def deleting(request,directory):
        result=await original(request,directory)
        Cleanup(store).delete(bid,client.cookies.get('vibeguard_session'))
        return result
    monkeypatch.setattr(main,'receive',deleting)
    response=repeat(client,{**headers,'Idempotency-Key':'race'},bid)
    assert response.status_code==404
    with store.connect() as db: assert db.execute('SELECT COUNT(*) FROM scans').fetchone()[0]==1


def test_baseline_actions_survive_expiry_during_repeat(runtime):
    import time
    client,headers,store=runtime
    baseline=upload(client,headers).json();finish(runtime)
    before=client.get('/api/v1/scans/'+baseline['scan_id']).json()
    assert before['repair']['human_actions']
    response=repeat(client,{**headers,'Idempotency-Key':'inherited-actions'},baseline['scan_id'])
    assert response.status_code==202
    with store.connect() as db:
        db.execute('UPDATE scans SET finished=? WHERE id=?',(time.time()-86401,baseline['scan_id']))
    finish(runtime)
    after=client.get('/api/v1/scans/'+response.json()['scan_id']).json()
    for action in before['repair']['human_actions']:
        assert action in after['repair']['human_actions']
        assert action in after['repair']['prompt_redacted']


@pytest.mark.skipif(os.environ.get('VIBEGUARD_DOCKER_TESTS')!='1',reason='Opt in to actual pinned scanner repeat smoke')
@pytest.mark.parametrize('mode',['codebase','repository','website'])
def test_actual_worker_repeat_smoke(runtime,monkeypatch,mode):
    """Real scanner launches; repository retrieval and web capture use labeled controlled fixtures."""
    from workers.launcher import Launcher
    from workers import website
    from tests.support.scanners import URL, observed
    from backend.adapters.repository import request_digest
    client,headers,store=runtime
    launcher=Launcher()
    clean=False
    if mode=='repository':
        def retrieve(metadata,directory):
            data=b'const safe = JSON.parse(input);' if clean else b'eval(req.query.code);'
            (directory/'f').write_bytes(data)
            (directory/'manifest.json').write_text(json.dumps({'files':[{'part_id':'f','relative_path':'app/src/main.ts'}]}))
            return ['app/src/main.ts'],[],'https://github.com/fixture/repeat','main',('b' if clean else 'a')*40
        monkeypatch.setattr('backend.api.main.retrieve',retrieve)
    if mode=='website':
        monkeypatch.setattr('backend.api.main.website_ready',lambda:True)
        execute=website.execute
        def capture(url,active):
            result=observed(url,active)
            if clean:
                result['entries'][0]['body']=b'<!doctype html><html><body>Corrected fixture</body></html>'
                result['entries'][0]['headers'] += [('X-Content-Type-Options','nosniff'),('X-Frame-Options','DENY'),('Content-Security-Policy',"default-src 'none'; frame-ancestors 'none'; base-uri 'none'"),('Strict-Transport-Security','max-age=31536000'),('Cache-Control','no-store')]
            return result
        monkeypatch.setattr(website,'execute',lambda *args:execute(*args,capture_fn=capture))
    def submit(baseline=None):
        url='/api/v1/scans'+(f'/{baseline}/rescans' if baseline else '')
        if mode=='codebase':
            if baseline: return repeat(client,headers,baseline,b'const safe = JSON.parse(input);')
            return upload(client,headers,data=b'eval(req.query.code);')
        body={'mode':mode,'authorization_confirmed':True}
        body.update({'repository_url':'https://github.com/fixture/repeat'} if mode=='repository' else {'target_url':URL})
        return client.post(url,headers=headers,json=body)
    first=submit();assert first.status_code==202,first.text
    finish(runtime,launcher)
    baseline=client.get('/api/v1/scans/'+first.json()['scan_id']).json()
    assert baseline['status']=='complete',baseline
    assert baseline['findings']
    clean=True;headers['Idempotency-Key']='actual-repeat'
    second=submit(baseline['scan_id']);assert second.status_code==202,second.text
    finish(runtime,launcher)
    after=client.get('/api/v1/scans/'+second.json()['scan_id']).json()
    assert after['status']=='complete',after
    result=client.get(f"/api/v1/scans/{baseline['scan_id']}/comparisons/{after['scan_id']}")
    assert result.status_code==200,result.text
    assert any(item['status']=='not_detected' for item in result.json()['items'])
    assert client.get('/api/v1/scans/'+baseline['scan_id']).json()==baseline
