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

- [Canonical backlog](../../planning-artifacts/epics.md) and [PRD](../../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 1.5: Investigate findings and copy a deterministic repair prompt](../../implementation-artifacts/1-5-investigate-findings-and-copy-a-deterministic-repair-prompt.md)

**Downstream work:**

- No direct successor; completion contributes to its epic acceptance.

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [ ] Connect a server-configured provider behind the bounded explanation port and explicit per-submission opt-in.
- [ ] Send sanitized structured findings only and validate returned IDs/locations/output shape.
- [ ] Keep core-owned master prompt composition and deterministic fallback, including all relevant human rotation actions.

## Out of scope

- No model-controlled scanning, commands, new findings or raw-source upload.
- No automatic retries or silent widening of sharing/size limits.

## Acceptance criteria

- [ ] **AC-1** **Given** sharing disabled, **When** a report is composed, **Then** no external request occurs and deterministic guidance remains usable.
- [ ] **AC-2** **Given** sharing enabled and a configured provider, **When** bounded sanitized findings are sent once, **Then** only valid existing IDs/locations are accepted and core composes the master prompt; **And** injected source/page instructions cannot trigger tools or widen sharing.
- [ ] **AC-3** **Given** timeout, invalid/invented output, unavailable provider or limit overflow, **When** processed, **Then** deterministic guidance covers affected/remaining Findings with an explicit reason and preserves rotation advice.

## Verification plan

- [ ] Assert no model request when sharing is off.
- [ ] Inspect the enabled request for bounded sanitized evidence and test valid explanation output.
- [ ] Test timeout/invented IDs/locations/invalid response/prompt injection and confirm usable honest fallback.

Record the actual commands, observed results and sanitized evidence in the PR and implementation record. Use commands introduced by the real scaffold; no nonexistent build/test command is asserted here.

## Definition of done

- [ ] All acceptance criteria satisfied, including relevant failure cases.
- [ ] Required predecessors complete; one accountable assignee recorded.
- [ ] Appropriate automated/manual checks run with observed results; limitations explicit.
- [ ] Contract/types/fixtures/docs updated together when changed.
- [ ] No secrets, runtime scan data or local agent installations in the diff.
- [ ] Reviewed PR linked and story/sprint/issue status reconciled.

[Implementation handoff](../../implementation-artifacts/4-1-add-opt-in-bounded-ai-explanations-with-fallback.md)
