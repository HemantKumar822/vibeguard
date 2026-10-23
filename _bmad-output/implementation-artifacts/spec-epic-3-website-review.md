---
title: Epic 3 bounded website review
type: feature
created: '2026-10-24'
status: done
route: dispatch
baseline_commit: 9dcf3143fd2605e4a09a5007714529f8d0b55c2f
context: []
---

<frozen-after-approval>
## Intent
Implement Stories 3.1–3.4 as one authorized batch: controlled public website capture, actual ZAP passive findings, browser-visible credential candidates and the existing graphical evidence/repair workflow. Preserve the merged UI polish and source/repository behavior. The user requested implementation without repetitive checkpoints or full-suite runs per story.

## Boundaries & Constraints
Only authorized unauthenticated HTTP80/HTTPS443 exact-origin GET requests. Resolve DNS for every connection, reject any nonpublic/mapped-private destination, pin the connected peer and validate HTTPS certificates normally. Count every request before send, including redirects; bound responses, discovery, pages, assets and total time using safety-v1. No environment proxy, cookies, scripts, form submissions, active attacks or cross-origin fetches.

Use a trusted host fetcher to capture responses, then import that HAR into pinned ZAP 2.17.0 in a network-disabled container. ZAP cannot originate external requests; its control API is loopback-only inside the container, with no port publication. This is a real passive baseline of captured responses, not the packaged online spider or active scanner. Gitleaks inspects temporary browser-visible text in another network-disabled worker. Both use the existing quota, cleanup, cancellation and publication fences. No raw vendor fields, response headers, body excerpts or credential values may cross report/UI/prompt boundaries. Capture/HAR/body data remains private temporary scratch and is purged on termination/deletion/recovery.

Website availability must fail closed when the proof record/image/implementation fingerprint is missing or stale. Show actual ZAP/asset outcomes and omitted/runtime-only scope. Preserve bounded useful evidence as partial when any stage fails; no error or limit may become a clean success.

## I/O & Edge-Case Matrix
| Input/state | Expected result |
| --- | --- |
| Authorized public origin with vulnerable headers and fake asset credential | Actual passive ZAP IDs and mapped masked asset URL/line, rotation actions and repair prompt |
| Public-key control and corrected headers | No automatic private-key classification; retain any other real ZAP warnings |
| Private/reserved/mapped IPv6/DNS rebind/alternate port/credentials | Reject before contacting forbidden peer |
| Same-origin redirect vs off-origin/loop/over-three redirects | Revalidate and count allowed requests; omit/stop forbidden redirect with incomplete scope |
| Request/page/asset/body/aggregate/deadline/output limit | Terminate bounded work, explicit incomplete coverage |
| Broken ZAP JSON/import/tool timeout or deletion/lost lease | Safe failed/partial result, stopped workers and no late report publication |
| Website mode, blocked or partial report | Same workspace, URL evidence rather than invented source paths, safe reconnect and prompt copy |
</frozen-after-approval>

## Code Map
- `backend/adapters/repository.py`: existing connection-pinning pattern, reused conceptually for HTTP/HTTPS with explicit shared web counters.
- `backend/core/contracts.py`, `lifecycle.py`, `cleanup.py`: shared modes, WebLocation, reports, transaction fences and raw source retention.
- `workers/launcher.py`, `coordinator.py`: retain API/Docker boundary and restricted immutable-image workers; dispatch website jobs separately.
- `backend/api/main.py`: extend JSON Intake admission without performing network work in the API.
- `frontend/src/SourceIntake.tsx`, `Report.tsx`: retain polished UI, generated schemas, filtering/recovery/clipboard and add target/location context.

## Tasks & Acceptance
- [x] `backend/adapters/web_capture.py`: bounded origin validation, per-connection DNS/peer enforcement, shared budgets, discovery and HAR capture.
- [x] `workers/zap_runner.py`, `launcher.py`: isolated import-only passive ZAP; bounded output and true errors, versions/plugin fingerprints.
- [x] `backend/adapters/web_report.py`, `workers/website.py`: sanitize actual alerts, map trusted Gitleaks findings back to fetched resources, partial outcomes and cleanup.
- [x] `backend/core/website_readiness.py`, API/contracts/types and UI: fail-closed availability and Website workflow.
- [x] `tests/`, docs and implementation records: hostile boundary tests, actual offline ZAP/asset/containment checks, then one combined epic verification.

Given a real captured response set, when the pinned scanners complete, then located findings and typed coverage reflect only observed resources.
Given malicious destinations or bounds, when encountered, then actual traffic cannot bypass peer/budget enforcement and missing coverage stays explicit.
Given missing/stale readiness or deleted work, when admission/publication is attempted, then it fails closed.

## Implementation Notes
Critical feasibility gate passed before integration: pinned ZAP 2.17.0, `--network=none`, private loopback control, import-only HAR produced alert IDs 10020/10015/10038/10035/10021. No external target was contacted by that probe. Official import behavior: https://www.zaproxy.org/docs/desktop/addons/import-export/automation/ . Existing source worker tests remain the baseline; broader tests are deferred until this full batch is present.

## Verification
Unit/API/DOM boundaries plus real network-disabled ZAP import and fake-credential/control cases. Physical denial of direct egress and private control exposure; full existing Python/frontend suite once at the epic boundary, then only targeted fixes. No unsupported claim of arbitrary-target delivery or rendered accessibility verification.


Implementation and batch verification complete. See [Epic 3 evidence](epic-3-verification.md); remote acceptance/closure is not implied.
