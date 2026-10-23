---
story_id: '5.1'
epic: 5
status: ready-for-dev
prepared: true
approval: pending-user-review
assignee: unassigned
owner_role: "QA / security validation"
priority: P0
depends_on: ["4.3"]
blocks: ["5.2"]
source: ../planning-artifacts/epics.md
---

# Story 5.1 · Run the labeled acceptance and adversarial corpus

> **Epic 5** · Required scope · Proposed owner role: **QA / security validation** · Actual assignee: **unassigned**

## Summary

Give evaluators repeatable evidence that all required modes and safety cases work on the actual demo machine, including what the tool misses.

## User story

As a hackathon evaluator, I want a repeatable real-output demonstration and failure evidence, so that detection, repair and comparison claims can be assessed honestly.

## Requirements and source of truth

- **FR-7 — Required issue categories**
- **FR-8 — Browser-visible secrets**
- **FR-9 — Public-key distinction**
- **FR-10 — Actual tool states**
- **FR-13 — Grounded explanations**
- **FR-16 — Real repeat execution**
- **FR-17 — Honest classifications**
- **FR-21 — Deletion and access**

**All references:** FR-7, FR-8, FR-9, FR-10, FR-13, FR-16, FR-17, FR-21; NFR-1, NFR-2, NFR-3, NFR-4, NFR-5, NFR-7; AD-12.

- [Canonical backlog](../planning-artifacts/epics.md) and [PRD](../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 4.3: Inspect paired rescan evidence and recovery](4-3-inspect-paired-rescan-evidence-and-recovery.md)

**Downstream work:**

- [Story 5.2: Verify accessible recovery and rehearse the honest demo](5-2-verify-accessible-recovery-and-rehearse-the-honest-demo.md)

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [ ] Run a per-mode vulnerable/corrected/clean matrix: all four categories across the product, real passive alerts and visible-asset secrets for websites, with unsupported cells explained.
- [ ] Exercise hostile intake/network/session/deletion/crash/model/sanitization cases against the actual implementation.
- [ ] Record sanitized expected/observed outputs, versions, coverage, runtimes and guidance utility without unsupported percentages.

## Out of scope

- No mock output substituted for a real scan or error screen counted as mode completion.
- No live secrets or unauthorized target testing.

## Acceptance criteria

- [ ] **AC-1** **Given** a labeled vulnerable/corrected/clean matrix covering all four issue categories across the product and all three input modes within their supported capabilities, **When** run on the demo machine, **Then** expected/observed rules/alerts, locations, versions, coverage and elapsed runtime are saved as sanitized evidence; **And** source/repository cases validate selected unsafe-input and access-check rules, website cases validate actual passive alerts and visible-asset secrets, unsupported matrix cells have explicit reasons, and required mode completion is 3/3 rather than three error screens.
- [ ] **AC-2** **Given** the hostile path/config/network/session/CSRF/idempotency/deletion/crash and model-outage corpus, **When** exercised, **Then** documented boundaries hold or failures block release; **And** fake private values are absent from all outward tested surfaces.
- [ ] **AC-3** **Given** recorded outcomes, **When** metrics and guidance are assessed, **Then** issue-occurrence TP/FP/FN, denominators, misses and per-criterion prompt utility are reported without invented accuracy/speed; **And** incomplete coverage cannot game results.

## Verification plan

- [ ] Demonstrate three successful required-mode loops with genuine rescans.
- [ ] Report issue-occurrence true/false positives and false negatives with valid denominators.
- [ ] Document failed safety criteria as release blockers and keep all outward evidence sanitized.

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

[Parent epic](../github-issues/epics/epic-05-demonstrate-the-complete-workflow-with-repeatable-evidence.md) · [All stories](README.md)
