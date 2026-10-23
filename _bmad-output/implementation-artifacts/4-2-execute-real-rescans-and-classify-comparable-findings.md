---
story_id: '4.2'
epic: 4
status: review
prepared: true
approval: approved-epic-batch
assignee: unassigned
owner_role: "Backend / comparison"
priority: P0
depends_on: ["2.2", "3.4"]
blocks: ["4.3"]
source: ../planning-artifacts/epics.md
---

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

- [Canonical backlog](../planning-artifacts/epics.md) and [PRD](../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 2.2: Review repository findings with commit attribution](2-2-review-repository-findings-with-commit-attribution.md)
- [Story 3.4: Investigate website findings in the shared workspace](3-4-investigate-website-findings-in-the-shared-workspace.md)

**Downstream work:**

- [Story 4.3: Inspect paired rescan evidence and recovery](4-3-inspect-paired-rescan-evidence-and-recovery.md)

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [x] Create owned same-mode repeat scans with recorded lineage and new revision/observation.
- [x] Prototype and test the source scan-repair-rescan loop after 1.5; retain all final dependencies and all-mode acceptance before completing this story.
- [x] Implement coverage/rule/policy-aware matching using safe structural context instead of line-only or secret-derived public IDs.
- [x] Return the four comparison classifications, reasons, paired evidence and retained human actions.

## Out of scope

- No stale-result reuse or cross-mode clearing of source findings.
- No verified_fixed label without a separate repeatable behavior-proof test.

## Acceptance criteria

- [x] **AC-1** **Given** source/repository/website baselines, **When** corrected same-mode inputs are submitted, **Then** actual scanners execute in new owned Scans with revision/observation and lineage; **And** baselines are preserved.
- [x] **AC-2** **Given** compatible rules/scope and deterministic matches, **When** compared, **Then** still_detected/not_detected/newly_detected are correct for labeled cases; **And** shifted lines alone do not imply repair.
- [x] **AC-3** **Given** failed tools, lost pages, changed fingerprints, ambiguous duplicate matches or cross-mode input, **When** comparison is requested, **Then** uncertainty yields unverified or the contract's conflict response; **And** URL results never clear source findings.
- [x] **AC-4** **Given** no behavior-proof test, **When** a finding disappears, **Then** verified_fixed is never emitted and relevant baseline human rotation actions remain available.

## Verification plan

- [x] Run actual corrected repeats for codebase, repository and website modes.
- [x] Test shifted lines, stable matches, removed/new findings and ambiguous duplicates.
- [x] Test failed checks, lost pages, changed versions/policy, wrong lineage and inaccessible/deleted baselines.

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
