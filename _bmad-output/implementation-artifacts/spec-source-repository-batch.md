---
title: Source scanning and public repository review batch
type: feature
created: '2026-10-24'
status: done
route: dispatch
baseline_commit: 56270eeb4386b36da5a1f5171e7c5e1f34f6fb38
context: []
---

<frozen-after-approval>
## Intent
Finish the source workflow (1.4–1.5), then public repository review (2.1–2.2), continuing the already implemented intake/lifecycle. The user explicitly requests a batch through Epic 2, implementation without repeated approval and a single full verification at its end. Retain existing teammate work and avoid redundant review agents.

## Boundaries & Constraints
Always use pinned offline Gitleaks/Semgrep with trusted locally authored rules, bounded memory-only vendor reports, sanitized typed findings and fenced publication. Keep real source outside the checkout. Coordinator owns Docker; API never imports workers. Preserve sessions, CSRF, idempotency and deletion. Repository retrieval uses fixed public GitHub endpoints, connection-pinned public IPs, TLS hostname validation, no redirects and bounded tar extraction. No credentials, clones, hooks, installs, source execution, private repositories or history scanning. Website and AI remain unavailable. Explain narrow access-check candidates without claiming bypasses.

## I/O & Edge-Case Matrix
| Input/state | Behavior |
| --- | --- |
| Fake credential, unsafe eval, disabled TLS, route without local guard | Located candidate findings from real trusted rules; rotation advice for credentials |
| Public browser key / clean protected controls | No automatic private-secret classification |
| Submitted ignore/config/nosem | Cannot disable mandatory checks |
| Bad JSON, tool error, deadline, output cap | Explicit failed/partial coverage; never clean success |
| Deletion or lost lease during tool | Cancel container and refuse late publication |
| Public repository/ref | Resolve full commit, retrieve only that bounded snapshot, reuse source pipeline |
| URL credentials, unsafe ref/IP, redirects, archive links/traversal/bombs | Safe rejection without source execution |
| Report, clipboard failure, reconnect, mode switch | Escaped evidence, filters, manual-copy fallback, preserve accepted identity |
</frozen-after-approval>

## Code Map
- `backend/adapters/intake.py`: reuse safe paths, limits and supported-file classification; opaque part manifest is authoritative.
- `workers/launcher.py`: extend restricted fixed commands to trusted rules and bounded JSON capture; preserve diagnostic probe compatibility.
- `workers/coordinator.py`, `backend/core/lifecycle.py`: heartbeat across whole job, cancellation and transactional result fence.
- `backend/core/contracts.py`: reuse Scan/Finding/Repair, add requested repository ref attribution.
- `backend/api/main.py`: extend existing admission with bounded repository JSON, reuse owner/idempotency/store.
- `frontend/src/SourceIntake.tsx`: keep submission, polling and delete; add repository mode and reconnect. Shared report component for both modes.

## Tasks & Acceptance
- [x] `rules/`, `backend/adapters/source.py`, `workers/launcher.py`: authored rules, fingerprints, outcome validation and sanitization.
- [x] `backend/core/lifecycle.py`, `workers/coordinator.py`: publish complete/partial/failed reports safely and clean actual containers.
- [x] `backend/adapters/repository.py`, `backend/api/main.py`: bounded provider retrieval/extraction with shared intake checks.
- [x] `frontend/src/Report.tsx`, `SourceIntake.tsx`: filters, evidence, deterministic prompt, repo/ref attribution and recovery.
- [x] `tests/`, generated contracts, docs and sprint tracking: batch verification, record observed limits honestly.

Given trusted labeled inputs, when real tools run, then rule/path/line and sanitized output agree with expected categories and controls.
Given failed or incomplete work, when publishing, then required checks and exclusions remain explicit and cannot produce a secure verdict.
Given identical uploaded and repository source, when reviewed, then both use identical rules and normalizers, with full commit retained for repository mode.
Given stale/deleted work, when attempting publication, then no report becomes readable.

## Implementation Notes
Planning completed inline to honor the user's explicit speed and usage preference. No full suite rerun until the batch reaches Epic 2. Existing 1.2/1.3 review states remain truthful until integrated verification; no automatic issue closure solely for pushed code.

## Verification
One combined Python/frontend suite, build/lint/generated parity and targeted real scanner/repository integration after the batch. Record visual/manual checks separately; do not infer them from compilation.

Batch implementation and automated verification complete. Both epics remain in progress for review, including a rendered accessibility check. Actual outcomes: [verification record](source-repository-batch-verification.md).


User accepted completion and requested issue/milestone closure on 2026-10-24 after focused review. Rendered accessibility checks remain an explicit Story 5.2 follow-up, not a passing claim.
