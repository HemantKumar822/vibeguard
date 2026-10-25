import pytest
from backend.evaluation.metrics import score, assert_sanitized, guidance, failed_rows, markdown


def finding(rule='rule', line=1):
    return {'rule_id': rule, 'location': {'path': 'app.ts', 'line_start': line}}


def test_occurrences_deduplicate_but_preserve_distinct_lines_and_misses():
    labels = [{'rule': 'rule', 'resource': 'app.ts', 'line': line} for line in (1, 2)]
    result = score(labels, [finding(), finding(), finding('unexpected')])
    assert (result['tp'], result['fp'], result['fn']) == (1, 1, 1)
    assert result['precision'] == result['recall'] == .5
    assert result['expected_count'] == result['observed_count'] == 2


def test_failed_or_incomplete_checks_cannot_remove_missed_labels():
    result = score([{'rule': 'rule', 'resource': 'app.ts', 'line': 1}], [])
    assert result['fn'] == 1 and result['recall'] == 0 and result['precision'] is None
    empty = score([], [])
    assert empty['precision'] is empty['recall'] is None


def test_privacy_gate_checks_nested_and_escaped_surfaces_without_echoing_secret():
    with pytest.raises(ValueError, match='^acceptance_privacy_failure$'):
        assert_sanitized({'repair': {'prompt': 'planted-value'}}, ['planted-value'])
    with pytest.raises(ValueError, match='acceptance_evidence_limit'):
        assert_sanitized({'large': 'a' * (2 * 1024 * 1024)}, [])


def test_guidance_does_not_claim_human_judgment():
    item = {**finding(), 'explanation': 'impact', 'fix_guidance': 'change',
            'verification_steps': ['verify'], 'human_actions': ['rotate'], 'category': 'credential'}
    result = guidance({'findings': [item], 'repair': {'prompt_redacted': 'app.ts impact change verify'}})
    assert result['teammate_judgment'] == 'unassessed'
    assert result['structural'][0]['rotation'] is False
    assert result['structural'][0]['location'] is True


def test_acceptance_exit_gate_rejects_partial_and_false_positive_controls():
    evidence = {'runs': [{'transport': 'controlled', 'mode': 'website', 'variant': 'clean', 'status': 'partial',
                         'completed': False, 'metrics': {'fp': 1}}],
                'comparisons': [{'http_status': 409}], 'remaining_source_directories': 1, 'release_blockers': ['coverage']}
    assert failed_rows(evidence) == 3
    assert '| controlled | website | clean | partial |' in markdown(evidence)
    evidence['runs'] = [{'completed': True, 'metrics': None, 'guidance': {'structural': [{'rule': 'x', 'rotation': False}]}}]
    assert failed_rows(evidence) == 3
