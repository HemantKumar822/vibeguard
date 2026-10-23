---
story_id: '4.1'
epic: 4
status: review
prepared: true
approval: approved-epic-batch
assignee: unassigned
owner_role: "Backend / AI integration"
priority: P0
depends_on: ["1.5"]
blocks: []
source: ../planning-artifacts/epics.md
---

# Story 4.1 · Add opt-in bounded AI explanations with fallback

> **Epic 4** · Required scope · Proposed owner role: **Backend / AI integration** · Actual assignee: **unassigned**

## Summary

Offer clearer AI-assisted explanations only when the user chooses sharing, while keeping evidence and the repair prompt usable if the model fails.

## User story

As a developer, I want optional AI explanations grounded in my findings, so that repair advice is understandable without sharing raw source or losing the fallback.

## Requirements and source of truth

- **FR-13 — Grounded explanations**
- **FR-14 — Consolidated repair prompt**
- **FR-15 — Credential follow-up**
- **FR-20 — Authorization and data choice**

**All references:** FR-13, FR-14, FR-15, FR-20; NFR-1, NFR-7; UX-DR6; AD-10.

- [Canonical backlog](../planning-artifacts/epics.md) and [PRD](../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 1.5: Investigate findings and copy a deterministic repair prompt](1-5-investigate-findings-and-copy-a-deterministic-repair-prompt.md)

**Downstream work:**

- No direct successor; completion contributes to its epic acceptance.

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [x] Connect a server-configured provider behind the bounded explanation port and explicit per-submission opt-in.
- [x] Send sanitized structured findings only and validate returned IDs/locations/output shape.
- [x] Keep core-owned master prompt composition and deterministic fallback, including all relevant human rotation actions.

## Out of scope

- No model-controlled scanning, commands, new findings or raw-source upload.
- No automatic retries or silent widening of sharing/size limits.

## Acceptance criteria

- [x] **AC-1** **Given** sharing disabled, **When** a report is composed, **Then** no external request occurs and deterministic guidance remains usable.
- [x] **AC-2** **Given** sharing enabled and a configured provider, **When** bounded sanitized findings are sent once, **Then** only valid existing IDs/locations are accepted and core composes the master prompt; **And** injected source/page instructions cannot trigger tools or widen sharing.
- [x] **AC-3** **Given** timeout, invalid/invented output, unavailable provider or limit overflow, **When** processed, **Then** deterministic guidance covers affected/remaining Findings with an explicit reason and preserves rotation advice.

## Verification plan

- [x] Assert no model request when sharing is off.
- [x] Inspect the enabled request for bounded sanitized evidence and test valid explanation output.
- [x] Test timeout/invented IDs/locations/invalid response/prompt injection and confirm usable honest fallback.

Record the actual commands, observed results and sanitized evidence in the PR and implementation record. Use commands introduced by the real scaffold; no nonexistent build/test command is asserted here.

## Definition of done

- [ ] All acceptance criteria satisfied, including relevant failure cases.
- [ ] Required predecessors complete; one accountable assignee recorded.
- [ ] Appropriate automated/manual checks run with observed results; limitations explicit.
- [ ] Contract/types/fixtures/docs updated together when changed.
- [ ] No secrets, runtime scan data or local agent installations in the diff.
- [ ] Reviewed PR linked and story/sprint/issue status reconciled.

## Implementation record

Implementation integrated for review in the Epic 4 batch (2026-10-24). Added optional bounded explanation port and deterministic fallback, real same-mode rescan admission with immutable lineage, conservative comparison, baseline-preserving paired evidence UI, and matrix/actual-worker smoke tests. Python syntax compilation and contract export/type generation succeeded. Batch verification, review patches, measured website readiness and actual pinned all-mode repeat smoke are complete; exact results and limitations are recorded in epic-4-verification.md. No live paid provider call or public-network repeat acceptance is claimed. See docs/DEVELOPMENT.md and spec-epic-4-ai-rescan-comparison.md for protocol, bounds and evidence commands.

[Parent epic](../github-issues/epics/epic-04-receive-grounded-ai-guidance-and-verify-changes-through-rescans.md) · [All stories](README.md)

### Batch verification completed

Implementation and review patches verified with one broad integration run and focused reruns only. See [Epic 4 evidence](epic-4-verification.md) for exact commands/results and live-provider/browser limitations. Ready for teammate/PR review; no remote issue closure is claimed.
