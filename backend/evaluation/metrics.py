"""Occurrence metrics retain misses even when a scanner or scope is incomplete."""
import json
from collections import Counter


def coverage_record(coverage):
    """Keep measured counts/reasons without copying a whole repository inventory."""
    return {key: coverage.get(key) for key in ('required_count', 'completed_count', 'rules_fingerprint', 'revision_or_observation', 'scope_complete')} | {
        'inspected_count': len(coverage.get('inspected', [])),
        'exclusion_count': len(coverage.get('exclusions', [])),
        'exclusion_reasons': dict(Counter(item['reason'] for item in coverage.get('exclusions', [])))}


def occurrence(finding):
    location = finding['location']
    return (finding['rule_id'], location.get('path') or location.get('url_redacted'), location.get('line_start'))


def score(expected, findings):
    wanted = {(item['rule'], item['resource'], item['line']) for item in expected}
    observed = {occurrence(item) for item in findings}
    tp, fp, fn = len(wanted & observed), len(observed - wanted), len(wanted - observed)
    return {'tp': tp, 'fp': fp, 'fn': fn, 'expected_count': len(wanted), 'observed_count': len(observed),
            'precision': tp / (tp + fp) if tp + fp else None,
            'recall': tp / (tp + fn) if tp + fn else None,
            'missed': sorted(wanted - observed, key=str), 'unexpected': sorted(observed - wanted, key=str)}


def guidance(scan):
    """Structural checks, explicitly separate from subjective teammate usefulness."""
    prompt = (scan.get('repair') or {}).get('prompt_redacted', '')
    findings = scan['findings']
    return {'structural': [{
        'rule': item['rule_id'],
        'location': str(item['location'].get('path') or item['location'].get('url_redacted')) in prompt,
        'impact': bool(item['explanation']) and item['explanation'] in prompt,
        'actionable_change': bool(item['fix_guidance']) and item['fix_guidance'] in prompt,
        'verification': bool(item['verification_steps']) and all(step in prompt for step in item['verification_steps']),
        'rotation': all(action in prompt for action in item['human_actions']) if item['category'] == 'credential' else None,
    } for item in findings], 'teammate_judgment': 'unassessed'}


def assert_sanitized(value, planted):
    encoded = json.dumps(value, ensure_ascii=False)
    if any(secret in encoded for secret in planted):
        raise ValueError('acceptance_privacy_failure')
    if len(encoded.encode()) > 2 * 1024 * 1024:
        raise ValueError('acceptance_evidence_limit')


def failed_rows(evidence):
    """An error, miss, unexpected occurrence or malformed comparison is never a pass."""
    failures = [row for row in evidence['runs'] if not row['completed']
                or (row.get('metrics') or {}).get('fn', 0) or (row.get('metrics') or {}).get('fp', 0)
                or any(value is False for criterion in row.get('guidance', {}).get('structural', [])
                       for key, value in criterion.items() if key != 'rule')]
    return len(failures) + sum(item['http_status'] != 200 for item in evidence['comparisons']) + int(evidence['remaining_source_directories'] != 0)


def markdown(evidence):
    lines = ['# Measured scanner acceptance', '',
             'Controlled transport uses actual pinned workers with local acquisition fixtures. Live observations have no accuracy denominator.', '',
             '| Transport | Mode | Variant | Status | Seconds | TP | FP | FN |',
             '|---|---|---|---|---:|---:|---:|---:|']
    for row in evidence['runs']:
        metrics = row.get('metrics') or {}
        lines.append('| ' + ' | '.join(str(value) for value in [row['transport'], row['mode'], row['variant'],
                     row.get('status', row.get('admission_status')), row.get('elapsed_seconds', '—'),
                     metrics.get('tp', '—'), metrics.get('fp', '—'), metrics.get('fn', '—')]) + ' |')
    lines += ['', f"Remaining source directories: {evidence['remaining_source_directories']}.", '',
              'Release blockers (exit zero only means executed checks passed):', '']
    lines += ['- ' + item for item in evidence['release_blockers']]
    return '\n'.join(lines) + '\n'
