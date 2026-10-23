---
title: 'Story 1.2: authorized bounded source-tree intake'
type: feature
created: '2026-10-24'
status: done
route: dispatch
baseline_commit: c330c98f94a07464f507adcb7f1cde5553237ef3
story_key: 1-2-accept-an-authorized-bounded-source-tree
review_loop_iteration: 0
context:
  - D:/TechFest/docs/PROJECT_RULES.md
  - D:/TechFest/_bmad-output/implementation-artifacts/epic-1-context.md
---

<frozen-after-approval reason="human-owned intent">

## Intent

Developers can submit a full source tree while preserving directories, explicitly authorizing review and seeing accepted scope and exclusions. Implement this before story 1.3; acceptance must never imply a scanner ran.

## Boundaries & Constraints

Always use API-CONTRACT v1, generated frontend types and safety-v1. Require session ownership, allowed Origin and CSRF for submission. Sharing is off unless explicitly chosen. Store SQLite metadata and private source staging outside the checkout and OneDrive; reject unsafe runtime configuration. Keep credentials, source and raw exceptions out of responses and logs. Session cookies are random, HTTP-only, SameSite Strict, Secure except explicit loopback HTTP development.

Never execute uploaded code, hooks, builds, dependencies or project scanner configuration. Do not implement repository/website intake, archives, findings, comparison or external model calls. Unsupported modes remain explicitly unavailable. Story 1.3 adds orchestration; until then accepted scans remain queued with no fabricated progress.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected behavior | Error |
|---|---|---|---|
| Tree | Permission plus metadata and mapped file bodies | 202 Scan, preserved safe paths, inventory/exclusions, stored sharing choice | Safe field errors |
| Permission | Missing/false authorization | No accepted scan or staged remnants | 403 |
| Mapping | Missing, repeated, unmapped parts or malformed metadata | Reject whole submission; remove staging | 400/422 |
| Paths | Absolute, traversal, links/devices, reserved Windows names, aliases, normalized/case collisions, file-directory conflicts | Reject before publication/dispatch | 422 |
| Limits | At and one over 25 MiB, 5,000 files, 2 MiB/file, depth 20, 240 UTF-8 bytes/path | Boundary accepted; over-limit rejected during stream; bounded headers/metadata too | 413/422 |
| Exclusions | Vendor/build/binary or unsupported content | Explicit bounded reasons; unsupported-only input cannot claim supported coverage | 422 when no reviewable source |
| Browser | Directory selection unavailable or relative paths lost | Actionable limitation and explicit mapped-file alternative; no invented tree | Visible error |

</frozen-after-approval>

## Code Map

- `backend/api/main.py`: health-only app and custom OpenAPI; introduce injectable app factory while retaining health behavior.
- `backend/core/contracts.py`: reuse CodebaseMetadata, Scan, Coverage, ErrorResponse; default missing sharing to false while preserving strict boolean validation.
- `backend/core/policy.py`, `backend/core/settings.py`: new authoritative limits, fingerprint and validated external runtime paths.
- `backend/adapters/storage.py`: new minimal sessions/submissions/scans storage, atomic acceptance and staging ownership; avoid future speculative tables.
- `backend/adapters/intake.py`: new bounded streaming multipart parser and safe tree manifest.
- `frontend/src/App.tsx`, `frontend/src/index.css`: retain visual tokens and dev fixture separation; mount a focused source submission component.
- `scripts/export_contracts.py`, `frontend/scripts/check-contracts.mjs`: regenerate schemas and types together; bootstrap tests currently assert absent routes and must be deliberately updated.

## Tasks & Acceptance

**Execution:**
- [x] `backend/core/policy.py`, `backend/core/settings.py` — implement policy and external storage validation.
- [x] `backend/adapters/storage.py`, `backend/api/session.py` — add minimal session persistence, Origin/cookie/CSRF checks and safe error handling.
- [x] `backend/adapters/intake.py` — parse bounded multipart incrementally, validate mappings/paths/types, stage private files and remove failed uploads; use a locked maintained multipart dependency.
- [x] `backend/api/main.py`, `backend/core/contracts.py` — session/capabilities/submission/owned-read endpoints and accepted Scan inventory; preserve unavailable modes and unassessed tool states.
- [x] `frontend/src/SourceIntake.tsx`, `frontend/src/App.tsx`, `frontend/src/index.css` — directory and mapped file selection, permission/sharing choices, bounds, inventory and safe error display; no persistent browser storage.
- [x] `tests/test_intake.py`, `tests/test_sessions.py`, `frontend/src/SourceIntake.test.tsx` — exercise matrix, chunked requests without Content-Length, mid-upload disconnect and cleanup; use private temporary runtime directories.
- [x] `contracts/openapi.json`, `frontend/src/generated/`, `uv.lock`, `docs/DEVELOPMENT.md`, story record — regenerate and document verified commands and limitations.

**Acceptance Criteria:**
- Given a supported multi-directory JS/TS tree, when submitted with permission, then the initiating session receives a valid queued Scan and explicit inventory/exclusions with sharing defaulted off.
- Given every unsafe path/type/mapping and boundary-plus-one case, when streamed, then it is rejected without unbounded buffering, scanner dispatch, secret-bearing errors or residual source.
- Given another session or unsupported browser input, when accessed or selected, then privacy or browser limitations remain explicit.

## Implementation Notes

Implemented session/Origin/CSRF protection, safe bounded multipart parsing, validated opaque private staging with relative-path manifest, SQLite ownership/idempotency/admission, generated v1 contract additions, and directory/mapped-file UI. Accepted scans remain queued and inspected coverage remains empty. Windows runtime ACLs are replaced with an owner-only inheritable ACL; POSIX uses owner-only permissions. Runtime configuration is explicit and rejected for checkout/OneDrive/link/junction paths. Current three queued slots remain occupied until story 1.3 adds lifecycle handling.


## Spec Change Log

- Clarified generated v1 Scan accepted_files and allow_external_ai fields to distinguish inventory from inspected coverage; existing fixture defaults remain compatible.


## Review Triage Log

| Finding | Verdict / evidence / route |
|---|---|
| Blind: expired key collision | medium: UNIQUE(owner,idem) survives expiry; patch existing transaction. |
| Blind: browser retry identity | medium: randomUUID on each attempt duplicates accepted lost-response submissions; patch key lifetime. |
| Blind: concurrent intake staging | high: receive precedes capacity check; patch internal concurrency guard. |
| Blind: slow upload lifetime | high: request.stream has no deadline; patch bounded waits and cleanup. |
| Blind: reserved part IDs | high: PART accepts Windows devices used as filenames; patch part validation. |
| Blind: runtime child links | high: only root checked, sources/database children trusted; patch child validation. |
| Blind: descendant ACL inheritance | high: root replacement does not remove protected descendant ACLs; patch existing storage initialization. |
| Blind: environment variants | medium: .env.local excluded despite relevant config policy; patch family recognition. |
| Blind: OpenAPI headers/errors | medium: generated operations omit actual mutation requirements/errors; patch route declarations. |
| Blind: mapped whitespace | medium: trim changes identity before validation; patch preserve characters. |
| Edge: runtime children | high: same reproduced child-link path; patch shared root cause above. |
| Edge: expired key | medium: same persistent uniqueness defect; patch shared root cause above. |
| Edge: retry key | medium: same browser lifetime defect; patch shared root cause above. |
| Edge: MIME parameters | medium: literal comparison misses parameterized prohibited types; patch base MIME parsing. |
| Gaps: independent Origin/CSRF | high: existing test lacks both so either guard can disappear; patch independent cases. |
| Gaps: global queue cap | medium: no fourth-submission assertion; patch cross-session capacity boundary. |
| Gaps: expired idempotency | medium: same old UNIQUE constraint blocks valid reuse; patch shared root cause above. |

## Verification

Observed: 72 backend tests pass; 8 frontend tests pass; production build and lint pass. Real boundary tests cover all configured numeric limits plus one. Real loopback multipart smoke test verifies owned queued inventory without scanner coverage. Generated parity verified after regeneration. One backend warning is Starlette's existing httpx TestClient deprecation.


- `uv run pytest -q` — intake, policy, session and existing regression tests pass.
- `uv run python scripts/export_contracts.py` and `npm --prefix frontend run generate:types` — synchronized contract artifacts.
- `npm --prefix frontend run check:contracts`, `test`, `build`, `lint` — generated parity, UI tests, strict typing and fixture exclusion pass.
- Run a real loopback multipart request and verify owned inventory; no security scan success is claimed.


Final review patches verified: 95 backend tests, 13 frontend tests, contract parity, build and lint passed. All independent findings addressed.
