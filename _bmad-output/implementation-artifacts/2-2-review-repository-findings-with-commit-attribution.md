---
story_id: '2.2'
epic: 2
status: ready-for-dev
prepared: true
approval: pending-user-review
assignee: unassigned
owner_role: "Frontend / repository workflow"
priority: P0
depends_on: ["2.1", "1.5"]
blocks: ["4.2"]
source: ../planning-artifacts/epics.md
---

# Story 2.2 · Review repository findings with commit attribution

> **Epic 2** · Required scope · Proposed owner role: **Frontend / repository workflow** · Actual assignee: **unassigned**

## Summary

Let the developer choose Repository mode and understand which commit produced the findings in the same visual workspace.

## User story

As a developer, I want repository submission and evidence in the same workspace, so that manual upload is unnecessary and results remain reproducible.

## Requirements and source of truth

- **FR-1 — Three submission modes**
- **FR-3 — Repository submission**
- **FR-11 — Attributed findings**
- **FR-19 — Cohesive graphical workflow**

**All references:** FR-1, FR-3, FR-11, FR-19; UX-DR1, UX-DR3, UX-DR15, UX-DR18; AD-1, AD-3.

- [Canonical backlog](../planning-artifacts/epics.md) and [PRD](../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Blocked by — finish these first:**

- [Story 2.1: Retrieve a bounded public repository snapshot](2-1-retrieve-a-bounded-public-repository-snapshot.md)
- [Story 1.5: Investigate findings and copy a deterministic repair prompt](1-5-investigate-findings-and-copy-a-deterministic-repair-prompt.md)

**Unblocks:**

- [Story 4.2: Execute real rescans and classify comparable findings](4-2-execute-real-rescans-and-classify-comparable-findings.md)

A prepared story is not automatically unblocked. Do not mark it in progress while required predecessors remain unfinished; discuss any contract-only parallel task separately.

## In scope / implementation checklist

- [ ] Connect the repository/ref form to real retrieval and shared report endpoints.
- [ ] Show requested/ref-resolved commit, actual progress and ordinary source evidence/repair guidance.
- [ ] Handle mode switching, refresh, missing ref and denied retrieval without duplicate work.

## Out of scope

- No private-repository login or history interface.
- No separate repository-only report schema or dashboard.

## Acceptance criteria

- [ ] **AC-1** **Given** Repository mode, **When** submitting a valid ref, **Then** the workspace displays requested/ref-resolved commit, actual progress, source findings and a usable prompt from live API output.
- [ ] **AC-2** **Given** denied repository/missing ref/retrieval failure, **When** rejected, **Then** input remains editable with a safe reason; **And** unsupported private/history capability is explicit.
- [ ] **AC-3** **Given** mode switching or refresh, **When** returning, **Then** accepted Scan identity and valid selected input/report state follow EXPERIENCE.md without duplicate retrieval.

## Verification plan

- [ ] Complete a live public-repository scan and inspect commit-attributed evidence.
- [ ] Repeat failed/missing-ref submission and correct it in place.
- [ ] Switch modes and reconnect; verify accepted scan identity is preserved.

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

[Parent epic](../github-issues/epics/epic-02-review-a-repository-revision-without-manual-upload.md) · [All stories](README.md)
