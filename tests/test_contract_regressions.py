import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.core.contracts import Scan, SourceLocation, ComparisonItem, Tool

FIXTURES = Path('fixtures/contracts')


def data(name):
    return json.loads((FIXTURES / f'{name}.json').read_text())['data']


@pytest.mark.parametrize('path', ['/etc/passwd', '../demo.ts', 'src/../demo.ts', 'C:/demo.ts', r'src\demo.ts'])
def test_unsafe_source_paths_fail_with_valid_line_numbers(path):
    with pytest.raises(ValidationError):
        SourceLocation(kind='source', path=path, line_start=1, line_end=2)


def test_valid_source_location_is_accepted():
    assert SourceLocation(kind='source', path='src/demo.ts', line_start=1, line_end=2).path == 'src/demo.ts'


@pytest.mark.parametrize('status', ['partial', 'failed'])
def test_terminal_scan_cannot_retain_running_tools(status):
    scan = data('source-running')
    scan.update(status=status, finished_at='2026-10-24T00:00:00Z', repair=data('source-clean')['repair'])
    with pytest.raises(ValidationError):
        Scan.model_validate(scan)


def test_complete_tool_cannot_claim_unfinished_coverage():
    scan = data('source-clean')
    scan['tools'][0]['coverage']['completed_count'] = 0
    with pytest.raises(ValidationError):
        Scan.model_validate(scan)


@pytest.mark.parametrize('reason', [None, '', ' '])
def test_skipped_tool_requires_a_reason(reason):
    tool = data('source-clean')['tools'][0]
    tool.update(status='skipped', reason=reason)
    with pytest.raises(ValidationError):
        Tool.model_validate(tool)


@pytest.mark.parametrize('status', ['still_detected', 'newly_detected', 'not_detected', 'unverified'])
def test_comparison_item_requires_observed_finding_identity(status):
    with pytest.raises(ValidationError):
        ComparisonItem(baseline_finding_id=None, new_finding_id=None, status=status,
                       reason_code='example', baseline_evidence_ref=None, new_evidence_ref=None)


@pytest.mark.parametrize('status,baseline,new', [
    ('still_detected', 'baseline-finding', 'new-finding'),
    ('not_detected', 'baseline-finding', None),
    ('newly_detected', None, 'new-finding'),
])
def test_observed_comparison_findings_require_traceable_evidence_refs(status, baseline, new):
    with pytest.raises(ValidationError):
        ComparisonItem(baseline_finding_id=baseline, new_finding_id=new, status=status,
                       reason_code='example', baseline_evidence_ref=None, new_evidence_ref=None)


def test_website_fixture_uses_web_observation_and_asset_coverage():
    scan = data('website')
    observation = scan['input']['observation_id']
    assert scan['coverage']['revision_or_observation'] == observation
    for tool in scan['tools']:
        if tool['applicable']:
            assert tool['coverage']['revision_or_observation'] == observation
            assert not any(key.startswith('src/') for key in tool['coverage']['inspected'])
    finding = scan['findings'][0]
    asset_tool = next(t for t in scan['tools'] if t['name'] == finding['scanner'])
    assert finding['location']['resource_key'] in asset_tool['coverage']['inspected']


def test_comparison_fixtures_reference_real_example_scan_pairs():
    scans = {}
    comparisons = []
    for path in FIXTURES.glob('*.json'):
        fixture = json.loads(path.read_text())
        if fixture['kind'] == 'scan':
            scans[fixture['data']['scan_id']] = fixture['data']
        elif fixture['kind'] == 'comparison':
            comparisons.append(fixture['data'])
    assert any(f['location']['kind'] == 'source' for s in scans.values() for f in s['findings'])
    for comparison in comparisons:
        baseline, new = scans[comparison['baseline_id']], scans[comparison['new_id']]
        assert new['baseline_id'] == baseline['scan_id']
        assert comparison['baseline_coverage'] == baseline['coverage']
        assert comparison['new_coverage'] == new['coverage']
        for item in comparison['items']:
            if item['baseline_finding_id']:
                assert item['baseline_finding_id'] in {f['id'] for f in baseline['findings']}
            if item['new_finding_id']:
                assert item['new_finding_id'] in {f['id'] for f in new['findings']}
