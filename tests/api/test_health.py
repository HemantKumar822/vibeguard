from fastapi.testclient import TestClient
from backend.api.main import create_app


def test_health_is_available_without_private_runtime(monkeypatch):
    monkeypatch.delenv('VIBEGUARD_RUNTIME_DIR', raising=False)
    client = TestClient(create_app())
    assert client.get('/api/v1/health').json() == {'status': 'ok', 'contract_version': 'v1'}


def test_scan_admission_requires_configured_private_runtime(monkeypatch):
    monkeypatch.delenv('VIBEGUARD_RUNTIME_DIR', raising=False)
    response = TestClient(create_app()).post('/api/v1/scans', json={})
    assert response.status_code == 503
    assert response.json()['error']['code'] == 'runtime_unavailable'
