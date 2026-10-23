"""Generate reviewable team story/epic documents from the canonical planning backlog.

Local files only. Does not initialize Git, contact GitHub, assign people or publish.
Dependencies guide integration and acceptance; coordinated parallel work is permitted.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_bmad-output'
PLAN = OUT / 'planning-artifacts'
STORIES = OUT / 'implementation-artifacts'
ISSUES = OUT / 'github-issues'

# Human-facing explanation and bounded tasks; acceptance remains canonical.
# summary, proposed owner role, implementation tasks, exclusions, verification.
DETAILS = {
 '1.1': (
  'Give the team a working development starting point and one shared API shape before separate feature work begins.',
  'Full-stack / platform',
  ['Create the React/TypeScript starter and minimal FastAPI health endpoint, then record compatible dependency locks.',
   'Turn API-CONTRACT v1 into backend models, a generated OpenAPI snapshot, frontend types and labeled boundary fixtures.',
   'Check the actual scanner/container runtime and record tool versions and immutable image digests; report missing prerequisites honestly.',
   'Add and run the real build/type/schema checks; replace planning-only setup notes with the commands that now work.'],
  ['No real upload, scanner integration, report UI, queue or website enforcement yet.', 'Do not create every future database table or advertise fixture data as scanner output.'],
  ['Build/type-check the starter and request the real health endpoint.', 'Validate every required boundary fixture against the generated schema.', 'Record scanner startup/version results, locks and runtime prerequisites.']),
 '1.2': (
  'Let a developer submit a source tree without losing directory structure or letting unsafe files reach a scanner.',
  'Backend / intake',
  ['Implement the source-tree multipart contract with permission and model-sharing fields; keep sharing off by default.',
   'Preserve safe relative paths and stream aggregate/file limits instead of buffering an unlimited upload.',
   'Create only session/submission records needed here; return the accepted inventory and explicit exclusions.',
   'Handle invalid, unsupported and browser-limited input with safe actionable errors.'],
  ['No archive-only replacement for required tree input.', 'No running uploaded code, installs or scanner commands in the intake handler.'],
  ['Submit a multi-directory JS/TS fixture and verify its paths/inventory.', 'Exercise traversal, links, duplicate/case collisions and malformed part mappings.', 'Test each configured limit at its boundary and one value over it.']),
 '1.3': (
  'Make accepted work private, bounded and observable, including when workers crash or a user deletes a scan.',
  'Backend / worker lifecycle',
  ['Add the core-owned persisted queue, transactional claim, tool/scan transitions and deadline handling.',
   'Launch restricted workers through the trusted launcher with read-only source, bounded scratch and no source-worker network.',
   'Enforce ownership, CSRF and idempotency; do not grant API/scanner jobs container-daemon access.',
   'Implement tombstone-first deletion, late-write prevention, expiry, crash recovery and truthful cleanup operations.'],
  ['No distributed Redis/Celery queue or public multiuser deployment.', 'No claim that a container exists implies its security limits are enforced.'],
  ['Check one-job/queue caps, duplicate/different-payload idempotency and terminal deadlines.', 'Attempt cross-session access and missing/invalid CSRF.', 'Crash a worker/coordinator and delete running/completed scans; verify no late resurrection or hidden cleanup failure.']),
 '1.4': (
  'Produce real source findings that tell the developer where to look while keeping credential values out of reports and logs.',
  'Security / scanner adapters',
  ['Integrate trusted Gitleaks and selected Semgrep rules with explicit process/report outcome handling.',
   'Build labeled vulnerable/control cases for credentials, unsafe input, configuration and selected access-check candidates.',
   'Normalize typed findings and confidence, then redact before storage, logging, UI or model boundaries.',
   'Pin reviewed rule/config versions, verify distribution rights and prevent submitted suppressions from silently disabling required checks.'],
  ['No comprehensive authorization/exploitability claim.', 'No external AI, dependency scanner or raw vendor-output persistence.'],
  ['Match expected rule IDs and actual file/line on labeled cases; record misses and false alarms.', 'Use a public-browser-key control and fake private credentials.', 'Test malformed output, timeout, findings-bearing exit codes, malicious suppression and raw-value leakage on outward surfaces.']),
 '1.5': (
  'Give the developer a usable source-review workspace and a repair prompt they can act on before AI integration exists.',
  'Frontend / source workflow',
  ['Implement source submission/progress, coverage, filters, finding selection/detail and the deterministic repair panel using the UX tokens.',
   'Show confidence, real source locations, incomplete checks and separate revoke/rotate guidance.',
   'Add safe clipboard fallback, reconnect-to-existing-scan behavior and confirmed deletion UI.',
   'Verify keyboard focus, narrow layout, contrast and reduced motion on the actual rendered interface.'],
  ['No chatbot, fake score, fabricated scan percentage or AI requirement.', 'No comparison UI until the comparison story.'],
  ['Run the source fixture through the live API, filter/select findings and copy the sanitized prompt.', 'Exercise clean/partial/filter-empty/disconnected/clipboard/delete-failure states.', 'Check keyboard, 360px viewport, 200% zoom and reduced motion; inspect hidden accessible output for raw secrets.']),
 '2.1': (
  'Review exactly one public repository revision through the existing source pipeline, without asking the user to upload it manually.',
  'Backend / repository adapter',
  ['Parse only the approved public GitHub identity/ref and resolve a full commit through fixed provider endpoints.',
   'Download a bounded snapshot with actual-destination/redirect checks and the shared safe extractor.',
   'Feed the validated tree to the existing source scanners and record commit/inventory/coverage.'],
  ['No arbitrary git clone arguments, hooks, submodule/LFS following, private credentials or history scan.', 'Do not bypass source intake limits because the source came from GitHub.'],
  ['Compare seeded findings for an uploaded tree and equivalent repository commit.', 'Reject credential-bearing/unsupported URLs, missing refs and unsafe redirects.', 'Test malicious archive paths, expansion/size limits and retrieval timeouts.']),
 '2.2': (
  'Let the developer choose Repository mode and understand which commit produced the findings in the same visual workspace.',
  'Frontend / repository workflow',
  ['Connect the repository/ref form to real retrieval and shared report endpoints.',
   'Show requested/ref-resolved commit, actual progress and ordinary source evidence/repair guidance.',
   'Handle mode switching, refresh, missing ref and denied retrieval without duplicate work.'],
  ['No private-repository login or history interface.', 'No separate repository-only report schema or dashboard.'],
  ['Complete a live public-repository scan and inspect commit-attributed evidence.', 'Repeat failed/missing-ref submission and correct it in place.', 'Switch modes and reconnect; verify accepted scan identity is preserved.']),
 '3.1': (
  'Prove URL scanning cannot reach internal systems or exceed the approved request/byte/time scope before enabling arbitrary targets.',
  'Security / networking',
  ['Create the dedicated ZAP/asset network path with no bypass route and no public ZAP control API.',
   'Enforce actual public destinations at connection time, including DNS changes, redirects and IPv4/IPv6 edge cases.',
   'Enforce shared pre-send request and response-byte/time budgets under safety-v1.',
   'Document the tested enforcement mechanism and fail closed when runtime capability is missing.'],
  ['No active attacks, authenticated sessions or broader-origin crawling.', 'No hostname precheck or permission checkbox presented as network isolation.'],
  ['Demonstrate allowed authorized-origin traffic through the selected runtime.', 'Block internal/reserved/metadata/mapped-IPv6/rebinding/redirect cases and direct egress.', 'Exceed each shared crawl/network budget and verify termination plus incomplete coverage.']),
 '3.2': (
  'Turn a real ZAP baseline into understandable deployment findings, without treating alerts or a failed crawl as successful security verification.',
  'Security / ZAP adapter',
  ['Run the pinned passive/baseline profile through the enforced network path.',
   'Normalize real alert IDs, sanitized web locations and assessed/excluded resources.',
   'Distinguish WARN/FAIL finding-bearing exits from execution/JSON/timeout failures.'],
  ['No active ZAP scan, authenticated crawl or private backend-source inference.', 'No broad exposed-secret promise from stock ZAP alone.'],
  ['Scan a controlled vulnerable deployment and assert actual alert/location evidence.', 'Scan corrected/clean variants and retain any additional observed warnings.', 'Test finding exits, broken/truncated JSON and timeout; verify truthful partial/failed coverage.']),
 '3.3': (
  'Detect private-credential candidates in browser-visible text assets and show the actual asset location with values masked.',
  'Security / asset analysis',
  ['Collect only bounded same-origin linked text assets through the same enforced egress/budget controls.',
   'Run the trusted secret detector on temporary text and map safe evidence back to asset URLs/real text lines.',
   'Record exclusions and clean up raw asset/temporary scanner data before outward persistence.'],
  ['No JavaScript execution, unlimited asset recursion or cross-origin harvesting.', 'Do not call unvisited/runtime-loaded assets assessed or classify all public keys as secrets.'],
  ['Find a fake private key in a served asset with masked URL/evidence.', 'Use public-key, cross-origin and runtime-only controls to verify confidence/exclusion behavior.', 'Exercise shared limits and sanitizer failure; inspect reports/logs/model inputs/clipboard surfaces for raw values.']),
 '3.4': (
  'Make Website URL review usable in the shared workspace, with separate ZAP and asset coverage and actionable deployment guidance.',
  'Frontend / website workflow',
  ['Connect authorized URL submission and real ZAP/asset progress to the common UI.',
   'Display typed web evidence, passive scope, visited/excluded resources and a deterministic repair prompt.',
   'Implement blocked/partial/clean/missing-asset recovery states without inventing source files.'],
  ['No new website-only data contract, chat surface or active-scan control.', 'A visible failure does not satisfy successful URL-mode delivery.'],
  ['Complete a live controlled website scan and copy guidance grounded in actual web evidence.', 'Exercise blocked destinations, partial crawl, no alerts and asset failure.', 'Verify the UI never implies access to private backend code or a secret-free verdict from unvisited assets.']),
 '4.1': (
  'Offer clearer AI-assisted explanations only when the user chooses sharing, while keeping evidence and the repair prompt usable if the model fails.',
  'Backend / AI integration',
  ['Connect a server-configured provider behind the bounded explanation port and explicit per-submission opt-in.',
   'Send sanitized structured findings only and validate returned IDs/locations/output shape.',
   'Keep core-owned master prompt composition and deterministic fallback, including all relevant human rotation actions.'],
  ['No model-controlled scanning, commands, new findings or raw-source upload.', 'No automatic retries or silent widening of sharing/size limits.'],
  ['Assert no model request when sharing is off.', 'Inspect the enabled request for bounded sanitized evidence and test valid explanation output.', 'Test timeout/invented IDs/locations/invalid response/prompt injection and confirm usable honest fallback.']),
 '4.2': (
  'Execute the checks again for corrected input and classify changes only where the new observations are genuinely comparable to the baseline.',
  'Backend / comparison',
  ['Create owned same-mode repeat scans with recorded lineage and new revision/observation.',
   'Prototype and test the source scan-repair-rescan loop after 1.5; retain all final dependencies and all-mode acceptance before completing this story.',
   'Implement coverage/rule/policy-aware matching using safe structural context instead of line-only or secret-derived public IDs.',
   'Return the four comparison classifications, reasons, paired evidence and retained human actions.'],
  ['No stale-result reuse or cross-mode clearing of source findings.', 'No verified_fixed label without a separate repeatable behavior-proof test.'],
  ['Run actual corrected repeats for codebase, repository and website modes.', 'Test shifted lines, stable matches, removed/new findings and ambiguous duplicates.', 'Test failed checks, lost pages, changed versions/policy, wrong lineage and inaccessible/deleted baselines.']),
 '4.3': (
  'Help the developer understand before/after evidence and remaining uncertainty, instead of showing a misleading fixed-count celebration.',
  'Frontend / comparison workflow',
  ['Implement same-mode rescan entry/progress while preserving baseline context.',
   'Display four labeled classifications with reasons, both revisions/observations and paired coverage/evidence.',
   'Preserve focus/selection and accessible narrow stacking with deliberate recovery for failed repeats.',
   'Verify comparison with external AI disabled or unavailable; optional AI integration is not a prerequisite.'],
  ['No UI-created match/classification algorithm or unsupported verified-fixed badge.', 'No loss of rotation reminders after a credential warning disappears.'],
  ['Walk UJ-3 using live repeat scans and inspect both observations.', 'Exercise failed repeat, changed coverage, expired baseline and disconnect.', 'Check keyboard navigation, narrow layout and retained baseline state without duplicate work.']),
 '5.1': (
  'Give evaluators repeatable evidence that all required modes and safety cases work on the actual demo machine, including what the tool misses.',
  'QA / security validation',
  ['Run a per-mode vulnerable/corrected/clean matrix: all four categories across the product, real passive alerts and visible-asset secrets for websites, with unsupported cells explained.',
   'Exercise hostile intake/network/session/deletion/crash/model/sanitization cases against the actual implementation.',
   'Record sanitized expected/observed outputs, versions, coverage, runtimes and guidance utility without unsupported percentages.'],
  ['No mock output substituted for a real scan or error screen counted as mode completion.', 'No live secrets or unauthorized target testing.'],
  ['Demonstrate three successful required-mode loops with genuine rescans.', 'Report issue-occurrence true/false positives and false negatives with valid denominators.', 'Document failed safety criteria as release blockers and keep all outward evidence sanitized.']),
 '5.2': (
  'Make the implemented workflow accessible and rehearsable so teammates can present it without hiding broken or incomplete states.',
  'Frontend / QA / demo operations',
  ['Test every journey and state against the rendered UX contracts, fixing meaningful recovery/accessibility defects.',
   'Write the actual operator setup, run, demo, recovery and cleanup guide from observed commands.',
   'Rehearse from a clean start on the demonstration machine and document remaining limitations.'],
  ['No optional feature expansion, decorative animation sprint or fabricated polished success.', 'Do not assert accessibility from token contrast calculations alone.'],
  ['Exercise keyboard, screen-reader/status behavior where available, 360px viewport, 200% zoom and reduced motion.', 'Test all empty/partial/denied/expired/clipboard/folder/deletion states with their recovery.', 'Follow the operator guide end to end and record real demo evidence and limitations.']),
}


def slug(title: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')


def canonical_story_blocks(text: str) -> dict[str, str]:
    return {f'{m[1]}.{m[2]}': m[4] for m in re.finditer(
        r'^### Story (\d+)\.(\d+): ([^\n]+)\n(.*?)(?=^### Story |^## Epic |\Z)', text, re.M | re.S)}


def main() -> None:
    backlog = json.loads((PLAN / 'backlog.json').read_text(encoding='utf-8-sig'))
    publication = ISSUES / 'publication.json'
    if publication.exists() and json.loads(publication.read_text(encoding='utf-8')).get('status') == 'published':
        raise RuntimeError('Issues are published; reconcile local documents and remote issues explicitly instead of regenerating the publication manifest')
    blocks = canonical_story_blocks((PLAN / 'epics.md').read_text(encoding='utf-8-sig'))
    stories = backlog['stories']
    by_id = {s['id']: s for s in stories}
    assert set(by_id) == set(DETAILS) == set(blocks), 'Story definitions drifted; reconcile before rendering'
    filenames = {s['id']: s['id'].replace('.', '-') + '-' + slug(s['title']) + '.md' for s in stories}
    epic_names = {e['id']: f"epic-{e['id']:02d}-{slug(e['title'])}.md" for e in backlog['epics']}
    blockers = {sid: [s['id'] for s in stories if sid in s['depends_on']] for sid in by_id}
    prd = PLAN / 'prds/prd-TechFest-2026-10-23/prd.md'
    labels = dict(re.findall(r'^\*\*(FR-\d+) — ([^\n]+?)\.\*\*', prd.read_text(encoding='utf-8-sig'), re.M))
    STORIES.mkdir(parents=True, exist_ok=True)
    (ISSUES / 'epics').mkdir(parents=True, exist_ok=True)

    def link(sid: str) -> str:
        return f"[Story {sid}: {by_id[sid]['title']}]({filenames[sid]})"

    for story in stories:
        sid = story['id']; path = STORIES / filenames[sid]
        if path.exists() and re.search(r'^status: (in-progress|review|done)$', path.read_text(encoding='utf-8-sig'), re.M):
            raise RuntimeError(f'{sid} has implementation activity; do not overwrite its record')
        summary, role, tasks, exclusions, checks = DETAILS[sid]
        canonical_acs = [l for l in blocks[sid].splitlines() if l.startswith('- **Given**')]
        assert canonical_acs == story['acceptance_criteria'], f'{sid}: stale backlog JSON'
        user_story = ' '.join(l.strip() for l in blocks[sid].splitlines() if l.startswith(('As a ', 'I want ', 'So that '))).replace(', So that ', ', so that ')
        deps = '\n'.join('- '+link(d) for d in story['depends_on']) or '- None. This is the starting story.'
        next_work = '\n'.join('- '+link(d) for d in blockers[sid]) or '- No direct successor; completion contributes to its epic acceptance.'
        requirements = '\n'.join('- **'+rid+' — '+labels[rid]+'**' for rid in re.findall(r'(?<![\w-])FR-\d+', story['requirements']))
        req_paths = '../planning-artifacts'
        body = [
            '---', f"story_id: '{sid}'", f"epic: {story['epic']}", 'status: ready-for-dev',
            'prepared: true', 'approval: pending-user-review', 'assignee: unassigned', f'owner_role: {json.dumps(role)}',
            'priority: P0', f"depends_on: {json.dumps(story['depends_on'])}", f"blocks: {json.dumps(blockers[sid])}",
            'source: ../planning-artifacts/epics.md', '---', '', f"# Story {sid} · {story['title']}", '',
            f"> **Epic {story['epic']}** · Required scope · Proposed owner role: **{role}** · Actual assignee: **unassigned**", '',
            '## Summary', '', summary, '', '## User story', '', user_story, '',
            '## Requirements and source of truth', '', requirements, '',
            f"**All references:** {story['requirements']}", '',
            f"- [Canonical backlog]({req_paths}/epics.md) and [PRD]({req_paths}/prds/prd-TechFest-2026-10-23/prd.md).",
            f"- [Architecture decisions]({req_paths}/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract]({req_paths}/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1]({req_paths}/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).",
            f"- [Visual contract]({req_paths}/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract]({req_paths}/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).", '',
            '## Dependencies', '', '**Depends on — coordination guidance:**', '', deps, '', '**Downstream work:**', '', next_work, '',
            'Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.', '',
            '## In scope / implementation checklist', '', *['- [ ] '+task for task in tasks], '',
            '## Out of scope', '', *['- '+item for item in exclusions], '',
            '## Acceptance criteria', '',
            *[f"- [ ] **AC-{i}** {ac[2:]}" for i, ac in enumerate(canonical_acs, 1)], '',
            '## Verification plan', '', *['- [ ] '+check for check in checks], '',
            'Record the actual commands, observed results and sanitized evidence in the PR and implementation record. Use commands introduced by the real scaffold; no nonexistent build/test command is asserted here.', '',
            '## Definition of done', '',
            '- [ ] All acceptance criteria satisfied, including relevant failure cases.',
            '- [ ] Required predecessors complete; one accountable assignee recorded.',
            '- [ ] Appropriate automated/manual checks run with observed results; limitations explicit.',
            '- [ ] Contract/types/fixtures/docs updated together when changed.',
            '- [ ] No secrets, runtime scan data or local agent installations in the diff.',
            '- [ ] Reviewed PR linked and story/sprint/issue status reconciled.', '',
            '## Implementation record', '', 'Not started. Record PR, actual commands/results, sanitized evidence and remaining limitations here during implementation.', '',
            f"[Parent epic](../github-issues/epics/{epic_names[story['epic']]}) · [All stories](README.md)", ''
        ]
        path.write_text('\n'.join(body), encoding='utf-8')

    manifest_items = []
    (ISSUES/'stories').mkdir(exist_ok=True)
    for epic in backlog['epics']:
        eid = epic['id']; children = [s for s in stories if s['epic'] == eid]
        child_ids={s['id'] for s in children}
        external=sorted({d for s in children for d in s['depends_on'] if d not in child_ids},key=lambda d:tuple(map(int,d.split('.'))))
        grouped=[]
        for label,pattern in [('Functional requirements',r'(?<![\w-])FR-\d+'),('Quality requirements',r'NFR-\d+'),('UX requirements',r'UX-DR\d+'),('Architecture decisions',r'AD-\d+')]:
            values=sorted({v for s in children for v in re.findall(pattern,s['requirements'])},key=lambda v:int(re.search(r'\d+',v)[0]))
            grouped.append(f"- **{label}:** {', '.join(values) or 'See child-story contracts' }.")
        prerequisite_links=', '.join(f"[Story {d}](../../implementation-artifacts/{filenames[d]})" for d in external) or 'None; this epic establishes the starting workflow.'
        body = [f"# Epic {eid} · {epic['title']}", '', '## User outcome', '',
                next(line for line in (PLAN/'epics.md').read_text(encoding='utf-8-sig').split(f"### Epic {eid}: ",1)[1].splitlines()[1:] if line.strip()), '',
                '## Requirements and governing decisions', '', *grouped, '',
                '## Delivery stories', '',
                *[f"- [ ] [Story {s['id']}: {s['title']}](../../implementation-artifacts/{filenames[s['id']]})" for s in children], '',
                '## Dependencies and ownership', '',
                '**Earlier-story prerequisites:** '+prerequisite_links, '',
                'Assign one accountable owner per child story. Use each story’s dependency links to coordinate parallel work and integration. Claim actual owners on GitHub; preserve acceptance before closing work.', '',
                '## Epic acceptance', '',
                '- [ ] Every linked child story meets its acceptance criteria with reviewed evidence.',
                '- [ ] The user outcome works end to end on real authorized inputs.',
                '- [ ] Required failure/recovery, privacy and safety boundaries are exercised.',
                '- [ ] Evidence and metrics state actual coverage and limitations.',
                '- [ ] Relevant documentation and sprint/GitHub statuses agree.', '',
                '## Scope rules', '',
                'Preserve the required codebase, repository and ZAP website flow, masked evidence, repair guidance and genuine rescans. Optional features never replace required safety or a required mode. No claim of completion from planning documents alone.', '',
                '[Canonical epic backlog](../../planning-artifacts/epics.md) · [Team story board](../README.md)', '']
        path = ISSUES/'epics'/epic_names[eid]; path.write_text('\n'.join(body),encoding='utf-8')
        manifest_items.append({'key':f'epic-{eid}','kind':'epic','title':f"[Epic {eid}] {epic['title']}",'body_file':path.relative_to(ROOT).as_posix(),'labels':['type:epic','priority:p0'],'children':[s['id'] for s in children]})

    board = ['# Team story board', '', '**5 epics · 16 prepared stories · implementation not started.**', '',
             'Each story explains the outcome, scope, requirements, dependencies, acceptance and verification. Story 1.1 is the recommended foundation; all GitHub issues remain open for coordinated parallel work. `ready-for-dev` means its handoff exists; it does not mean its prerequisites are complete.', '',
             '## Stories and dependencies', '', '| Story | Proposed owner role | Depends on | Downstream work |', '| --- | --- | --- | --- |']
    for story in stories:
        sid=story['id']; role=DETAILS[sid][1]
        deps=', '.join(story['depends_on']) or 'None — start here'
        successors=', '.join(blockers[sid]) or '—'
        board.append(f"| [{sid} · {story['title']}](../implementation-artifacts/{filenames[sid]}) | {role} | {deps} | {successors} |")
        handoff=STORIES/filenames[sid]
        draft=ISSUES/'stories'/f"story-{sid.replace('.', '-')}.md"
        issue_body=handoff.read_text(encoding='utf-8').split('---',2)[2].lstrip()
        issue_body=issue_body.split('## Implementation record',1)[0].rstrip()
        def rebase(match: re.Match[str]) -> str:
            target=match[2]
            if target.startswith(('https://','http://','#')):
                return match[0]
            resolved=(handoff.parent/target).resolve()
            relative=os.path.relpath(resolved,draft.parent).replace(os.sep,'/')
            return f'[{match[1]}]({relative})'
        issue_body=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',rebase,issue_body)
        issue_body+=f"\n\n[Implementation handoff](../../implementation-artifacts/{filenames[sid]})\n"
        draft.write_text(issue_body,encoding='utf-8')
        manifest_items.append({'key':sid,'kind':'story','parent':f"epic-{story['epic']}",'title':f"[Story {sid}] {story['title']}",'body_file':draft.relative_to(ROOT).as_posix(),'source_file':handoff.relative_to(ROOT).as_posix(),'depends_on':story['depends_on'],'blocks':blockers[sid],'labels':['type:story','priority:p0'],'assignee':None,'suggested_owner_role':role})
    board += ['', '## Epics', '', *[f"- [Epic {e['id']} · {e['title']}](epics/{epic_names[e['id']]})" for e in backlog['epics']], '',
              '## Parallel work', '', 'After source intake/lifecycle prerequisites, repository retrieval and the high-risk ZAP network gate can proceed separately. AI integration can begin after the source report. Respect the exact dependency lists; coordinate changes to shared schema/state modules with one owner.', '',
              '## How to use this board', '',
              '1. Claim a story and coordinate its dependencies; proposed owner roles are guidance, not assigned people.',
              '2. Read its scope and governing contracts; create a focused branch.',
              '3. Complete its acceptance and verification; record real results in a reviewed PR.',
              '4. Update the [sprint tracker](../implementation-artifacts/sprint-status.yaml) and, once published, the actual GitHub issue. Do not maintain a competing JSON progress board.', '',
              '## Publication status', '', '**Not published.** [manifest.json](manifest.json) is a derived draft import package, not remote issue state. No repository, commit, issue number or assignee is invented. Before later publication, resolve local file links to verified repository blob URLs, replace dependency IDs with returned real issue URLs and establish supported parent/dependency relationships. See [repository setup](../../docs/REPOSITORY_SETUP.md).', '']
    (ISSUES/'README.md').write_text('\n'.join(board),encoding='utf-8')
    (STORIES/'README.md').write_text('# Story handoffs\n\n[Open the team story board](../github-issues/README.md) for all 16 stories, dependencies and suggested owner roles.\n\nThese files are prepared implementation handoffs. Their acceptance comes from [epics.md](../planning-artifacts/epics.md); no implementation is complete. `ready-for-dev` means prepared, while dependencies guide integration and completion. Story 1.1 is the recommended foundation; all GitHub issues remain open for coordinated parallel work.\n\nUse [sprint-status.yaml](sprint-status.yaml) for current implementation state. Fill a story’s implementation record during the build; do not regenerate over an active story.\n',encoding='utf-8')
    (ISSUES/'manifest.json').write_text(json.dumps({'publication_status':'not-published','canonical_backlog':'_bmad-output/planning-artifacts/epics.md','items':manifest_items},indent=2),encoding='utf-8')
    (ISSUES/'labels.json').write_text(json.dumps([
        {'name':'type:epic','color':'5319E7','description':'User outcome delivered by linked stories'},
        {'name':'type:story','color':'1D76DB','description':'Bounded implementation story with acceptance'},
        {'name':'priority:p0','color':'B60205','description':'Required scope; dependency order still controls eligibility'}],indent=2),encoding='utf-8')
    # Match BMAD's story-file floor, preserving all actual progress states.
    tracker=STORIES/'sprint-status.yaml'
    content=tracker.read_text(encoding='utf-8-sig')
    for filename in filenames.values():
        key=filename.removesuffix('.md')
        content=re.sub(r'(?m)^(  '+re.escape(key)+r': )backlog$',r'\g<1>ready-for-dev',content)
    tracker.write_text(content,encoding='utf-8')
    print('Prepared 16 detailed story handoffs, 5 epic drafts, linked board and publication manifest. No GitHub or project Git operation performed.')


if __name__=='__main__':
    main()
