# Project rules

These are shared team rules, not an agent installation. They apply to code, reviews, documentation and demonstrations.

## Scope and evidence

1. Required intake is **Codebase, Repository and Website URL**; URLs use OWASP ZAP baseline/passive review under the recorded scope assumptions. Do not revert to ZIP-only or silently defer a required mode.
2. Preserve browser-visible credential coverage, masked source/web evidence, one repair prompt and real rescans. A website URL does not expose private backend source.
3. Findings are candidates. Public browser keys are not automatically private secrets; missing local auth is not proof of bypass; absence on rescan is not proof of repair or rotation.
4. Demonstration output must be real. Development fixtures stay visibly labeled; no fake safe score, scan progress, metrics or scanner success.

## Source of truth

- Product intent: [PRD](../_bmad-output/planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- Appearance and interaction: [DESIGN.md](../_bmad-output/planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [EXPERIENCE.md](../_bmad-output/planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).
- Technical invariants: [architecture spine](../_bmad-output/planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../_bmad-output/planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety profile](../_bmad-output/planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- Acceptance/dependencies: [epics.md](../_bmad-output/planning-artifacts/epics.md); individual story handoffs expand this without replacing or weakening its criteria.
- Progress: [sprint-status.yaml](../_bmad-output/implementation-artifacts/sprint-status.yaml), then reconcile with actual GitHub issues after publication. Generated JSON is an import snapshot, not a second live tracker.

If sources conflict, stop the affected implementation choice, record the conflict and update the governing artifact before merging. The user's explicit corrections govern the earlier reference proposals. Do not silently invent a new contract or waive acceptance.

## Engineering guardrails

One core owns Scan state; workers return bounded results and cannot mutate the database. Frontend uses generated public types. Keep source/repository and website worker networking separate. Never execute submitted code, grant scanner/API containers host credentials or Docker control, or let an LLM run tools.

Every boundary must be testable: permissions/session/CSRF, malicious paths/archives, trusted configs, timeout/output/queue limits, actual network destinations, redaction, fallback, deletion/crash cleanup and comparison eligibility. Unknown or failed coverage remains visible.

Keep runtime data outside the checkout. Retain lockfiles, record immutable tool/rule/image versions and document candidate version changes. Use a compatible real build, not version metadata alone, as bootstrap evidence. No live secrets in fixtures or reports.

## Team delivery

One accountable owner per story, dependencies respected, focused PR, teammate review and recorded tests. Avoid simultaneous ownership of the shared schema/state modules. Resolve a boundary together before separate owners extend it. Do not claim a 24-hour commitment without actual team capacity and time remaining.

Optional dependency scanners, private/history access, active/authenticated checks, combined inputs and decorative motion come after the required loop. They never displace safety, truthful evidence or a required mode.
