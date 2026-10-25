import os
import time
from fastapi.testclient import TestClient
from backend.core.cleanup import Cleanup
from backend.core.lifecycle import Lifecycle
from tests.support.runtime import runtime, upload


def test_tombstone_foreign_csrf_cleanup_retry_late_result(runtime):
    client, headers, store = runtime
    scan = upload(client,headers).json(); path='/api/v1/scans/'+scan['scan_id']
    core=Lifecycle(store); core.lease('worker'); core.claim('worker')
    assert client.delete(path).status_code == 403
    assert TestClient(client.app).delete(path,headers=headers).status_code == 404
    response=client.delete(path,headers=headers)
    assert response.status_code == 202
    operation=response.json()['operation_id']; op='/api/v1/deletions/'+operation
    assert client.get(path).status_code == 404
    assert TestClient(client.app).get(op).status_code == 404
    assert not core.unavailable(scan['scan_id'],'worker')
    def broken(_): raise RuntimeError('private daemon error')
    Cleanup(store,broken).sweep()
    assert client.get(op).json()['status'] == 'failed'
    assert 'private daemon' not in client.get(op).text
    assert upload(client,{**headers,'Idempotency-Key':'blocked'}).status_code == 503
    stopped=[]; Cleanup(store,stopped.append).sweep()
    assert scan['scan_id'] in stopped
    assert client.get(op).json()['status'] == 'complete'
    assert not (store.staging/scan['scan_id']).exists()
    assert client.get(path).status_code == 404


def test_report_and_session_expiry_and_abandoned_staging(runtime):
    client,headers,store=runtime
    scan=upload(client,headers).json(); core=Lifecycle(store)
    core.lease('worker'); core.claim('worker'); core.unavailable(scan['scan_id'],'worker')
    with store.connect() as db:
        db.execute('UPDATE scans SET finished=?',(time.time()-86401,))
    assert client.get('/api/v1/scans/'+scan['scan_id']).status_code == 404
    assert upload(client,headers).status_code == 404
    orphan=store.staging/'abandoned'; orphan.mkdir(); (orphan/'raw').write_text('private')
    os.utime(orphan,(time.time()-601,time.time()-601))
    Cleanup(store,lambda _: None).sweep()
    assert not orphan.exists() and not (store.staging/scan['scan_id']).exists()
    with store.connect() as db:
        db.execute('UPDATE sessions SET touched=?',(time.time()-86401,))
    assert client.get('/api/v1/scans/'+scan['scan_id']).status_code == 404



def test_api_sweep_expires_queue_without_coordinator(runtime):
    client,headers,store=runtime
    scan=upload(client,headers).json()
    with store.connect() as db:
        db.execute('UPDATE scans SET created=?',(time.time()-601,))
    Cleanup(store).sweep()
    result=client.get('/api/v1/scans/'+scan['scan_id']).json()
    assert result['status']=='failed'
    assert result['error']['code']=='deadline_exceeded'


def test_cleaned_terminal_is_not_stopped_repeatedly(runtime):
    client,headers,store=runtime
    scan=upload(client,headers).json()
    core=Lifecycle(store); core.lease('worker'); core.claim('worker'); core.unavailable(scan['scan_id'],'worker')
    stopped=[]
    cleanup=Cleanup(store,stopped.append)
    cleanup.sweep(); cleanup.sweep()
    assert stopped==[scan['scan_id']]


def test_completed_deletion_cannot_regress_and_metadata_expires(runtime):
    client,headers,store=runtime
    scan=upload(client,headers).json()
    operation=Cleanup(store).delete(scan['scan_id'],client.cookies.get('vibeguard_session'))
    Cleanup(store,lambda _:None).sweep()
    Cleanup(store).sweep()
    assert Cleanup(store).operation(operation.operation_id,client.cookies.get('vibeguard_session')).status=='complete'
    with store.connect() as db:
        db.execute('UPDATE scans SET created=?',(time.time()-86401,))
    Cleanup(store).sweep()
    with store.connect() as db:
        assert db.execute('SELECT count(*) FROM scans').fetchone()[0]==0
        assert db.execute('SELECT count(*) FROM deletions').fetchone()[0]==0
