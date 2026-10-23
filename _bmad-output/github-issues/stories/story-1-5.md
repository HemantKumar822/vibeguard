# Story 1.5 · Investigate findings and copy a deterministic repair prompt

> **Epic 1** · Required scope · Proposed owner role: **Frontend / source workflow** · Actual assignee: **unassigned**

## Summary

Give the developer a usable source-review workspace and a repair prompt they can act on before AI integration exists.

## User story

As a developer, I want one accessible workspace for source evidence and repair guidance, so that I can act without interpreting raw scanner output.

## Requirements and source of truth

- **FR-12 — Interactive investigation**
- **FR-14 — Consolidated repair prompt**
- **FR-15 — Credential follow-up**
- **FR-19 — Cohesive graphical workflow**
- **FR-20 — Authorization and data choice**
- **FR-21 — Deletion and access**

**All references:** FR-12, FR-14, FR-15, FR-19, FR-20, FR-21; NFR-6; UX-DR2, UX-DR3, UX-DR4, UX-DR5, UX-DR6, UX-DR8, UX-DR9, UX-DR10, UX-DR11, UX-DR12, UX-DR13, UX-DR14, UX-DR15, UX-DR16, UX-DR17, UX-DR18; AD-3, AD-4.

- [Canonical backlog](../../planning-artifacts/epics.md) and [PRD](../../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 1.4: Detect and sanitize source findings with trusted rules](../../implementation-artifacts/1-4-detect-and-sanitize-source-findings-with-trusted-rules.md)

**Downstream work:**

- [Story 2.2: Review repository findings with commit attribution](../../implementation-artifacts/2-2-review-repository-findings-with-commit-attribution.md)
- [Story 3.4: Investigate website findings in the shared workspace](../../implementation-artifacts/3-4-investigate-website-findings-in-the-shared-workspace.md)
- [Story 4.1: Add opt-in bounded AI explanations with fallback](../../implementation-artifacts/4-1-add-opt-in-bounded-ai-explanations-with-fallback.md)

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [ ] Implement source submission/progress, coverage, filters, finding selection/detail and the deterministic repair panel using the UX tokens.
- [ ] Show confidence, real source locations, incomplete checks and separate revoke/rotate guidance.
- [ ] Add safe clipboard fallback, reconnect-to-existing-scan behavior and confirmed deletion UI.
- [ ] Verify keyboard focus, narrow layout, contrast and reduced motion on the actual rendered interface.

## Out of scope

- No chatbot, fake score, fabricated scan percentage or AI requirement.
- No comparison UI until the comparison story.

## Acceptance criteria

- [ ] **AC-1** **Given** an actual source report, **When** opening/filtering/selecting findings, **Then** tokens, list/detail, real timeline and coverage match the UX contracts; **And** typed locations, confidence, impact and repair use sanitized escaped text.
- [ ] **AC-2** **Given** findings or completed clean checks, **When** composing guidance, **Then** one deterministic prompt includes reported locations, required changes, verification and separate rotation actions; **And** no model is needed and no blanket secure verdict appears.
- [ ] **AC-3** **Given** clipboard failure, partial report, disconnect or delete failure, **When** the action fails, **Then** the specified recovery remains visible, copy permits sanitized manual selection, and reconnect checks the existing Scan without duplicating it.
- [ ] **AC-4** **Given** keyboard, reduced-motion, 360px viewport and 200% zoom, **When** core actions are exercised, **Then** focus/labels/contrast and local code scrolling meet the UX contract; **And** no hidden raw secrets or persistent source cache exists.

## Verification plan

- [ ] Run the source fixture through the live API, filter/select findings and copy the sanitized prompt.
- [ ] Exercise clean/partial/filter-empty/disconnected/clipboard/delete-failure states.
- [ ] Check keyboard, 360px viewport, 200% zoom and reduced motion; inspect hidden accessible output for raw secrets.

Record the actual commands, observed results and sanitized evidence in the PR and implementation record. Use commands introduced by the real scaffold; no nonexistent build/test command is asserted here.

## Definition of done

- [ ] All acceptance criteria satisfied, including relevant failure cases.
- [ ] Required predecessors complete; one accountable assignee recorded.
- [ ] Appropriate automated/manual checks run with observed results; limitations explicit.
- [ ] Contract/types/fixtures/docs updated together when changed.
- [ ] No secrets, runtime scan data or local agent installations in the diff.
- [ ] Reviewed PR linked and story/sprint/issue status reconciled.

[Implementation handoff](../../implementation-artifacts/1-5-investigate-findings-and-copy-a-deterministic-repair-prompt.md)
