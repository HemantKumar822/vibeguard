---
story_id: '3.4'
epic: 3
status: done
prepared: true
approval: user-accepted
assignee: unassigned
owner_role: "Frontend / website workflow"
priority: P0
depends_on: ["3.3", "1.5"]
blocks: ["4.2"]
source: ../planning-artifacts/epics.md
---

# Story 3.4 · Investigate website findings in the shared workspace

> **Epic 3** · Required scope · Proposed owner role: **Frontend / website workflow** · Actual assignee: **unassigned**

## Summary

Make Website URL review usable in the shared workspace, with separate ZAP and asset coverage and actionable deployment guidance.

## User story

As a developer, I want website submission, evidence and repair guidance together, so that I can act on deployment observations with clear limitations.

## Requirements and source of truth

- **FR-1 — Three submission modes**
- **FR-4 — Website submission**
- **FR-5 — Recognized scope**
- **FR-12 — Interactive investigation**
- **FR-14 — Consolidated repair prompt**
- **FR-19 — Cohesive graphical workflow**
- **FR-20 — Authorization and data choice**

**All references:** FR-1, FR-4, FR-5, FR-12, FR-14, FR-19, FR-20; UX-DR1, UX-DR2, UX-DR3, UX-DR5, UX-DR6, UX-DR15, UX-DR18; AD-1, AD-3.

- [Canonical backlog](../planning-artifacts/epics.md) and [PRD](../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 3.3: Detect secrets in bounded visible assets](3-3-detect-secrets-in-bounded-visible-assets.md)
- [Story 1.5: Investigate findings and copy a deterministic repair prompt](1-5-investigate-findings-and-copy-a-deterministic-repair-prompt.md)

**Downstream work:**

- [Story 4.2: Execute real rescans and classify comparable findings](4-2-execute-real-rescans-and-classify-comparable-findings.md)

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [ ] Connect authorized URL submission and real ZAP/asset progress to the common UI.
- [ ] Display typed web evidence, passive scope, visited/excluded resources and a deterministic repair prompt.
- [ ] Implement blocked/partial/clean/missing-asset recovery states without inventing source files.

## Out of scope

- No new website-only data contract, chat surface or active-scan control.
- A visible failure does not satisfy successful URL-mode delivery.

## Acceptance criteria

- [ ] **AC-1** **Given** Website URL mode and permission, **When** an accepted scan runs, **Then** actual ZAP/asset states, passive scope, observed URL evidence and coverage are rendered without invented source paths.
- [ ] **AC-2** **Given** blocked input, partial crawl, no alerts or missing asset evidence, **When** reported, **Then** the exact UX limitation/recovery appears, completed-count semantics remain truthful and prompt guidance uses available evidence only.
- [ ] **AC-3** **Given** a successful live report, **When** copied, **Then** one sanitized repair prompt and relevant human rotation reminder are usable without the model.

## Verification plan

- [ ] Complete a live controlled website scan and copy guidance grounded in actual web evidence.
- [ ] Exercise blocked destinations, partial crawl, no alerts and asset failure.
- [ ] Verify the UI never implies access to private backend code or a secret-free verdict from unvisited assets.

Record the actual commands, observed results and sanitized evidence in the PR and implementation record. Use commands introduced by the real scaffold; no nonexistent build/test command is asserted here.

## Definition of done

- [ ] All acceptance criteria satisfied, including relevant failure cases.
- [ ] Required predecessors complete; one accountable assignee recorded.
- [ ] Appropriate automated/manual checks run with observed results; limitations explicit.
- [ ] Contract/types/fixtures/docs updated together when changed.
- [ ] No secrets, runtime scan data or local agent installations in the diff.
- [ ] Reviewed PR linked and story/sprint/issue status reconciled.

## Implementation record

Implemented in the Epic 3 batch. See [verification evidence](epic-3-verification.md) for the actual end-of-epic suite, focused corrections, network-disabled ZAP/asset checks and authorized live site result. Broader/rendered acceptance remains a Story 5.2 follow-up; no remote closure is claimed.

[Parent epic](../github-issues/epics/epic-03-review-a-deployed-website-with-zap-and-visible-asset-evidence.md) · [All stories](README.md)

User accepted completion and authorized PR #25 merge on 2026-10-24. Broader independent review and rendered accessibility verification remain tracked in Story 5.2 (#21).
