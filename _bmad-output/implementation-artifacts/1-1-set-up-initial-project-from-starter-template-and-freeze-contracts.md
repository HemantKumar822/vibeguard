---
story_id: '1.1'
epic: 1
status: ready-for-dev
prepared: true
approval: pending-user-review
assignee: unassigned
owner_role: "Full-stack / platform"
priority: P0
depends_on: []
blocks: ["1.2"]
source: ../planning-artifacts/epics.md
---

# Story 1.1 · Set up initial project from starter template and freeze contracts

> **Epic 1** · Required scope · Proposed owner role: **Full-stack / platform** · Actual assignee: **unassigned**

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

- [ ] Create the React/TypeScript starter and minimal FastAPI health endpoint, then record compatible dependency locks.
- [ ] Turn API-CONTRACT v1 into backend models, a generated OpenAPI snapshot, frontend types and labeled boundary fixtures.
- [ ] Check the actual scanner/container runtime and record tool versions and immutable image digests; report missing prerequisites honestly.
- [ ] Add and run the real build/type/schema checks; replace planning-only setup notes with the commands that now work.

## Out of scope

- No real upload, scanner integration, report UI, queue or website enforcement yet.
- Do not create every future database table or advertise fixture data as scanner output.

## Acceptance criteria

- [ ] **AC-1** **Given** a clean checkout, **When** the documented bootstrap runs, **Then** the Vite react-ts workspace and FastAPI health endpoint build/start using recorded compatible locks; **And** candidate version changes are documented rather than silently floating.
- [ ] **AC-2** **Given** API-CONTRACT v1, **When** backend models/OpenAPI and frontend types are generated, **Then** source-running, partial, clean, website, AI-fallback, comparison and deletion fixtures validate against the same schema; **And** fixture UI is visibly development-only.
- [ ] **AC-3** **Given** the intended container runtime, **When** pinned scanner images are checked, **Then** actual Gitleaks/Semgrep/ZAP versions and immutable digests are recorded; **And** unavailable runtime/tooling creates a blocking feasibility result rather than fake scan success.
- [ ] **AC-4** **Given** no feature needs a table yet, **When** the starter is created, **Then** no speculative full database/entity set is created; **And** runtime data and credentials remain outside version control.

## Verification plan

- [ ] Build/type-check the starter and request the real health endpoint.
- [ ] Validate every required boundary fixture against the generated schema.
- [ ] Record scanner startup/version results, locks and runtime prerequisites.

Record the actual commands, observed results and sanitized evidence in the PR and implementation record. Use commands introduced by the real scaffold; no nonexistent build/test command is asserted here.

## Definition of done

- [ ] All acceptance criteria satisfied, including relevant failure cases.
- [ ] Required predecessors complete; one accountable assignee recorded.
- [ ] Appropriate automated/manual checks run with observed results; limitations explicit.
- [ ] Contract/types/fixtures/docs updated together when changed.
- [ ] No secrets, runtime scan data or local agent installations in the diff.
- [ ] Reviewed PR linked and story/sprint/issue status reconciled.

## Implementation record

Not started. Record PR, actual commands/results, sanitized evidence and remaining limitations here during implementation.

[Parent epic](../github-issues/epics/epic-01-review-a-codebase-safely-and-act-on-real-findings.md) · [All stories](README.md)
