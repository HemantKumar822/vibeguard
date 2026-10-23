---
story_id: '1.2'
epic: 1
status: ready-for-dev
prepared: true
approval: pending-user-review
assignee: unassigned
owner_role: "Backend / intake"
priority: P0
depends_on: ["1.1"]
blocks: ["1.3"]
source: ../planning-artifacts/epics.md
---

# Story 1.2 · Accept an authorized bounded source tree

> **Epic 1** · Required scope · Proposed owner role: **Backend / intake** · Actual assignee: **unassigned**

## Summary

Let a developer submit a source tree without losing directory structure or letting unsafe files reach a scanner.

## User story

As a developer, I want to submit my full source tree with clear limits, so that I know exactly what the review will inspect.

## Requirements and source of truth

- **FR-1 — Three submission modes**
- **FR-2 — Full codebase submission**
- **FR-5 — Recognized scope**
- **FR-20 — Authorization and data choice**

**All references:** FR-1, FR-2, FR-5, FR-20; NFR-2, NFR-3; UX-DR1, UX-DR15, UX-DR16; AD-1, AD-11.

- [Canonical backlog](../planning-artifacts/epics.md) and [PRD](../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 1.1: Set up initial project from starter template and freeze contracts](1-1-set-up-initial-project-from-starter-template-and-freeze-contracts.md)

**Downstream work:**

- [Story 1.3: Run isolated jobs with owned status and deletion](1-3-run-isolated-jobs-with-owned-status-and-deletion.md)

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [ ] Implement the source-tree multipart contract with permission and model-sharing fields; keep sharing off by default.
- [ ] Preserve safe relative paths and stream aggregate/file limits instead of buffering an unlimited upload.
- [ ] Create only session/submission records needed here; return the accepted inventory and explicit exclusions.
- [ ] Handle invalid, unsupported and browser-limited input with safe actionable errors.

## Out of scope

- No archive-only replacement for required tree input.
- No running uploaded code, installs or scanner commands in the intake handler.

## Acceptance criteria

- [ ] **AC-1** **Given** valid folder/file-tree multipart input and permission confirmation, **When** submitted, **Then** relative paths, inventory, exclusions and external-sharing choice are recorded under the initiating session; **And** model sharing defaults off.
- [ ] **AC-2** **Given** traversal, absolute paths, links, special files, duplicate/case-colliding paths or missing multipart mappings, **When** validated, **Then** input is rejected safely before scanner dispatch; **And** field errors do not include raw source/credentials.
- [ ] **AC-3** **Given** each safety-v1 file/count/byte/path bound and one over-limit case, **When** streamed, **Then** the allowed boundary succeeds and over-limit input is rejected without unbounded buffering.
- [ ] **AC-4** **Given** unsupported project/browser input, **When** selected, **Then** inventory/coverage or browser limitation is explicit; **And** unsupported Codebase behavior is not counted as delivered support.

## Verification plan

- [ ] Submit a multi-directory JS/TS fixture and verify its paths/inventory.
- [ ] Exercise traversal, links, duplicate/case collisions and malformed part mappings.
- [ ] Test each configured limit at its boundary and one value over it.

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
