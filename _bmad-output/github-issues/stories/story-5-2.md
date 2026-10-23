# Story 5.2 · Verify accessible recovery and rehearse the honest demo

> **Epic 5** · Required scope · Proposed owner role: **Frontend / QA / demo operations** · Actual assignee: **unassigned**

## Summary

Make the implemented workflow accessible and rehearsable so teammates can present it without hiding broken or incomplete states.

## User story

As a team presenter, I want a usable, rehearsed application and operator guide, so that the demonstration is reliable and its limitations are clear.

## Requirements and source of truth

- **FR-19 — Cohesive graphical workflow**

**All references:** FR-19; NFR-6; UX-DR11, UX-DR12, UX-DR13, UX-DR14, UX-DR15, UX-DR16, UX-DR17, UX-DR18; AD-12.

- [Canonical backlog](../../planning-artifacts/epics.md) and [PRD](../../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Blocked by — finish these first:**

- [Story 5.1: Run the labeled acceptance and adversarial corpus](../../implementation-artifacts/5-1-run-the-labeled-acceptance-and-adversarial-corpus.md)

**Unblocks:**

- No direct successor; completion contributes to its epic acceptance.

A prepared story is not automatically unblocked. Do not mark it in progress while required predecessors remain unfinished; discuss any contract-only parallel task separately.

## In scope / implementation checklist

- [ ] Test every journey and state against the rendered UX contracts, fixing meaningful recovery/accessibility defects.
- [ ] Write the actual operator setup, run, demo, recovery and cleanup guide from observed commands.
- [ ] Rehearse from a clean start on the demonstration machine and document remaining limitations.

## Out of scope

- No optional feature expansion, decorative animation sprint or fabricated polished success.
- Do not assert accessibility from token contrast calculations alone.

## Acceptance criteria

- [ ] **AC-1** **Given** all three UX journeys, **When** tested at desktop/360px, 200% zoom, keyboard and reduced motion, **Then** core actions, focus, labels, status announcements, contrast and evidence reflow pass; **And** findings/fixes are recorded rather than asserting accessibility from tokens alone.
- [ ] **AC-2** **Given** each specified error/empty/partial/denied/expired state and unsupported clipboard/folder behavior, **When** encountered, **Then** recovery copy and actions match EXPERIENCE.md without data loss or duplicate scans.
- [ ] **AC-3** **Given** a clean start on the demo machine, **When** the operator guide is followed, **Then** versioned setup, real scan/repair/rescan, cleanup and failure recovery are rehearsed; **And** fixture-only limitations and pending issues are disclosed, not hidden behind mock output.

## Verification plan

- [ ] Exercise keyboard, screen-reader/status behavior where available, 360px viewport, 200% zoom and reduced motion.
- [ ] Test all empty/partial/denied/expired/clipboard/folder/deletion states with their recovery.
- [ ] Follow the operator guide end to end and record real demo evidence and limitations.

Record the actual commands, observed results and sanitized evidence in the PR and implementation record. Use commands introduced by the real scaffold; no nonexistent build/test command is asserted here.

## Definition of done

- [ ] All acceptance criteria satisfied, including relevant failure cases.
- [ ] Required predecessors complete; one accountable assignee recorded.
- [ ] Appropriate automated/manual checks run with observed results; limitations explicit.
- [ ] Contract/types/fixtures/docs updated together when changed.
- [ ] No secrets, runtime scan data or local agent installations in the diff.
- [ ] Reviewed PR linked and story/sprint/issue status reconciled.

[Implementation handoff](../../implementation-artifacts/5-2-verify-accessible-recovery-and-rehearse-the-honest-demo.md)
