---
story_id: '1.3'
epic: 1
status: ready-for-dev
prepared: true
approval: pending-user-review
assignee: unassigned
owner_role: "Backend / worker lifecycle"
priority: P0
depends_on: ["1.2"]
blocks: ["1.4", "3.1"]
source: ../planning-artifacts/epics.md
---

# Story 1.3 · Run isolated jobs with owned status and deletion

> **Epic 1** · Required scope · Proposed owner role: **Backend / worker lifecycle** · Actual assignee: **unassigned**

## Summary

Make accepted work private, bounded and observable, including when workers crash or a user deletes a scan.

## User story

As a submitting developer, I want bounded private scans that I can track and delete, so that failures and retained data stay under control.

## Requirements and source of truth

- **FR-10 — Actual tool states**
- **FR-21 — Deletion and access**

**All references:** FR-10, FR-21; NFR-3, NFR-5, NFR-7; UX-DR9; AD-2, AD-5, AD-9, AD-11.

- [Canonical backlog](../planning-artifacts/epics.md) and [PRD](../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 1.2: Accept an authorized bounded source tree](1-2-accept-an-authorized-bounded-source-tree.md)

**Downstream work:**

- [Story 1.4: Detect and sanitize source findings with trusted rules](1-4-detect-and-sanitize-source-findings-with-trusted-rules.md)
- [Story 3.1: Enforce authorized website networking and budgets](3-1-enforce-authorized-website-networking-and-budgets.md)

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [ ] Add the core-owned persisted queue, transactional claim, tool/scan transitions and deadline handling.
- [ ] Launch restricted workers through the trusted launcher with read-only source, bounded scratch and no source-worker network.
- [ ] Enforce ownership, CSRF and idempotency; do not grant API/scanner jobs container-daemon access.
- [ ] Implement tombstone-first deletion, late-write prevention, expiry, crash recovery and truthful cleanup operations.

## Out of scope

- No distributed Redis/Celery queue or public multiuser deployment.
- No claim that a container exists implies its security limits are enforced.

## Acceptance criteria

- [ ] **AC-1** **Given** accepted work, **When** the coordinator claims a job, **Then** one transactional core-owned claim dispatches restricted workers; **And** source is read-only, network disabled, quotas applied and no Docker socket/host secrets reach API or scanner jobs.
- [ ] **AC-2** **Given** duplicate Idempotency-Key requests, **When** retried, **Then** matching payload returns the original Scan and changed payload returns 409; **And** queue/deadline caps produce the documented status/error.
- [ ] **AC-3** **Given** another session, missing CSRF, timeout or coordinator crash, **When** access/recovery occurs, **Then** ownership/CSRF are enforced, abandoned work becomes explicitly failed and scratch cleanup runs.
- [ ] **AC-4** **Given** a running or completed Scan, **When** deletion is requested, **Then** it is immediately inaccessible, late commits are blocked and a deletion operation reports actual cleanup success/failure within policy; **And** expiry follows safety-v1.

## Verification plan

- [ ] Check one-job/queue caps, duplicate/different-payload idempotency and terminal deadlines.
- [ ] Attempt cross-session access and missing/invalid CSRF.
- [ ] Crash a worker/coordinator and delete running/completed scans; verify no late resurrection or hidden cleanup failure.

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

[Parent epic](../github-issues/epics/epic-01-review-a-codebase-safely-and-act-on-real-findings.md) · [All stories](README.md)
