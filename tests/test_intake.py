import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.api.main import create_app
from backend.core.settings import Settings

@pytest.fixture
def runtime(tmp_path):
    app = create_app(Settings(tmp_path / 'runtime', loopback_http=True))
    client = TestClient(app)
    origin = {'Origin': 'http://127.0.0.1:8000'}
    response = client.post('/api/v1/session', headers=origin)
    headers = {**origin, 'X-CSRF-Token': response.json()['csrf_token'], 'Idempotency-Key': 'test'}
    return client, headers, app.state.storage

def upload(client, headers, paths=None, data=b'const x = 1', **changes):
    paths = paths or ['app/src/main.ts']
    metadata = {'mode':'codebase', 'authorization_confirmed':True,
                'files':[{'part_id':f'f{i}', 'relative_path':p} for i,p in enumerate(paths)]}
    metadata.update(changes)
    return client.post('/api/v1/scans', headers=headers, files=[('metadata',(None,json.dumps(metadata))),
        *[(f'f{i}', ('ignored', data)) for i in range(len(paths))]])

def test_accept_inventory_default_sharing_and_owned_read(runtime):
    client, headers, store = runtime
    response = upload(client, headers, ['app/src/main.ts', 'node_modules/pkg/index.js'])
    assert response.status_code == 202, response.text
    scan = response.json()
    assert scan['status'] == 'queued' and scan['allow_external_ai'] is False
    assert scan['accepted_files'] == ['app/src/main.ts']
    assert scan['coverage']['inspected'] == [] and scan['coverage']['completed_count'] == 0
    assert scan['coverage']['exclusions'][0]['reason'] == 'vendor_or_build_output'
    assert client.get('/api/v1/scans/' + scan['scan_id']).json() == scan
    assert TestClient(client.app).get('/api/v1/scans/' + scan['scan_id']).status_code == 404
    assert len(list((store.staging / scan['scan_id']).iterdir())) == 2
    assert upload(client, headers, ['app/src/main.ts', 'node_modules/pkg/index.js']).json()['scan_id'] == scan['scan_id']
    assert upload(client, headers, data=b'changed').status_code == 409

@pytest.mark.parametrize('paths', [['/a.js'], ['../a.js'], ['a\\b.js'], ['C:/a.js'], ['con.js'], ['a./b.js'], ['a.js','A.js'], ['a.js','a.js/b.ts'], ['a//b.ts'], ['x/' * 20 + 'a.ts'], ['x'*241 + '.js']])
def test_unsafe_paths_cleanup(runtime, paths):
    client, headers, store = runtime
    assert upload(client, headers, paths).status_code == 422
    assert not list(store.staging.iterdir())

@pytest.mark.parametrize('changes,status', [({'authorization_confirmed':False},403), ({'authorization_confirmed':1},403), ({'allow_external_ai':1},422), ({'files':[]},400)])
def test_metadata_permission_mapping(runtime, changes, status):
    client, headers, store = runtime
    assert upload(client, headers, **changes).status_code == status
    assert not list(store.staging.iterdir())

@pytest.mark.parametrize('path,data', [('main.py',b'print(1)'), ('main.js',b'\xff'), ('main.js',b'\x00')])
def test_unsupported_only_rejected(runtime, path, data):
    client, headers, store = runtime
    assert upload(client, headers, [path], data).status_code == 422
    assert not list(store.staging.iterdir())

def test_file_limit_boundary(runtime):
    client, headers, store = runtime
    assert upload(client, headers, data=b'a'*(2*1024*1024)).status_code == 202
    headers['Idempotency-Key'] = 'over'
    assert upload(client, headers, data=b'a'*(2*1024*1024+1)).status_code == 413
    assert len(list(store.staging.iterdir())) == 1

def test_chunked_without_length_and_incomplete_cleanup(runtime):
    client, headers, store = runtime
    metadata = json.dumps({'mode':'codebase','authorization_confirmed':True,'files':[{'part_id':'f','relative_path':'main.js'}]})
    body = (f'--BOUND\r\nContent-Disposition: form-data; name="metadata"\r\n\r\n{metadata}\r\n--BOUND\r\nContent-Disposition: form-data; name="f"; filename="ignored"\r\n\r\nconst x=1\r\n--BOUND--\r\n').encode()
    headers['Content-Type'] = 'multipart/form-data; boundary=BOUND'
    response = client.post('/api/v1/scans', headers=headers, content=(body[i:i+7] for i in range(0,len(body),7)))
    assert response.status_code == 202, response.text
    headers['Idempotency-Key'] = 'incomplete'
    assert client.post('/api/v1/scans', headers=headers, content=iter([body[:-20]])).status_code == 400
    assert len(list(store.staging.iterdir())) == 1

def test_real_count_boundary_and_one_over(runtime):
    client, headers, store = runtime
    paths = [f'src/f{i}.ts' for i in range(5000)]
    assert upload(client, headers, paths, b'').status_code == 202
    headers['Idempotency-Key'] = 'count_over'
    assert upload(client, headers, paths + ['src/over.ts'], b'').status_code == 413
    assert len(list(store.staging.iterdir())) == 1

def test_aggregate_boundary_and_one_over(runtime):
    client, headers, store = runtime
    def send(extra):
        paths = [f'f{i}.ts' for i in range(13)]
        metadata = {'mode':'codebase','authorization_confirmed':True,'files':[{'part_id':f'f{i}','relative_path':p} for i,p in enumerate(paths)]}
        bodies = [(f'f{i}',('ignored', b'a' * (2*1024*1024 if i < 12 else 1024*1024 + extra))) for i in range(13)]
        return client.post('/api/v1/scans',headers=headers,files=[('metadata',(None,json.dumps(metadata))),*bodies])
    assert send(0).status_code == 202
    headers['Idempotency-Key'] = 'aggregate_over'
    assert send(1).status_code == 413
    assert len(list(store.staging.iterdir())) == 1

def test_exact_path_depth_and_utf8_boundary(runtime):
    client, headers, _ = runtime
    path = '/'.join(['a'] * 19 + ['b.ts'])
    assert upload(client, headers, [path]).status_code == 202
    headers['Idempotency-Key'] = 'utf8'
    path = 'é' * 118 + '.tsx'
    assert len(path.encode()) == 240
    assert upload(client, headers, [path]).status_code == 202
    headers['Idempotency-Key'] = 'utf8_over'
    assert upload(client, headers, ['é' * 119 + '.tsx']).status_code == 422

def test_disconnect_cleans_partial_staging(runtime):
    client, headers, store = runtime
    headers['Content-Type'] = 'multipart/form-data; boundary=B'
    def broken():
        yield b'--B\r\nContent-Disposition: form-data; name="f"\r\n\r\nsecret-content'
        raise RuntimeError('private transport failure')
    response = client.post('/api/v1/scans', headers=headers, content=broken())
    assert response.status_code == 400
    assert 'secret-content' not in response.text and 'private transport' not in response.text
    assert not list(store.staging.iterdir())

@pytest.mark.parametrize('parts', [
    [('metadata',(None,'{}')),('metadata',(None,'{}'))],
    [('metadata',(None,'not json'))],
    [('other',('file',b'x'))],
    [('f',('file',b'link','application/x-symlink'))],
])
def test_invalid_part_shapes_cleanup(runtime, parts):
    client, headers, store = runtime
    assert client.post('/api/v1/scans', headers=headers, files=parts).status_code in {400,422}
    assert not list(store.staging.iterdir())

def test_bounded_metadata_and_headers(runtime):
    client, headers, store = runtime
    assert client.post('/api/v1/scans', headers=headers, files=[('metadata',(None,' '*(2*1024*1024+1)))]).status_code == 413
    headers['Content-Type'] = 'multipart/form-data; boundary=B'
    body = b'--B\r\nX-Huge: ' + b'x'*8193 + b'\r\n\r\nbody\r\n--B--\r\n'
    assert client.post('/api/v1/scans',headers=headers,content=body).status_code == 413
    assert not list(store.staging.iterdir())

def test_expired_idempotency_key_reusable_with_active_session(runtime):
    import time
    client, headers, store = runtime
    first = upload(client, headers).json()
    with store.connect() as db:
        db.execute('UPDATE scans SET created=? WHERE id=?', (time.time()-86401, first['scan_id']))
    second = upload(client, headers, data=b'new payload')
    assert second.status_code == 202
    assert second.json()['scan_id'] != first['scan_id']
    assert client.get('/api/v1/scans/'+first['scan_id']).status_code == 200
    with store.connect() as db:
        assert db.execute('SELECT COUNT(*) FROM scans').fetchone()[0] == 2

@pytest.mark.parametrize('part_id', ['NUL','CON','aux','COM1','LPT9'])
def test_reserved_multipart_names_never_opened(runtime, part_id):
    client, headers, store = runtime
    metadata = {'mode':'codebase','authorization_confirmed':True,'files':[{'part_id':part_id,'relative_path':'main.ts'}]}
    response = client.post('/api/v1/scans',headers=headers,files=[('metadata',(None,json.dumps(metadata))),(part_id,('ignored',b'x'))])
    assert response.status_code == 400
    assert not list(store.staging.iterdir())

@pytest.mark.parametrize('mime', ['application/x-symlink; charset=utf-8','inode/chardevice; x=y','inode/blockdevice; x=y'])
def test_device_mime_parameters_rejected(runtime, mime):
    client, headers, store = runtime
    response = client.post('/api/v1/scans',headers=headers,files=[('f',('ignored',b'x',mime))])
    assert response.status_code == 422
    assert not list(store.staging.iterdir())

def test_env_variants_reviewable(runtime):
    client, headers, _ = runtime
    response = upload(client,headers,['.env.local','.env.production'],b'PUBLIC_NAME=example')
    assert response.status_code == 202
    assert response.json()['accepted_files'] == ['.env.local','.env.production']

def test_global_queue_cap_and_replay_at_capacity(runtime):
    client, headers, store = runtime
    first = upload(client,headers).json()
    for index in range(2):
        other = TestClient(client.app)
        csrf = other.post('/api/v1/session',headers={'Origin':headers['Origin']}).json()['csrf_token']
        other_headers = {**headers,'X-CSRF-Token':csrf,'Idempotency-Key':f'other{index}'}
        assert upload(other,other_headers).status_code == 202
    headers['Idempotency-Key'] = 'fourth'
    assert upload(client,headers).status_code == 429
    headers['Idempotency-Key'] = 'test'
    assert upload(client,headers).json()['scan_id'] == first['scan_id']
    assert len(list(store.staging.iterdir())) == 3
    with store.connect() as db:
        assert db.execute('SELECT COUNT(*) FROM scans').fetchone()[0] == 3

@pytest.mark.parametrize('deadline', ['idle','total','cancel'])
def test_stream_deadlines_and_cancellation_cleanup(runtime, monkeypatch, deadline):
    import asyncio
    import httpx
    import backend.adapters.intake as intake
    client, headers, store = runtime
    monkeypatch.setattr(intake,'IDLE_UPLOAD_SECONDS', .01 if deadline == 'idle' else 10)
    monkeypatch.setattr(intake,'TOTAL_UPLOAD_SECONDS', .01 if deadline == 'total' else 10)
    async def run():
        started = asyncio.Event()
        async def body():
            yield b'--B\r\nContent-Disposition: form-data; name="f"\r\n\r\nsource'
            started.set()
            await asyncio.sleep(1)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=client.app),base_url='http://testserver',cookies=client.cookies) as async_client:
            task = asyncio.create_task(async_client.post('/api/v1/scans',headers={**headers,'Content-Type':'multipart/form-data; boundary=B'},content=body()))
            if deadline == 'cancel':
                await started.wait()
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await task
            else:
                response = await task
                assert response.status_code == 400
                assert response.json()['error']['code'] == 'upload_deadline_exceeded'
    asyncio.run(run())
    assert not list(store.staging.iterdir())
    assert client.app.state.intake_guard.acquire(blocking=False)
    client.app.state.intake_guard.release()

def test_concurrent_intake_guard_before_staging(runtime, monkeypatch):
    import asyncio
    import httpx
    import backend.api.main as main
    client, headers, store = runtime
    async def run():
        entered, finish = asyncio.Event(), asyncio.Event()
        async def blocked(request,directory):
            entered.set()
            await finish.wait()
            raise main.IntakeError(400,'test_stop')
        monkeypatch.setattr(main,'receive',blocked)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=client.app),base_url='http://testserver',cookies=client.cookies) as async_client:
            first = asyncio.create_task(async_client.post('/api/v1/scans',headers=headers,content=b'x'))
            await entered.wait()
            assert len(list(store.staging.iterdir())) == 1
            second = await async_client.post('/api/v1/scans',headers={**headers,'Idempotency-Key':'second'},content=b'x')
            assert second.status_code == 429 and second.json()['error']['code'] == 'intake_busy'
            assert len(list(store.staging.iterdir())) == 1
            finish.set()
            assert (await first).status_code == 400
    asyncio.run(run())
    assert not list(store.staging.iterdir())
