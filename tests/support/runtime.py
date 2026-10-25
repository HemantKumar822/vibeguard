"""Owned temporary API runtime and bounded upload helper."""
import json
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
