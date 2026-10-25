import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.api.main import app
from backend.core.contracts import Intake, Scan, Comparison, Deletion, ErrorResponse

FIXTURES = Path('fixtures/contracts')




def test_required_contract_fixtures_validate():
    fixtures = list(FIXTURES.glob('*.json'))
    assert {p.stem for p in fixtures} == {
        'source-running', 'source-partial', 'source-clean', 'website',
        'ai-fallback', 'comparison', 'comparison-unverified', 'deletion-failed', 'source-baseline', 'source-corrected'}
    models = {'scan': Scan, 'comparison': Comparison, 'deletion': Deletion}
    for path in fixtures:
        fixture = json.loads(path.read_text())
        models[fixture['kind']].model_validate(fixture['data'])


def test_complete_scan_cannot_hide_a_failed_required_check():
    scan = json.loads((FIXTURES/'source-partial.json').read_text())['data']
    scan['status'] = 'complete'
    with pytest.raises(ValidationError):
        Scan.model_validate(scan)


def test_invalid_location_and_fake_fix_status_are_rejected():
    fixture = json.loads((FIXTURES/'website.json').read_text())['data']
    fixture['findings'][0]['location'] = {'kind': 'source', 'path': '/private/source.js', 'line_start': 0, 'line_end': 0}
    with pytest.raises(ValidationError):
        Scan.model_validate(fixture)
    comparison = json.loads((FIXTURES/'comparison.json').read_text())['data']
    comparison['items'][0]['status'] = 'verified_fixed'
    with pytest.raises(ValidationError):
        Comparison.model_validate(comparison)


@pytest.mark.parametrize('payload', [
    {'mode': 'repository', 'repository_url': 'https://github.com/team/demo', 'authorization_confirmed': False, 'allow_external_ai': False},
    {'mode': 'repository', 'target_url': 'https://example.com', 'authorization_confirmed': True, 'allow_external_ai': False},
    {'mode': 'website', 'target_url': 'https://example.com', 'authorization_confirmed': True, 'allow_external_ai': False, 'extra': 'forbidden'},
    {'mode': 'website', 'target_url': 'https://example.com', 'authorization_confirmed': 1, 'allow_external_ai': False},
    {'mode': 'website', 'target_url': 'https://example.com', 'authorization_confirmed': True, 'allow_external_ai': 1},
])
def test_intake_rejects_permission_missing_fields_and_unknown_fields(payload):
    with pytest.raises(ValidationError):
        Intake.model_validate(payload)




def test_generated_schema_matches_live_app():
    assert json.loads(Path('contracts/openapi.json').read_text()) == app.openapi()


def test_error_response_has_the_contract_wrapper():
    value = {'error': {'code': 'not_ready', 'message': 'Not available.', 'request_id': 'example', 'details': {}}}
    assert ErrorResponse.model_validate(value).model_dump() == value


def test_failed_deletion_requires_an_explicit_error():
    fixture = json.loads((FIXTURES/'deletion-failed.json').read_text())['data']
    fixture['error'] = None
    with pytest.raises(ValidationError):
        Deletion.model_validate(fixture)


def test_implemented_openapi_errors_and_submission_headers():
    schema = app.openapi()
    submission = schema['paths']['/api/v1/scans']['post']
    assert {parameter['name'] for parameter in submission['parameters'] if parameter['required']} == {'Origin','X-CSRF-Token','Idempotency-Key'}
    for status in ['400','403','404','409','413','422','429','503']:
        assert submission['responses'][status]['content']['application/json']['schema']['$ref'].endswith('/ErrorResponse')
