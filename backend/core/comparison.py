"""Conservative direct-lineage observations. Absence never establishes repair."""
from collections import defaultdict
from urllib.parse import urlsplit
from backend.api.session import IntakeError
from backend.core.contracts import Comparison, ComparisonItem

TERMINAL={'complete','partial','failed'}


def key(finding):
    location=finding.location
    if location.kind=='source':
        return finding.scanner,finding.rule_id,location.path,finding.match_context
    return finding.scanner,finding.rule_id,location.url_redacted,location.part,location.parameter_redacted


def same_input_scope(before,after):
    if before.mode=='repository' and before.input.repository!=after.input.repository: return False
    if before.mode=='website':
        left=urlsplit(before.input.target_redacted or '')
        right=urlsplit(after.input.target_redacted or '')
        return bool(left.netloc) and (left.scheme,left.netloc)==(right.scheme,right.netloc)
    return True


def compatible(before,after,scanner):
    if not same_input_scope(before,after): return False
    if before.policy_id!=after.policy_id or before.policy_fingerprint!=after.policy_fingerprint:
        return False
    left=next(t for t in before.tools if t.name==scanner)
    right=next(t for t in after.tools if t.name==scanner)
    return (left.applicable and right.applicable and all(
        getattr(left,field) is not None and getattr(left,field)==getattr(right,field)
        for field in ('version','image_digest','rules_fingerprint')))


def resource(finding):
    return finding.location.path if finding.location.kind=='source' else finding.location.resource_key


def covered(before,after,finding):
    if not compatible(before,after,finding.scanner): return False,'incompatible_fingerprints'
    if finding.location.kind=='source' and 'uncertain_identifier' in finding.match_context: return False,'uncertain_structural_context'
    if finding.location.kind=='web':
        left=urlsplit(before.input.target_redacted or '')
        right=urlsplit(after.input.target_redacted or '')
        if (left.scheme,left.netloc)!=(right.scheme,right.netloc): return False,'changed_origin'
        # Values deliberately omitted from public URLs cannot establish resource identity.
        if urlsplit(finding.location.url_redacted).query: return False,'redacted_url_identity'
    for scan in (before,after):
        tool=next(t for t in scan.tools if t.name==finding.scanner)
        if (tool.status!='complete' or not tool.coverage.scope_complete or not scan.coverage.scope_complete):
            return False,'incomplete_coverage'
        if resource(finding) not in tool.coverage.inspected: return False,'resource_not_reassessed'
        if tool.coverage.inspected.count(resource(finding))!=1: return False,'ambiguous_resource'
    return True,'comparable_scope'


def compare(before,after):
    if after.baseline_id!=before.scan_id or before.mode!=after.mode or before.status not in TERMINAL or after.status not in TERMINAL:
        raise IntakeError(409,'comparison_not_ready_or_invalid_lineage')
    groups=defaultdict(lambda:[[],[]])
    for side,scan in enumerate((before,after)):
        for finding in scan.findings: groups[key(finding)][side].append(finding)
    items=[]
    def item(left,right,status,reason):
        items.append(ComparisonItem(baseline_finding_id=left.id if left else None,new_finding_id=right.id if right else None,
            status=status,reason_code=reason,baseline_evidence_ref=f'{before.scan_id}/findings/{left.id}' if left else None,
            new_evidence_ref=f'{after.scan_id}/findings/{right.id}' if right else None))
    for left,right in groups.values():
        observed=(left or right)[0]
        safe,reason=covered(before,after,observed)
        ambiguous=len(left)>1 or len(right)>1
        if ambiguous:
            for finding in left: item(finding,None,'unverified','ambiguous_candidates')
            for finding in right: item(None,finding,'unverified','ambiguous_candidates')
        elif left and right:
            web_unsafe=observed.location.kind=='web' and reason in {'redacted_url_identity','changed_origin','ambiguous_resource','resource_not_reassessed'}
            if compatible(before,after,observed.scanner) and not web_unsafe and reason!='uncertain_structural_context':
                item(left[0],right[0],'still_detected','unique_rule_and_structural_location')
            else: item(left[0],right[0],'unverified',reason)
        elif left:
            item(left[0],None,'not_detected' if safe else 'unverified','not_observed_in_comparable_scope' if safe else reason)
        else:
            item(None,right[0],'newly_detected' if safe else 'unverified','new_observation_in_comparable_scope' if safe else reason)
    complete=same_input_scope(before,after) and before.coverage.scope_complete and after.coverage.scope_complete and all(
        compatible(before,after,t.name) for t in before.tools if t.required)
    return Comparison(baseline_id=before.scan_id,new_id=after.scan_id,status='comparable' if complete and all(i.status!='unverified' for i in items) else 'partial',
        baseline_input=before.input,new_input=after.input,baseline_coverage=before.coverage,new_coverage=after.coverage,
        items=items,human_actions=sorted({action for scan in (before,after) for finding in scan.findings for action in finding.human_actions} |
            {action for scan in (before,after) if scan.repair for action in scan.repair.human_actions}))
