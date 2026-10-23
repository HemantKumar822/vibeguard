"""Source job orchestration; only sanitized contract objects can be published."""
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from backend.adapters.source import fingerprint, normalize
from backend.adapters.intake import safe_paths
from backend.core.contracts import CodebaseMetadata, SafeError
from backend.core.repair import repair_for


def execute(scan, lifecycle, launcher, token):
    stage=lifecycle.store.staging/scan.scan_id
    manifest=json.loads((stage/'manifest.json').read_text())
    metadata=CodebaseMetadata(mode='codebase',authorization_confirmed=True,files=manifest['files'])
    safe_paths(metadata)
    tree=Path(tempfile.mkdtemp(prefix='trusted-',dir=stage))
    try:
        for item in metadata.files:
            original=stage/item.part_id
            if original.is_symlink() or not original.is_file(): raise ValueError('invalid_manifest')
            target=tree/item.relative_path
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(original,target)
        rules=fingerprint()
        scan.warnings=['Selected static rules only; authorization and exploitability require human review.',
                       'Evidence omits source literals. Public browser keys are not automatically private secrets.']
        if scan.coverage.exclusions: scan.warnings.append('Some submitted files were excluded; inspect the inventory and reasons.')
        truncated=False
        for tool in scan.tools:
            if tool.required: tool.status='queued'; tool.started_at=None
        for tool in [item for item in scan.tools if item.required]:
            if not lifecycle.active(scan.scan_id,token): raise RuntimeError('job_cancelled')
            tool.status='running'; tool.started_at=datetime.now(timezone.utc)
            tool.rules_fingerprint=rules
            tool.coverage.rules_fingerprint=rules
            tool.coverage.required_count=len(scan.accepted_files)
            tool.coverage.completed_count=0
            tool.coverage.inspected=[]
            tool.coverage.scope_complete=False
            tool.version=launcher.versions.get(tool.name)
            tool.image_digest=getattr(launcher,'images',{}).get(tool.name)
            if not lifecycle.progress(scan,token): raise RuntimeError('job_cancelled')
            try:
                raw=launcher.scan(tool.name,tree,scan.scan_id,active=lambda: lifecycle.active(scan.scan_id,token))
                findings,inspected=normalize(tool.name,raw,tree)
                inspected=scan.accepted_files if inspected is None else inspected
                inspected=sorted(set(inspected)&set(scan.accepted_files))
                tool.coverage.inspected=inspected
                expected=([name for name in scan.accepted_files if Path(name).suffix.lower() in {'.js','.jsx','.ts','.tsx','.mjs','.cjs'}]
                          if tool.name=='semgrep' else scan.accepted_files)
                tool.coverage.required_count=len(expected)
                tool.coverage.completed_count=len(set(inspected)&set(expected))
                tool.coverage.scope_complete=set(expected).issubset(inspected)
                tool.status='complete'
                remaining=1000-len(scan.findings)
                if len(findings)>remaining: truncated=True
                scan.findings.extend(findings[:remaining])
                if not tool.coverage.scope_complete: scan.warnings.append(f'{tool.name} did not inspect all expected files.')
            except Exception as exc:
                code='tool_timeout' if isinstance(exc,TimeoutError) else 'source_check_failed'
                tool.status='timed_out' if isinstance(exc,TimeoutError) else 'failed'
                tool.reason=code
                tool.error=SafeError(code=code,message='A required source check did not complete.',request_id=scan.scan_id,details={})
                scan.warnings.append(f'{tool.name} did not complete. No absence conclusion is available for that tool.')
            tool.finished_at=datetime.now(timezone.utc)
            scan.coverage.completed_count=sum(t.status=='complete' and t.coverage.scope_complete for t in scan.tools if t.required)
            if not lifecycle.progress(scan,token): raise RuntimeError('job_cancelled')
        scan.coverage.completed_count=sum(t.status=='complete' and t.coverage.scope_complete for t in scan.tools if t.required)
        scan.coverage.inspected=sorted({path for t in scan.tools if t.required for path in t.coverage.inspected})
        scan.coverage.rules_fingerprint=rules
        scan.coverage.scope_complete=scan.coverage.completed_count==2 and not truncated
        if truncated: scan.warnings.append('Finding limit reached; report coverage is incomplete.')
        scan.status='complete' if scan.coverage.scope_complete else ('partial' if scan.findings or scan.coverage.completed_count else 'failed')
        scan.finished_at=datetime.now(timezone.utc)
        scan.repair=repair_for(scan,budget_seconds=max(0, min(15, 300-(datetime.now(timezone.utc)-scan.started_at).total_seconds())) if scan.started_at else 0)
        # Large inventories/evidence must not silently turn into a clean result
        # or exceed the public report boundary. Retain explicit partial coverage.
        if len(scan.model_dump_json().encode())>5*1024*1024:
            scan.status='partial'; scan.coverage.scope_complete=False
            scan.warnings.append('Report bound reached; resource manifests and evidence are incomplete.')
            scan.coverage.inspected=scan.coverage.inspected[:1000]
            for tool in scan.tools:
                if tool.required:
                    tool.coverage.inspected=tool.coverage.inspected[:1000]
                    tool.coverage.scope_complete=False
            scan.coverage.completed_count=0
            while scan.findings and len(scan.model_dump_json().encode())>5*1024*1024:
                scan.findings=scan.findings[:len(scan.findings)//2]
            scan.repair=repair_for(scan,budget_seconds=0)
        if scan.status=='failed': scan.error=SafeError(code='source_checks_failed',message='Required source checks failed.',request_id=scan.scan_id,details={})
        lifecycle.publish(scan,token)
        return scan
    finally:
        shutil.rmtree(tree)
