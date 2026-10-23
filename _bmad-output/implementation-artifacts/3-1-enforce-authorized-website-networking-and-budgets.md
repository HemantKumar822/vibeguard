---
story_id: '3.1'
epic: 3
status: ready-for-dev
prepared: true
approval: pending-user-review
assignee: unassigned
owner_role: "Security / networking"
priority: P0
depends_on: ["1.3"]
blocks: ["3.2"]
source: ../planning-artifacts/epics.md
---

# Story 3.1 · Enforce authorized website networking and budgets

> **Epic 3** · Required scope · Proposed owner role: **Security / networking** · Actual assignee: **unassigned**

## Summary

Prove URL scanning cannot reach internal systems or exceed the approved request/byte/time scope before enabling arbitrary targets.

## User story

As a developer, I want URL checks restricted to permitted destinations and scope, so that a submission cannot access internal systems or crawl without limits.

## Requirements and source of truth

- **FR-4 — Website submission**

**All references:** FR-4; NFR-3, NFR-4, NFR-7; AD-7, AD-11, AD-12.

- [Canonical backlog](../planning-artifacts/epics.md) and [PRD](../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 1.3: Run isolated jobs with owned status and deletion](1-3-run-isolated-jobs-with-owned-status-and-deletion.md)

**Downstream work:**

- [Story 3.2: Produce located ZAP baseline findings](3-2-produce-located-zap-baseline-findings.md)

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [ ] Create the dedicated ZAP/asset network path with no bypass route and no public ZAP control API.
- [ ] Enforce actual public destinations at connection time, including DNS changes, redirects and IPv4/IPv6 edge cases.
- [ ] Enforce shared pre-send request and response-byte/time budgets under safety-v1.
- [ ] Document the tested enforcement mechanism and fail closed when runtime capability is missing.

## Out of scope

- No active attacks, authenticated sessions or broader-origin crawling.
- No hostname precheck or permission checkbox presented as network isolation.

## Acceptance criteria

- [ ] **AC-1** **Given** an allowed public origin, **When** ZAP/asset traffic connects, **Then** all traffic uses enforced connection-time public-destination checks and trusted request/response counters; **And** direct egress is blocked and ZAP control is private.
- [ ] **AC-2** **Given** private/reserved/metadata addresses, mapped IPv6, DNS rebinding, unsafe redirects, alternate ports or over-budget responses, **When** attempted, **Then** connections are rejected/terminated under safety-v1 and coverage is explicitly incomplete.
- [ ] **AC-3** **Given** the selected runtime cannot demonstrate these controls, **When** readiness is checked, **Then** arbitrary URL submission stays disabled and the missing required capability is reported; **And** fixture-only operation is not declared delivery.

## Verification plan

- [ ] Demonstrate allowed authorized-origin traffic through the selected runtime.
- [ ] Block internal/reserved/metadata/mapped-IPv6/rebinding/redirect cases and direct egress.
- [ ] Exceed each shared crawl/network budget and verify termination plus incomplete coverage.

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

[Parent epic](../github-issues/epics/epic-03-review-a-deployed-website-with-zap-and-visible-asset-evidence.md) · [All stories](README.md)
