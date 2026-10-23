---
story_id: '3.3'
epic: 3
status: review
prepared: true
approval: pending-user-review
assignee: unassigned
owner_role: "Security / asset analysis"
priority: P0
depends_on: ["3.2"]
blocks: ["3.4"]
source: ../planning-artifacts/epics.md
---

# Story 3.3 · Detect secrets in bounded visible assets

> **Epic 3** · Required scope · Proposed owner role: **Security / asset analysis** · Actual assignee: **unassigned**

## Summary

Detect private-credential candidates in browser-visible text assets and show the actual asset location with values masked.

## User story

As a developer, I want exposed browser-readable credentials identified, so that deployment-visible risks are not missed by relying on ZAP alerts alone.

## Requirements and source of truth

- **FR-8 — Browser-visible secrets**
- **FR-9 — Public-key distinction**
- **FR-10 — Actual tool states**
- **FR-11 — Attributed findings**

**All references:** FR-8, FR-9, FR-10, FR-11; NFR-1, NFR-4; AD-4, AD-7.

- [Canonical backlog](../planning-artifacts/epics.md) and [PRD](../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 3.2: Produce located ZAP baseline findings](3-2-produce-located-zap-baseline-findings.md)

**Downstream work:**

- [Story 3.4: Investigate website findings in the shared workspace](3-4-investigate-website-findings-in-the-shared-workspace.md)

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [ ] Collect only bounded same-origin linked text assets through the same enforced egress/budget controls.
- [ ] Run the trusted secret detector on temporary text and map safe evidence back to asset URLs/real text lines.
- [ ] Record exclusions and clean up raw asset/temporary scanner data before outward persistence.

## Out of scope

- No JavaScript execution, unlimited asset recursion or cross-origin harvesting.
- Do not call unvisited/runtime-loaded assets assessed or classify all public keys as secrets.

## Acceptance criteria

- [ ] **AC-1** **Given** same-origin linked text assets with a planted fake private credential, **When** fetched/scanned through the enforced network and trusted detector, **Then** masked asset URL/actual text location evidence is returned and temporary filenames are mapped correctly.
- [ ] **AC-2** **Given** public-key controls, runtime-loaded/unvisited or cross-origin assets, **When** assessed, **Then** no automatic private-key claim occurs and omitted coverage is explicit; **And** no JavaScript/application code executes.
- [ ] **AC-3** **Given** asset/request/byte/time/output bounds or sanitization failure, **When** exceeded, **Then** the asset check is incomplete, raw values do not reach outward channels and overall completeness reflects the failure.

## Verification plan

- [ ] Find a fake private key in a served asset with masked URL/evidence.
- [ ] Use public-key, cross-origin and runtime-only controls to verify confidence/exclusion behavior.
- [ ] Exercise shared limits and sanitizer failure; inspect reports/logs/model inputs/clipboard surfaces for raw values.

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
