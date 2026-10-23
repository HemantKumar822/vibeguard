from fastapi.testclient import TestClient
import pytest
from backend.api.main import create_app
from backend.core.settings import Settings

def test_sessions_origin_csrf_and_cookie(tmp_path):
    client = TestClient(create_app(Settings(tmp_path / 'runtime', loopback_http=True)))
    assert client.post('/api/v1/session').status_code == 403
    response = client.post('/api/v1/session', headers={'Origin':'http://127.0.0.1:8000'})
    assert response.status_code == 200
    cookie = response.headers['set-cookie'].lower()
    assert 'httponly' in cookie and 'samesite=strict' in cookie
    assert client.post('/api/v1/session', headers={'Origin':'http://127.0.0.1:8000'}).json() == response.json()
    assert client.get('/api/v1/capabilities').json()['permitted_modes'] == ['codebase','repository']
    assert client.post('/api/v1/scans').status_code == 403

def test_runtime_rejects_checkout_and_onedrive(tmp_path):
    from pathlib import Path
    for path in [Path.cwd() / 'runtime', tmp_path / 'OneDrive' / 'runtime', Path('relative')]:
        with pytest.raises(ValueError):
            Settings(path, loopback_http=True).validate()
    with pytest.raises(ValueError):
        Settings(tmp_path / 'runtime').validate()

@pytest.mark.parametrize('origin,csrf', [('valid','missing'),('valid','wrong'),('wrong','valid')])
def test_independent_mutation_guards(tmp_path, origin, csrf):
    client = TestClient(create_app(Settings(tmp_path/'runtime',loopback_http=True)))
    valid_origin = 'http://127.0.0.1:8000'
    token = client.post('/api/v1/session',headers={'Origin':valid_origin}).json()['csrf_token']
    headers = {'Origin':valid_origin if origin == 'valid' else 'http://wrong.example','Idempotency-Key':'guard'}
    if csrf != 'missing':
        headers['X-CSRF-Token'] = token if csrf == 'valid' else 'wrong'
    assert client.post('/api/v1/scans',headers=headers,content=b'anything').status_code == 403
    store = client.app.state.storage
    assert not list(store.staging.iterdir())
    with store.connect() as db:
        assert db.execute('SELECT COUNT(*) FROM scans').fetchone()[0] == 0

@pytest.mark.parametrize('descendant', ['sources','metadata.sqlite3','sources/nested'])
def test_runtime_rejects_descendant_links_before_open(tmp_path, descendant):
    import os, subprocess
    from backend.adapters.storage import Storage
    root, outside = tmp_path/'runtime', tmp_path/'outside'
    root.mkdir(); outside.mkdir()
    marker = outside/'marker'; marker.write_text('unchanged')
    target = root/descendant
    target.parent.mkdir(parents=True,exist_ok=True)
    if descendant == 'metadata.sqlite3':
        try:
            target.symlink_to(marker)
        except OSError:
            os.link(marker,target)
    elif os.name == 'nt':
        subprocess.run(['cmd','/c','mklink','/J',str(target),str(outside)],capture_output=True,check=True)
    else:
        target.symlink_to(outside,target_is_directory=True)
    with pytest.raises(ValueError,match='Unsafe runtime descendant'):
        Storage(Settings(root,loopback_http=True))
    assert marker.read_text() == 'unchanged'

def test_existing_descendants_private(tmp_path):
    import os, stat, subprocess
    from backend.adapters.storage import Storage
    root = tmp_path/'runtime'
    child = root/'sources'/'old'
    child.mkdir(parents=True)
    file = child/'body'; file.write_text('source')
    if os.name != 'nt':
        child.chmod(0o777); file.chmod(0o666)
    Storage(Settings(root,loopback_http=True))
    if os.name == 'nt':
        output = subprocess.run(['icacls',str(file)],capture_output=True,text=True,check=True).stdout
        assert 'Everyone' not in output and 'BUILTIN\\Users' not in output
    else:
        assert stat.S_IMODE(child.stat().st_mode) == 0o700
        assert stat.S_IMODE(file.stat().st_mode) == 0o600
