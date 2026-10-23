"""Website orchestration: one controlled capture, two network-disabled analyzers."""
from datetime import datetime, timezone
import hashlib
import json
import tempfile
import time
from pathlib import Path
from backend.adapters.web_capture import capture, display, TEXT_TYPES, write_har
from backend.adapters.web_report import zap_findings, asset_findings
from backend.adapters.source import fingerprint, normalize
from backend.core.contracts import Scan, SafeError, Exclusion
from backend.core.repair import repair_for
from backend.core.website_readiness import implementation


def execute(scan,lifecycle,launcher,token,capture_fn=capture):
    stage=lifecycle.store.staging/scan.scan_id
    active=lambda:lifecycle.active(scan.scan_id,token)
    # Verify Docker and both required immutable images before the first web connection.
    launcher.website_available()
    request=json.loads((stage/'website.json').read_text())
    scan.warnings=['Passive review of captured unauthenticated responses only; no application JavaScript or active attacks run.',
                   'Runtime-loaded assets, private backend source and resources outside the exact origin were not assessed.',
                   'Response bodies and sensitive values are omitted from evidence; exposed credentials still require rotation.']
    for tool in scan.tools:
        if tool.required: tool.status='queued'; tool.started_at=None
    if not lifecycle.progress(scan,token): raise RuntimeError('job_cancelled')
    capture_started=time.monotonic()
    observed=capture_fn(request['target_url'],active=active)
    if not active(): raise RuntimeError('job_cancelled')
    entries=observed['entries']
    resources={entry['url']:{'key':f'web-{index:04d} {display(entry["url"])}','display':display(entry['url'])} for index,entry in enumerate(entries)}
    scan.coverage.exclusions=[Exclusion.model_validate(item) for item in observed['exclusions']]
    scan.warnings.append(f'Observed {observed["requests"]} GET requests and {observed["bytes"]} response bytes within the shared capture budget.')
    if not observed['complete']: scan.warnings.append('Capture is incomplete. Review omissions before drawing absence conclusions.')
    asset_dir=Path(tempfile.mkdtemp(prefix='assets-',dir=stage))
    mapping={}
    text_incomplete=False
    for index,entry in enumerate(entries):
        if entry.get('mime') not in TEXT_TYPES|{'text/html','application/xhtml+xml'}: continue
        try:
            content=entry['body'].decode('utf-8')
            if '\x00' in content: raise ValueError
        except (ValueError,UnicodeDecodeError):
            text_incomplete=True
            scan.coverage.exclusions.append(Exclusion(resource_key=resources[entry['url']]['key'],reason='non_utf8_text_not_secret_scanned'))
            continue
        name=f'asset-{index:04d}.txt'
        (asset_dir/name).write_bytes(entry['body']); mapping[name]=resources[entry['url']]
    write_har(entries,stage/'capture.har')
    fingerprints=[implementation()]
    for name in ('asset_secrets','zap'):
        if not active(): raise RuntimeError('job_cancelled')
        tool=next(item for item in scan.tools if item.name==name)
        tool.status='running'; tool.started_at=datetime.now(timezone.utc)
        tool.coverage.required_count=len(resources) if name=='zap' else len(mapping)
        tool.coverage.completed_count=0; tool.coverage.scope_complete=False
        tool.version=launcher.versions.get('gitleaks' if name=='asset_secrets' else name)
        tool.image_digest=launcher.images.get('gitleaks' if name=='asset_secrets' else name)
        if not lifecycle.progress(scan,token): raise RuntimeError('job_cancelled')
        try:
            if not entries or (name=='asset_secrets' and not mapping): raise ValueError('no_observed_text')
            remaining=180 if name=='zap' else min(30,capture_started+60-time.monotonic())
            if remaining<=0: raise TimeoutError('asset_stage_timeout')
            raw=launcher.scan(name,stage if name=='zap' else asset_dir,scan.scan_id,active=active,timeout=remaining)
            if name=='zap':
                findings,rule_hash=zap_findings(raw,resources)
                inspected=[resource['key'] for resource in resources.values()]
            else:
                source_findings,_=normalize('gitleaks',raw,asset_dir)
                findings=asset_findings(source_findings,mapping); rule_hash=fingerprint()
                inspected=[resource['key'] for resource in mapping.values()]
            fingerprints.append(rule_hash)
            tool.rules_fingerprint=rule_hash; tool.coverage.rules_fingerprint=rule_hash
            tool.coverage.inspected=inspected; tool.coverage.completed_count=len(inspected)
            tool.coverage.exclusions=scan.coverage.exclusions
            tool.coverage.scope_complete=observed['complete'] and (name=='zap' or not text_incomplete)
            tool.status='complete'
            if len(scan.findings)+len(findings)>1000:
                tool.coverage.scope_complete=False; scan.warnings.append('Finding cap reached; report is incomplete.')
            scan.findings.extend(findings[:max(0,1000-len(scan.findings))])
        except Exception as exc:
            tool.status='timed_out' if isinstance(exc,TimeoutError) else 'failed'
            tool.reason='passive_stage_incomplete'
            tool.error=SafeError(code=tool.reason,message='A required passive review stage did not complete.',request_id=scan.scan_id,details={})
            scan.warnings.append(f'{name} did not complete; no clean-result conclusion is available for that stage.')
        tool.finished_at=datetime.now(timezone.utc)
        scan.coverage.completed_count=sum(item.status=='complete' and item.coverage.scope_complete for item in scan.tools if item.required)
        if not lifecycle.progress(scan,token): raise RuntimeError('job_cancelled')
    scan.coverage.inspected=sorted({key for item in scan.tools if item.required for key in item.coverage.inspected})
    scan.coverage.rules_fingerprint=hashlib.sha256(':'.join(fingerprints).encode()).hexdigest() if fingerprints else None
    scan.coverage.scope_complete=scan.coverage.completed_count==2
    scan.status='complete' if scan.coverage.scope_complete else ('partial' if scan.findings or scan.coverage.inspected else 'failed')
    scan.finished_at=datetime.now(timezone.utc)
    scan.repair=repair_for(scan)
    if scan.status=='failed': scan.error=SafeError(code='website_review_failed',message='Website review did not complete.',request_id=scan.scan_id,details={})
    lifecycle.publish(scan,token)
    return Scan.model_validate(scan.model_dump())
