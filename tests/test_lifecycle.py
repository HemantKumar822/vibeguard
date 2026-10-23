from concurrent.futures import ThreadPoolExecutor
import time
import pytest
from backend.core.lifecycle import Lifecycle
from backend.api.session import IntakeError
from test_intake import runtime, upload


def test_transactional_claim_and_unavailable(runtime):
    client, headers, store = runtime
    scan = upload(client, headers).json()
    core = Lifecycle(store)
    assert core.lease('coordinator')
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: core.claim('coordinator'), range(4)))
    assert len([result for result in results if result]) == 1
    assert core.unavailable(scan['scan_id'], 'coordinator')
    result = client.get('/api/v1/scans/' + scan['scan_id']).json()
    assert result['status'] == 'failed'
    assert result['coverage']['completed_count'] == 0
    assert all(t['status'] not in {'running', 'queued'} for t in result['tools'])
    assert result['repair']['status'] == 'fallback'


def test_lease_recovery_and_late_write_fence(runtime):
    client, headers, store = runtime
    scan = upload(client, headers).json()
    core = Lifecycle(store)
    assert core.lease('old') and core.claim('old')
    assert not core.lease('new')
    with store.connect() as db:
        db.execute('UPDATE coordinator SET heartbeat=?', (time.time()-16,))
    assert core.lease('new')
    assert not core.unavailable(scan['scan_id'], 'old')
    assert client.get('/api/v1/scans/' + scan['scan_id']).json()['error']['code'] == 'coordinator_lost'
    assert core.claim('new') is None


@pytest.mark.parametrize('state,age', [('queued',601),('running',301)])
def test_deadlines(runtime, state, age):
    client, headers, store = runtime
    scan = upload(client, headers).json()
    core = Lifecycle(store); core.lease('token')
    if state == 'running': core.claim('token')
    column = 'created' if state == 'queued' else 'claimed'
    with store.connect() as db:
        db.execute(f'UPDATE scans SET {column}=?', (time.time()-age,))
    assert core.claim('token') is None
    result = client.get('/api/v1/scans/'+scan['scan_id']).json()
    assert result['status'] == 'failed'
    assert result['tools'][0]['status'] == 'timed_out'


def test_coordinator_dispatch_and_cleanup_sequence(runtime):
    from workers.coordinator import run_once
    from backend.core.cleanup import Cleanup
    client,headers,store=runtime
    scan=upload(client,headers).json()
    stopped=[]
    result=run_once(Lifecycle(store),Cleanup(store,stopped.append),'coordinator')
    assert result.scan_id==scan['scan_id']
    assert scan['scan_id'] in stopped
    assert not (store.staging/scan['scan_id']).exists()
    report=client.get('/api/v1/scans/'+scan['scan_id']).json()
    assert report['status']=='failed'
    assert report['error']['code']=='trusted_adapters_unavailable'
