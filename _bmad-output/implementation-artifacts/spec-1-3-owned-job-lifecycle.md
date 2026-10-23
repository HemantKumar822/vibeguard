---
title: 'Story 1.3: private bounded job lifecycle'
type: feature
created: '2026-10-24'
status: done
route: dispatch
baseline_commit: 77523d31ac499a31f7629c7e3ac8403492996b12
story_key: 1-3-run-isolated-jobs-with-owned-status-and-deletion
review_loop_iteration: 0
context:
  - D:/TechFest/docs/PROJECT_RULES.md
  - D:/TechFest/_bmad-output/implementation-artifacts/epic-1-context.md
---

<frozen-after-approval reason="human-owned intent">

## Intent

Build on verified story 1.2 so accepted source submissions have a private, bounded, observable lifecycle with truthful failure and deletion. Implement only after 1.2 passes its intake/session checks. The trusted coordinator alone launches restricted jobs and the core alone commits state.

## Boundaries & Constraints

Always enforce safety-v1: one running job, three queued, 600-second queue deadline, 300-second global runtime, 90-second source-tool deadline, 5 MiB output/tool, 2 CPUs, 2 GiB RAM, 128 processes and 256 MiB scratch. Store SQLite WAL and private artifacts outside Git/OneDrive. Use immutable scanner digests from verified bootstrap evidence, allowlisted argument arrays, read-only source/root, non-root identity, no network, dropped capabilities and no-new-privileges. The API and worker processes receive neither Docker control nor host secrets.

Never run submitted code or use uploaded rules/config/suppressions. Do not introduce Redis/Celery, public deployment, website egress, findings adapters or comparison. Before story 1.4 installs trusted scanning adapters/rules, version-only probes cannot produce complete/clean scans; terminate unsupported execution with explicit failed/unavailable coverage and deterministic guidance. Scanner containment must be tested physically, not inferred from flags.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected behavior | Error |
|---|---|---|---|
| Admission | Valid owned intake | Transactional queue insertion; caps checked before acceptance | 429 when full; 503 when unsafe runtime |
| Retry | Same session/key and canonical metadata/content | Return original Scan; changed payload conflicts | 409 |
| Ownership | Different/lost/expired cookie | Nonrevealing absence for Scan and deletion operation | 404 |
| Mutation | Missing/invalid CSRF or disallowed Origin | No state change | 403 |
| Claims | Concurrent coordinators/restart | One transactional claim; abandoned work failed and cleaned; no automatic rerun | Explicit safe state |
| Deadline | Queue, tool or global timeout | Core closes tools/Scan, stops worker and cleans scratch | Failed/timed-out with limitations |
| Delete | Queued/running/terminal Scan | Tombstone first, hide immediately, stop work, reject late writes, expose cleanup operation | 202; actual pending/complete/failed |
| Retention | 24h terminal report or inactive session | Inaccessible immediately on expiry; startup and 60s sweeper purge | Cleanup failures block admission |

</frozen-after-approval>

## Code Map

- `backend/adapters/storage.py` from 1.2: extend minimally with persisted queue claims, idempotency and deletion operations; transactional core operations own every transition.
- `backend/core/lifecycle.py`: new state service assembling existing Scan/Tool/Deletion shapes, validating transitions and tombstone guards.
- `backend/core/contracts.py`: retain v1 terminal invariants and deterministic repair requirements; do not invent scan cancellation/deletion states.
- `workers/coordinator.py`, `workers/launcher.py`: new separate trusted command-line process and restricted Docker launcher; API must never import/call Docker launcher.
- `scripts/scanner_readiness.py`, `contracts/scanner-readiness.json`: reuse immutable pins and restricted probe lessons, not version success as scan coverage.
- `backend/api/main.py`, `backend/api/session.py`: wire idempotent admission, owned polling, delete and deletion-status reads.
- `frontend/src/SourceIntake.tsx`: display actual queue/tool state and deletion operation, no synthetic progress; frontend consumes generated types.

## Tasks & Acceptance

**Execution:**
- [x] `backend/core/lifecycle.py`, `backend/adapters/storage.py` — atomic admission/claim, canonical payload idempotency, guarded transitions, safe terminalization and explicit queue/global deadlines.
- [x] `workers/launcher.py` — construct fixed digest-based launches with bounded scratch/output, kill daemon-side jobs on timeout and cleanup; never shell-interpolate user fields.
- [x] `workers/coordinator.py` — separate CLI loop, single coordinator lease/heartbeat, recovery and shutdown; sanitize all returned status; source adapters unavailable until 1.4.
- [x] `backend/core/cleanup.py` — tombstone-first deletion, actual cleanup result/deadline/retry, late-result fences, session/report expiry and startup/minute sweep; persist unresolved cleanup and block admission.
- [x] `backend/api/main.py`, `frontend/src/SourceIntake.tsx` — owned polling/delete routes, headers and truthful tool/deletion states; stop polling on unmount/404 and keep tokens in memory.
- [x] `tests/test_lifecycle.py`, `tests/test_cleanup.py`, `tests/test_worker_isolation.py` — contention, expiry, idempotency, crash, cleanup failure and late-write tests; real Docker checks for read-only mounts, unavailable network/socket, quotas and non-root identity.
- [x] `contracts/openapi.json`, `frontend/src/generated/`, `docs/DEVELOPMENT.md`, story/sprint records — regenerate shared artifacts and document separate API/coordinator commands and operational limitations.

**Acceptance Criteria:**
- Given accepted work and concurrent claimers, when scheduled, then exactly one claim runs restricted workers and no API/scanner receives daemon credentials.
- Given matching/different retries or full queue, when admitted, then the original Scan, 409 or 429 is returned transactionally without duplicate jobs.
- Given crashes/deadlines/foreign sessions, when recovered/accessed, then explicit failure, cleanup and ownership protections hold.
- Given deletion or expiry during a worker run, when late results arrive, then the Scan stays hidden, writes fail and cleanup status reports observed success/failure within policy.

## Implementation Notes

- Implemented SQLite transactional admission/claims, lease recovery, expiry and late-write fences; API never imports the Docker launcher.
- Coordinator dispatch explicitly fails unsupported adapters with zero completed coverage and deterministic fallback guidance. No submitted code is run.
- Cleanup is tombstone-first, durable and retried; failures block intake. Source retention, session expiry and orphan staging sweeps are implemented.
- UI polls actual scan/tool/deletion states with abort/404 handling and memory-only tokens.
- Physical Linux Docker containment/timeout/output cleanup checks passed (4 tests); lifecycle/cleanup focused checks passed (6 tests). Final combined validation/review remains with parent workflow.

## Spec Change Log

## Review Triage Log

| Finding | Verdict and evidence / resolution |
|---|---|
| Blind 1: unreachable deletion | high: dialog had no opener; added accessible trigger and deletion UI regression. Patch. |
| Blind 2: tool states hidden | medium: response tools not rendered; render actual states, tested failed transition. Patch. |
| Blind 3: fallback hidden | medium: error/warnings/repair omitted; render escaped server guidance, tested. Patch. |
| Blind 4: cleanup status race | high: stale API sweep could overwrite complete; conditional update forbids regression. Patch. |
| Blind 5: lease expires during cleanup | high: stop can exceed lease; renew heartbeat during cleanup and fence claim after loss. Patch. |
| Blind 6: queue expiry needs coordinator | medium: API sweep lacked queue expiry; core expiry invoked from sweeps, tested without coordinator. Patch. |
| Blind 7: repeat terminal stop | medium: every terminal history row hit Docker; only stop terminal sources still present, repeated sweep tested. Patch. |
| Blind 8: startup cleanup window | high: background first sweep permits admission first; await initial cleanup before lifespan yield. Patch. |
| Blind 9: private metadata retention | medium: tombstones retained indefinitely; purge completed operation and scan metadata after retry TTL, tested. Patch. |
| Edge 1: unreachable deletion | high: same UI defect, opener and deletion test resolve. Patch. |
| Edge 2: missing observed state/guidance | medium: same omitted response fields, render tools and guidance. Patch. |
| Edge 3: completed status regression | high: same stale write, conditional update resolves. Patch. |
| Gaps 1: polling not tested | medium: previous tests stopped before polling; fake-timer failed/404 transitions and abort assertions now pass. Patch. |
| Gaps other 1: closed dialog | high: same missing trigger; deletion dialog/open/request/cleanup tests pass. Patch. |
| Gaps other 2: old status copy | medium: removed static unavailable statement in favor of observed warnings/states/guidance. Patch. |

## Verification

- `uv run pytest -q` — lifecycle, intake/session and generated-schema regressions pass.
- Run isolated-worker integration tests against the local Linux Docker engine; assert actual restrictions, cancellation and cleanup.
- Regenerate OpenAPI/types, then frontend contract checks, tests, build and lint pass.
- Exercise a real owned submission, coordinator dispatch, foreign-session read and deletion; record unavailable scanner-adapter coverage honestly.

Final verification: combined suite observed 101 passed, one total-upload deadline failure and three Docker opt-in skips. The deadline was fixed and all three deadline cases passed. Docker physical tests separately passed (4). Targeted lifecycle/cleanup after review: 9 passed; coordinator sequence: 1 passed. Targeted UI: 11 passed. Contract parity, production build and lint passed. No full-suite repetition after focused fixes per user instruction. No finding deferred. Existing Starlette warning remains.
