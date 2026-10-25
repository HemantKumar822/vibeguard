import json
from pathlib import Path
import pytest
from backend.api.session import IntakeError
from backend.core.contracts import Scan
from backend.core.comparison import compare

@pytest.fixture
def pair():
    before=Scan.model_validate(json.loads(Path('fixtures/contracts/source-baseline.json').read_text())['data'])
    # Use an explicit compatible manifest, without treating fixture metadata as real runtime evidence.
    for tool in before.tools:
        if tool.required:
            tool.version='fixture-v1'; tool.image_digest='sha256:fixture'; tool.rules_fingerprint='fixture-rules'
            tool.coverage.inspected=sorted({f.location.path for f in before.findings})
    after=before.model_copy(deep=True)
    after.scan_id='new';after.baseline_id=before.scan_id
    for index,f in enumerate(after.findings): f.id='after-'+str(index)
    return before,after


def test_line_shift_matches_without_using_line_or_public_id(pair):
    before,after=pair
    for f in after.findings: f.location.line_start+=10;f.location.line_end=f.location.line_start
    result=compare(before,after)
    assert all(item.status=='still_detected' for item in result.items)
    assert before.findings[0].id!=after.findings[0].id


def test_absence_is_only_comparable_observation_and_retains_actions(pair):
    before,after=pair; after.findings=[]
    result=compare(before,after)
    assert all(item.status=='not_detected' for item in result.items)
    assert result.human_actions


@pytest.mark.parametrize('change',['failed','missing','fingerprint','policy'])
def test_uncertain_absence_is_unverified(pair,change):
    before,after=pair; after.findings=[]
    if change=='failed': after.coverage.scope_complete=False
    if change=='missing':
        for tool in after.tools: tool.coverage.inspected=[]
    if change=='fingerprint':
        for tool in after.tools: tool.rules_fingerprint='changed'
    if change=='policy': after.policy_fingerprint='changed'
    result=compare(before,after)
    assert result.status=='partial' and all(item.status=='unverified' for item in result.items)


def test_duplicate_candidates_never_pair_arbitrarily(pair):
    before,after=pair
    before.findings.append(before.findings[0].model_copy(update={'id':'duplicate'}))
    result=compare(before,after)
    assert any(item.reason_code=='ambiguous_candidates' for item in result.items)


def test_invalid_lineage_or_mode_conflicts(pair):
    before,after=pair;after.baseline_id=None
    with pytest.raises(IntakeError): compare(before,after)


def test_positive_observation_survives_partial_scope(pair):
    before,after=pair;after.coverage.scope_complete=False
    assert all(i.status=='still_detected' for i in compare(before,after).items)


@pytest.mark.parametrize('change',['query','origin','missing','collision'])
@pytest.mark.parametrize('positive',[True,False])
def test_website_identity_uncertainty(change,positive):
    before=Scan.model_validate(json.loads(Path('fixtures/contracts/website.json').read_text())['data'])
    before.findings=before.findings[:1]
    location=before.findings[0].location
    location.url_redacted='https://controlled.example/page'+('?query=redacted' if change=='query' else '')
    location.resource_key=location.url_redacted
    before.input.target_redacted='https://controlled.example/'
    for tool in before.tools:
        if tool.required:
            tool.version='fixture'; tool.image_digest='fixture'; tool.rules_fingerprint='fixture'
            tool.coverage.inspected=[location.resource_key]
    after=before.model_copy(deep=True); after.scan_id='repeat';after.baseline_id=before.scan_id
    if positive: after.findings[0].id='new-finding'
    else: after.findings=[]
    if change=='origin': after.input.target_redacted='https://different.example/'
    if change=='missing':
        for tool in after.tools: tool.coverage.inspected=[]
    if change=='collision':
        for tool in after.tools: tool.coverage.inspected.append(location.resource_key)
    result=compare(before,after)
    assert result.status=='partial'
    assert all(item.status=='unverified' for item in result.items)


def test_changed_origin_empty_reports_are_not_comparable():
    before=Scan.model_validate(json.loads(Path('fixtures/contracts/website.json').read_text())['data'])
    before.findings=[];before.input.target_redacted='https://first.example/'
    after=before.model_copy(deep=True);after.scan_id='new';after.baseline_id=before.scan_id
    after.input.target_redacted='https://second.example/'
    assert compare(before,after).status=='partial'


def test_adapter_line_shift_and_unrelated_replacement(tmp_path):
    from backend.adapters.source import normalize
    path=tmp_path/'app.ts'
    def finding(code,line):
        path.write_text(code)
        raw=json.dumps({'results':[{'check_id':'vg-unsafe-eval','path':'app.ts','start':{'line':line}}], 'paths':{'scanned':['app.ts']}}).encode()
        return normalize('semgrep',raw,tmp_path)[0][0]
    original=finding('eval(req.query.code);',1)
    shifted=finding('\n\neval(req.query.code);',3)
    assert original.match_context==shifted.match_context
    replaced=finding('eval(otherInput);',1)
    assert 'uncertain_identifier' in replaced.match_context
    assert original.match_context!=replaced.match_context


def test_different_unknown_identifiers_never_claim_a_positive_match(pair):
    before,after=pair
    for scan in (before,after):
        scan.findings=scan.findings[:1]
        scan.findings[0].match_context='structural-v1:eval ( uncertain_identifier )'
    result=compare(before,after)
    assert result.items[0].status=='unverified'
    assert result.items[0].reason_code=='uncertain_structural_context'
