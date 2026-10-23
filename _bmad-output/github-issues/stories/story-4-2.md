# Story 4.2 · Execute real rescans and classify comparable findings

> **Epic 4** · Required scope · Proposed owner role: **Backend / comparison** · Actual assignee: **unassigned**

## Summary

Execute the checks again for corrected input and classify changes only where the new observations are genuinely comparable to the baseline.

## User story

As a developer, I want a corrected submission assessed again against its baseline, so that changes are supported by comparable evidence.

## Requirements and source of truth

- **FR-16 — Real repeat execution**
- **FR-17 — Honest classifications**
- **FR-18 — Comparison evidence**

**All references:** FR-16, FR-17, FR-18; NFR-5; AD-2, AD-8, AD-9.

- [Canonical backlog](../../planning-artifacts/epics.md) and [PRD](../../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Blocked by — finish these first:**

- [Story 2.2: Review repository findings with commit attribution](../../implementation-artifacts/2-2-review-repository-findings-with-commit-attribution.md)
- [Story 3.4: Investigate website findings in the shared workspace](../../implementation-artifacts/3-4-investigate-website-findings-in-the-shared-workspace.md)

**Unblocks:**

- [Story 4.3: Inspect paired rescan evidence and recovery](../../implementation-artifacts/4-3-inspect-paired-rescan-evidence-and-recovery.md)

A prepared story is not automatically unblocked. Do not mark it in progress while required predecessors remain unfinished; discuss any contract-only parallel task separately.

## In scope / implementation checklist

- [ ] Create owned same-mode repeat scans with recorded lineage and new revision/observation.
- [ ] Prototype and test the source scan-repair-rescan loop after 1.5; retain all final dependencies and all-mode acceptance before completing this story.
- [ ] Implement coverage/rule/policy-aware matching using safe structural context instead of line-only or secret-derived public IDs.
- [ ] Return the four comparison classifications, reasons, paired evidence and retained human actions.

## Out of scope

- No stale-result reuse or cross-mode clearing of source findings.
- No verified_fixed label without a separate repeatable behavior-proof test.

## Acceptance criteria

- [ ] **AC-1** **Given** source/repository/website baselines, **When** corrected same-mode inputs are submitted, **Then** actual scanners execute in new owned Scans with revision/observation and lineage; **And** baselines are preserved.
- [ ] **AC-2** **Given** compatible rules/scope and deterministic matches, **When** compared, **Then** still_detected/not_detected/newly_detected are correct for labeled cases; **And** shifted lines alone do not imply repair.
- [ ] **AC-3** **Given** failed tools, lost pages, changed fingerprints, ambiguous duplicate matches or cross-mode input, **When** comparison is requested, **Then** uncertainty yields unverified or the contract's conflict response; **And** URL results never clear source findings.
- [ ] **AC-4** **Given** no behavior-proof test, **When** a finding disappears, **Then** verified_fixed is never emitted and relevant baseline human rotation actions remain available.

## Verification plan

- [ ] Run actual corrected repeats for codebase, repository and website modes.
- [ ] Test shifted lines, stable matches, removed/new findings and ambiguous duplicates.
- [ ] Test failed checks, lost pages, changed versions/policy, wrong lineage and inaccessible/deleted baselines.

Record the actual commands, observed results and sanitized evidence in the PR and implementation record. Use commands introduced by the real scaffold; no nonexistent build/test command is asserted here.

## Definition of done

- [ ] All acceptance criteria satisfied, including relevant failure cases.
- [ ] Required predecessors complete; one accountable assignee recorded.
- [ ] Appropriate automated/manual checks run with observed results; limitations explicit.
- [ ] Contract/types/fixtures/docs updated together when changed.
- [ ] No secrets, runtime scan data or local agent installations in the diff.
- [ ] Reviewed PR linked and story/sprint/issue status reconciled.

[Implementation handoff](../../implementation-artifacts/4-2-execute-real-rescans-and-classify-comparable-findings.md)
