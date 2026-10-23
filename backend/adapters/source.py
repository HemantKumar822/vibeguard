"""Trusted scanner output boundary: never copy vendor strings into public fields."""
import hashlib
import json
import secrets
import re
from pathlib import Path
from backend.core.contracts import Finding, SourceLocation

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / 'rules'
RULE_DATA = {
    'vg-private-key': ('credential', 'Private signing key candidate', 'critical', 'high', 'Remove private key material from source and secret stores that expose it.'),
    'vg-aws-access-key': ('credential', 'AWS access key candidate', 'high', 'high', 'Replace embedded credentials with a server-side secret reference.'),
    'vg-github-token': ('credential', 'GitHub token candidate', 'high', 'high', 'Replace embedded tokens with a server-side secret reference.'),
    'vg-secret-assignment': ('credential', 'Private credential assignment candidate', 'high', 'medium', 'Confirm this is a private credential and move it to a server-side secret store.'),
    'vg-unsafe-eval': ('unsafe_input', 'Dynamic evaluation candidate', 'high', 'medium', 'Trace input provenance; replace eval with a constrained parser or explicit allowlist.'),
    'vg-tls-disabled': ('insecure_configuration', 'TLS verification disabled', 'high', 'high', 'Enable certificate verification and configure a trusted certificate authority.'),
    'vg-access-candidate': ('access_check', 'Review route authorization', 'medium', 'needs_review', 'Check global middleware and handler authorization; add server-side access checks where missing.'),
}


def fingerprint():
    digest = hashlib.sha256(b'vibeguard-source-v2:allowlisted-structural-identifiers:uncertain-unknown-identifiers:no-suppressions:no-source-execution')
    for name in ('gitleaks.toml', 'semgrep.json', 'empty.ignore'):
        digest.update(name.encode()); digest.update((RULES / name).read_bytes())
    return digest.hexdigest()


def structure(source, path, line):
    # Preserve only punctuation/keyword shape, never literals or caller identifiers.
    text=(source/path).read_text(encoding='utf-8').splitlines()[line-1]
    text=re.sub(r'([\"\'`])(?:\\.|(?!\1).)*?\1', ' LITERAL ', text)
    tokens=re.findall(r'[A-Za-z_$][A-Za-z0-9_$]*|[0-9]+|[^\w\s]',text)
    keywords={'const','let','var','return','if','else','function','async','await','true','false','null','new','eval','req','request','query','params','body','code','JSON','parse','app','get','post','res','response','send','rejectUnauthorized','verify','LITERAL'}
    return ' '.join(token if token in keywords or not re.fullmatch(r'[A-Za-z0-9_$]+',token) else 'uncertain_identifier' for token in tokens)[:512]


def normalize(tool, raw, source):
    """Return sanitized candidates and inspected files; reject malformed/incomplete reports."""
    try:
        payload = json.loads(raw)
        if tool == 'gitleaks':
            if not isinstance(payload, list): raise ValueError
            rows, inspected = payload, None
        else:
            if not isinstance(payload, dict) or payload.get('errors') or not isinstance(payload.get('results'), list): raise ValueError
            rows = payload['results']
            paths = payload.get('paths', {})
            if not isinstance(paths, dict) or not isinstance(paths.get('scanned'), list): raise ValueError
            inspected = [relative(item, source) for item in paths['scanned']]
        findings = []
        for row in rows:
            if not isinstance(row, dict): raise ValueError
            rule = row.get('RuleID') if tool == 'gitleaks' else row.get('check_id')
            if rule not in RULE_DATA: raise ValueError
            if (RULE_DATA[rule][0]=='credential') != (tool=='gitleaks'): raise ValueError
            path = relative(row.get('File') if tool == 'gitleaks' else row.get('path'), source)
            line = row.get('StartLine') if tool == 'gitleaks' else row.get('start', {}).get('line')
            if type(line) is not int or not 1 <= line <= max(1, len((source / path).read_text(encoding='utf-8').splitlines())): raise ValueError
            category, title, severity, confidence, fix = RULE_DATA[rule]
            actions = ['Revoke or rotate the exposed credential at its provider; source removal alone does not revoke it.'] if category == 'credential' else []
            reason = ('Only a local route shape was observed. Global middleware or handler checks may protect it; this is not proof of a bypass.'
                      if category == 'access_check' else 'A selected trusted static rule matched; review the actual application context.')
            findings.append(Finding(id=secrets.token_hex(16), scanner=tool, rule_id=rule, category=category,
                title=title, severity=severity, confidence=confidence, confidence_reason=reason,
                location=SourceLocation(kind='source', path=path, line_start=line, line_end=line),
                evidence_redacted=f'Trusted rule {rule} matched at the reported file and line. Source literals are omitted.',
                explanation=title + '. ' + reason, fix_guidance=fix,
                verification_steps=['Review the reported location and any surrounding authorization/data flow.',
                                    'Add a vulnerable/control regression case and rerun the same trusted checks.'],
                human_actions=actions, match_context=f'structural-v2:{tool}:{rule}:{path}:{structure(source,path,line)}'))
        return findings, inspected
    except (ValueError, TypeError, KeyError, AttributeError, OSError):
        raise ValueError('invalid_scanner_report') from None


def relative(value, source):
    if not isinstance(value, str): raise ValueError('invalid_location')
    value = value.removeprefix('/source/').removeprefix('./')
    location = SourceLocation(kind='source', path=value, line_start=None, line_end=None)
    path = source / location.path
    if not path.is_file() or path.is_symlink() or source.resolve() not in path.resolve().parents:
        raise ValueError('invalid_location')
    return location.path
