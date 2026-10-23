---
story_id: '2.1'
epic: 2
status: ready-for-dev
prepared: true
approval: pending-user-review
assignee: unassigned
owner_role: "Backend / repository adapter"
priority: P0
depends_on: ["1.4"]
blocks: ["2.2"]
source: ../planning-artifacts/epics.md
---

# Story 2.1 · Retrieve a bounded public repository snapshot

> **Epic 2** · Required scope · Proposed owner role: **Backend / repository adapter** · Actual assignee: **unassigned**

## Summary

Review exactly one public repository revision through the existing source pipeline, without asking the user to upload it manually.

## User story

As a developer, I want to select a public repository and reference, so that the review identifies the exact source revision assessed.

## Requirements and source of truth

- **FR-3 — Repository submission**
- **FR-5 — Recognized scope**
- **FR-10 — Actual tool states**

**All references:** FR-3, FR-5, FR-10; NFR-3, NFR-4; AD-6, AD-11.

- [Canonical backlog](../planning-artifacts/epics.md) and [PRD](../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Blocked by — finish these first:**

- [Story 1.4: Detect and sanitize source findings with trusted rules](1-4-detect-and-sanitize-source-findings-with-trusted-rules.md)

**Unblocks:**

- [Story 2.2: Review repository findings with commit attribution](2-2-review-repository-findings-with-commit-attribution.md)

A prepared story is not automatically unblocked. Do not mark it in progress while required predecessors remain unfinished; discuss any contract-only parallel task separately.

## In scope / implementation checklist

- [ ] Parse only the approved public GitHub identity/ref and resolve a full commit through fixed provider endpoints.
- [ ] Download a bounded snapshot with actual-destination/redirect checks and the shared safe extractor.
- [ ] Feed the validated tree to the existing source scanners and record commit/inventory/coverage.

## Out of scope

- No arbitrary git clone arguments, hooks, submodule/LFS following, private credentials or history scan.
- Do not bypass source intake limits because the source came from GitHub.

## Acceptance criteria

- [ ] **AC-1** **Given** an allowed GitHub HTTPS identity/ref, **When** retrieved, **Then** fixed provider endpoints resolve a full commit and bounded archive; **And** only permitted public destinations/redirects are contacted.
- [ ] **AC-2** **Given** unsafe URL/ref, credential-bearing URL, blocked redirect, traversal/link archive, size/ratio abuse or timeout, **When** retrieved/extracted, **Then** validation rejects safely under safety-v1 with explicit failure rather than an empty successful scan.
- [ ] **AC-3** **Given** a valid snapshot, **When** passed through shared intake and scanners, **Then** source inventory, exclusions and attributed findings match equivalent uploaded source; **And** no clone hooks, submodule/LFS retrieval, install or build runs.

## Verification plan

- [ ] Compare seeded findings for an uploaded tree and equivalent repository commit.
- [ ] Reject credential-bearing/unsupported URLs, missing refs and unsafe redirects.
- [ ] Test malicious archive paths, expansion/size limits and retrieval timeouts.

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

[Parent epic](../github-issues/epics/epic-02-review-a-repository-revision-without-manual-upload.md) · [All stories](README.md)
