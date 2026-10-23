---
story_id: '1.1'
epic: 1
status: in-review
prepared: true
approval: implementation-authorized
assignee: HemantKumar822
owner_role: "Full-stack / platform"
priority: P0
depends_on: []
blocks: ["1.2"]
baseline_commit: 2338c6d85dff1d07ac8984e0e081a8daf12a7cf6
source: ../planning-artifacts/epics.md
---

# Story 1.1 · Set up initial project from starter template and freeze contracts

> **Epic 1** · Required scope · Proposed owner role: **Full-stack / platform** · Actual assignee: **HemantKumar822**

## Summary

Give the team a working development starting point and one shared API shape before separate feature work begins.

## User story

As a team developer, I want a reproducible starter and shared boundary fixtures, so that separate UI and scanner work integrates without incompatible assumptions.

## Requirements and source of truth

- **FR-19 — Cohesive graphical workflow**

**All references:** FR-19; NFR-5; UX-DR11; AD-3, AD-12.

- [Canonical backlog](../planning-artifacts/epics.md) and [PRD](../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- None. This is the starting story.

**Downstream work:**

- [Story 1.2: Accept an authorized bounded source tree](1-2-accept-an-authorized-bounded-source-tree.md)

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [x] Create the React/TypeScript starter and minimal FastAPI health endpoint, then record compatible dependency locks.
- [x] Turn API-CONTRACT v1 into backend models, a generated OpenAPI snapshot, frontend types and labeled boundary fixtures.
- [x] Check the actual scanner/container runtime and record tool versions and immutable image digests; report missing prerequisites honestly.
- [x] Add and run the real build/type/schema checks; replace planning-only setup notes with the commands that now work.

## Out of scope

- No real upload, scanner integration, report UI, queue or website enforcement yet.
- Do not create every future database table or advertise fixture data as scanner output.

## Acceptance criteria

- [x] **AC-1** **Given** a clean checkout, **When** the documented bootstrap runs, **Then** the Vite react-ts workspace and FastAPI health endpoint build/start using recorded compatible locks; **And** candidate version changes are documented rather than silently floating.
- [x] **AC-2** **Given** API-CONTRACT v1, **When** backend models/OpenAPI and frontend types are generated, **Then** source-running, partial, clean, website, AI-fallback, comparison and deletion fixtures validate against the same schema; **And** fixture UI is visibly development-only.
- [x] **AC-3** **Given** the intended container runtime, **When** pinned scanner images are checked, **Then** actual Gitleaks/Semgrep/ZAP versions and immutable digests are recorded; **And** unavailable runtime/tooling creates a blocking feasibility result rather than fake scan success.
- [x] **AC-4** **Given** no feature needs a table yet, **When** the starter is created, **Then** no speculative full database/entity set is created; **And** runtime data and credentials remain outside version control.

## Verification plan

- [x] Build/type-check the starter and request the real health endpoint.
- [x] Validate every required boundary fixture against the generated schema.
- [x] Record scanner startup/version results, locks and runtime prerequisites.

Record the actual commands, observed results and sanitized evidence in the PR and implementation record. Use commands introduced by the real scaffold; no nonexistent build/test command is asserted here.

## Definition of done

- [ ] All acceptance criteria satisfied, including relevant failure cases.
- [ ] Required predecessors complete; one accountable assignee recorded.
- [ ] Appropriate automated/manual checks run with observed results; limitations explicit.
- [ ] Contract/types/fixtures/docs updated together when changed.
- [ ] No secrets, runtime scan data or local agent installations in the diff.
- [ ] Reviewed PR linked and story/sprint/issue status reconciled.

## Implementation record

Implemented on `feat/1-1-project-bootstrap`; PR/teammate review pending. No real submission or security scan is available yet.

- Started with failing tests for the missing backend, readiness checker, error envelope and failure states; implemented the smallest bootstrap to make them pass.
- `uv sync --frozen`: passed. `npm --prefix frontend ci`: passed after stopping the development server that held a native module open on Windows.
- `uv run pytest -q`: 16 passed; one upstream Starlette warning recommends replacing its deprecated httpx compatibility dependency with httpx2 in a later dependency update.
- Backend OpenAPI export, generated TypeScript, typecheck, production build and lint: passed.
- All eight synthetic fixtures validate in Python and compile against generated frontend types. Production assets exclude the fixture module and payloads.
- Docker Desktop 4.96.3 installed through winget; Linux engine 29.9.2 running. Gitleaks 8.30.1 passed its actual version probe by immutable digest. Semgrep/ZAP image pulls did not finish within the bounded attempts; [readiness evidence](../../contracts/scanner-readiness.json) remains an explicit blocking feasibility result. No version/digest is invented for unavailable images. AC-3's unavailable-tool branch is exercised, not a claim that scanners are ready.
- Browser visual inspection was not performed because the browser access request was declined. No accessibility or rendered-layout pass is claimed.

## Code map

- [HTTP health and schema](../../backend/api/main.py)
- [Shared typed models](../../backend/core/contracts.py)
- [Exported OpenAPI](../../contracts/openapi.json) and [frontend types](../../frontend/src/generated/api.ts)
- [Fixture examples](../../fixtures/contracts/) and [development setup](../../docs/DEVELOPMENT.md)
- [Scanner feasibility probe](../../scripts/scanner_readiness.py)

## Review triage log

Review was performed inline per the user's preference to avoid routine subagent usage; it is not an independent teammate review.

| Finding | Evidence and disposition |
| --- | --- |
| Proposed TypeScript 7 incompatible with generator | Reproduced missing `ts.factory`; pinned supported 5.9.3. Generation/build pass. |
| Error response wrapper missing | Added `ErrorResponse`, exported it, and tested the required envelope. |
| Numeric consent was coerced to booleans | Reproduced numeric permission/sharing acceptance; strict boolean checks and regressions now pass. |
| Failed deletion allowed no error | Added explicit failure-reason validation; regression passes. |
| Newly installed Docker helper absent from inherited PATH | Observed credential-helper lookup failure; scoped PATH to Docker's sibling binaries and added regression. |
| One scanner timeout skipped subsequent probes | Reproduced and fixed per-scanner timeout handling; subsequent tools are now attempted. |
| Development fixtures might ship as production results | Checked built JS; fixture module/data are absent. |

Scanner execution/containment, uploads, sessions, persistent state and rescan algorithms remain in their own stories. The scanner-readiness gate remains blocked until all actual image probes pass.

[Parent epic](../github-issues/epics/epic-01-review-a-codebase-safely-and-act-on-real-findings.md) · [All stories](README.md)
