"""Public web evidence is built from trusted templates, never raw vendor messages."""
import hashlib
import json
import re
import secrets
from backend.adapters.web_capture import display
from backend.core.contracts import Finding, WebLocation

# Actual ZAP IDs remain visible, while descriptions/remediation use approved wording.
KNOWN={
    '10020':('Frame embedding policy missing','Restrict frame embedding with an appropriate Content-Security-Policy frame-ancestors directive.'),
    '10021':('Content type sniffing protection missing','Set X-Content-Type-Options: nosniff on appropriate responses.'),
    '10035':('Strict transport policy missing','For HTTPS deployments, configure a suitable Strict-Transport-Security policy after confirming HTTPS coverage.'),
    '10038':('Content security policy missing','Define and test a restrictive Content-Security-Policy suited to the application.'),
    '10015':('Cache policy requires review','Review cache-control headers for the sensitivity of this response.'),
    '10010':('Cookie HttpOnly policy requires review','Set HttpOnly on sensitive session cookies where appropriate.'),
    '10011':('Cookie transport policy requires review','Set Secure on sensitive cookies served over HTTPS.'),
    '10054':('Cookie SameSite policy requires review','Set a suitable SameSite policy on authentication/session cookies.'),
    '10023':('Information disclosure candidate','Remove unnecessary diagnostic or technology-disclosure response information.'),
    '10036':('Server version disclosure candidate','Review and minimize unnecessary server version disclosure.'),
}


def zap_findings(raw,resources):
    try:
        value=json.loads(raw)
        if value.get('mode')!='offline-passive-har' or value.get('version')!='2.17.0' or value.get('isolation_verified') is not True or value.get('error') or not isinstance(value.get('alerts'),list) or not value.get('plugins'): raise ValueError
        if value.get('expected')!=len(resources) or value.get('messages',0)<len(resources): raise ValueError
        findings=[]
        for alert in value['alerts']:
            code=alert.get('pluginId')
            if not isinstance(code,str) or not re.fullmatch(r'[0-9]{1,8}',code): raise ValueError
            resource=resources.get(alert.get('url'))
            if resource is None: raise ValueError
            risk=alert.get('risk'); confidence=alert.get('confidence')
            if risk not in {'Informational','Low','Medium','High'} or confidence not in {'False Positive','Low','Medium','High','Confirmed'}: raise ValueError
            title,fix=KNOWN.get(code,('Passive deployment finding requires review',
                'Review the official ZAP alert rule and the affected response; apply context-appropriate remediation.'))
            findings.append(Finding(id=secrets.token_hex(16),scanner='zap',rule_id=code,
                category='insecure_configuration',title=title,
                severity={'Informational':'info','Low':'low','Medium':'medium','High':'high'}[risk],
                confidence={'False Positive':'needs_review','Low':'needs_review','Medium':'medium','High':'high','Confirmed':'high'}[confidence],
                confidence_reason='Actual ZAP passive alert on a captured response; application context still requires human review.',
                location=WebLocation(kind='web',url_redacted=resource['display'],resource_key=resource['key'],part='response',parameter_redacted=None,line_start=None),
                evidence_redacted=f'ZAP passive rule {code} observed the recorded response. Raw headers, values and body excerpts are omitted.',
                explanation=title+'. This is a deployment observation, not proof of exploitability or access to private backend source.',
                fix_guidance=fix,verification_steps=['Review the response and the official ZAP alert definition.',
                    'Apply the change and perform a new authorized review of the corrected deployment.'],human_actions=[],
                match_context=f'zap:{code}:{resource["key"]}'))
        plugins=value['plugins']
        if any(not isinstance(name,str) or not re.fullmatch(r'[a-f0-9]{64}',digest) for name,digest in plugins.items()): raise ValueError
        return findings,hashlib.sha256(json.dumps(plugins,sort_keys=True).encode()).hexdigest()
    except (ValueError,TypeError,AttributeError,KeyError): raise ValueError('invalid_zap_report') from None


def asset_findings(findings,mapping):
    result=[]
    for finding in findings:
        resource=mapping.get(finding.location.path)
        if resource is None: raise ValueError('unknown_asset_location')
        finding.scanner='asset_secrets'
        finding.location=WebLocation(kind='web',url_redacted=resource['display'],resource_key=resource['key'],part='asset',parameter_redacted=None,line_start=finding.location.line_start)
        finding.match_context=f'asset_secrets:{finding.rule_id}:{resource["display"]}:asset'
        result.append(finding)
    return result
