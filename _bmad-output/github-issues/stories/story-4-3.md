# Story 4.3 · Inspect paired rescan evidence and recovery

> **Epic 4** · Required scope · Proposed owner role: **Frontend / comparison workflow** · Actual assignee: **unassigned**

## Summary

Help the developer understand before/after evidence and remaining uncertainty, instead of showing a misleading fixed-count celebration.

## User story

As a developer, I want before/after findings and coverage in the workspace, so that I can explain what changed and what remains uncertain.

## Requirements and source of truth

- **FR-16 — Real repeat execution**
- **FR-17 — Honest classifications**
- **FR-18 — Comparison evidence**
- **FR-19 — Cohesive graphical workflow**

**All references:** FR-16, FR-17, FR-18, FR-19; UX-DR7, UX-DR13, UX-DR14, UX-DR15, UX-DR17, UX-DR18; AD-3, AD-8.

- [Canonical backlog](../../planning-artifacts/epics.md) and [PRD](../../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 4.2: Execute real rescans and classify comparable findings](../../implementation-artifacts/4-2-execute-real-rescans-and-classify-comparable-findings.md)

**Downstream work:**

- [Story 5.1: Run the labeled acceptance and adversarial corpus](../../implementation-artifacts/5-1-run-the-labeled-acceptance-and-adversarial-corpus.md)

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [ ] Implement same-mode rescan entry/progress while preserving baseline context.
- [ ] Display four labeled classifications with reasons, both revisions/observations and paired coverage/evidence.
- [ ] Preserve focus/selection and accessible narrow stacking with deliberate recovery for failed repeats.
- [ ] Verify comparison with external AI disabled or unavailable; optional AI integration is not a prerequisite.

## Out of scope

- No UI-created match/classification algorithm or unsupported verified-fixed badge.
- No loss of rotation reminders after a credential warning disappears.

## Acceptance criteria

- [ ] **AC-1** **Given** a baseline, **When** Rescan is selected, **Then** same-mode inputs, permission and actual progress appear while baseline evidence stays accessible.
- [ ] **AC-2** **Given** terminal comparison, **When** a Finding is selected, **Then** both revisions/observations, paired sanitized evidence, classification reason and coverage are available; **And** narrow view stacks baseline then new with text labels.
- [ ] **AC-3** **Given** failed repeat, expired baseline, disconnect or changed coverage, **When** displayed, **Then** no fixed-success state appears and deliberate retry/recovery follows EXPERIENCE.md; **And** keyboard focus/selection remain stable.

## Verification plan

- [ ] Walk UJ-3 using live repeat scans and inspect both observations.
- [ ] Exercise failed repeat, changed coverage, expired baseline and disconnect.
- [ ] Check keyboard navigation, narrow layout and retained baseline state without duplicate work.

Record the actual commands, observed results and sanitized evidence in the PR and implementation record. Use commands introduced by the real scaffold; no nonexistent build/test command is asserted here.

## Definition of done

- [ ] All acceptance criteria satisfied, including relevant failure cases.
- [ ] Required predecessors complete; one accountable assignee recorded.
- [ ] Appropriate automated/manual checks run with observed results; limitations explicit.
- [ ] Contract/types/fixtures/docs updated together when changed.
- [ ] No secrets, runtime scan data or local agent installations in the diff.
- [ ] Reviewed PR linked and story/sprint/issue status reconciled.

[Implementation handoff](../../implementation-artifacts/4-3-inspect-paired-rescan-evidence-and-recovery.md)
