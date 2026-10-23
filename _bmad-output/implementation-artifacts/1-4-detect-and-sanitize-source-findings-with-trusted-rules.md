---
story_id: '1.4'
epic: 1
status: done
prepared: true
approval: pending-user-review
assignee: unassigned
owner_role: "Security / scanner adapters"
priority: P0
depends_on: ["1.3"]
blocks: ["1.5", "2.1", "3.2"]
source: ../planning-artifacts/epics.md
---

# Story 1.4 · Detect and sanitize source findings with trusted rules

> **Epic 1** · Required scope · Proposed owner role: **Security / scanner adapters** · Actual assignee: **unassigned**

## Summary

Produce real source findings that tell the developer where to look while keeping credential values out of reports and logs.

## User story

As a developer, I want real, located source findings without exposed secret values, so that I can identify relevant repairs safely.

## Requirements and source of truth

- **FR-6 — Source checks**
- **FR-7 — Required issue categories**
- **FR-9 — Public-key distinction**
- **FR-10 — Actual tool states**
- **FR-11 — Attributed findings**
- **FR-15 — Credential follow-up**

**All references:** FR-6, FR-7, FR-9, FR-10, FR-11, FR-15; NFR-1, NFR-2; UX-DR5; AD-4, AD-5.

- [Canonical backlog](../planning-artifacts/epics.md) and [PRD](../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 1.3: Run isolated jobs with owned status and deletion](1-3-run-isolated-jobs-with-owned-status-and-deletion.md)

**Downstream work:**

- [Story 1.5: Investigate findings and copy a deterministic repair prompt](1-5-investigate-findings-and-copy-a-deterministic-repair-prompt.md)
- [Story 2.1: Retrieve a bounded public repository snapshot](2-1-retrieve-a-bounded-public-repository-snapshot.md)
- [Story 3.2: Produce located ZAP baseline findings](3-2-produce-located-zap-baseline-findings.md)

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [ ] Integrate trusted Gitleaks and selected Semgrep rules with explicit process/report outcome handling.
- [ ] Build labeled vulnerable/control cases for credentials, unsafe input, configuration and selected access-check candidates.
- [ ] Normalize typed findings and confidence, then redact before storage, logging, UI or model boundaries.
- [ ] Pin reviewed rule/config versions, verify distribution rights and prevent submitted suppressions from silently disabling required checks.

## Out of scope

- No comprehensive authorization/exploitability claim.
- No external AI, dependency scanner or raw vendor-output persistence.

## Acceptance criteria

- [ ] **AC-1** **Given** labeled fake-credential, unsafe-input, insecure-configuration and selected access-check fixtures plus protected/clean controls, **When** trusted Gitleaks/Semgrep rules run, **Then** expected rule/file/line evidence and actual misses/false alarms are recorded; **And** missing access checks remain candidates rather than proven bypasses.
- [ ] **AC-2** **Given** submitted config, ignore files or inline suppressions, **When** scanning, **Then** mandatory trusted checks cannot be silently disabled; **And** approved rule versions, hashes and distribution rights are recorded.
- [ ] **AC-3** **Given** vendor JSON with secret-bearing fields, **When** normalized, **Then** only typed sanitized findings cross persistence/log/API boundaries; **And** fake raw values are absent on tested outward surfaces, including unknown vendor fields.
- [ ] **AC-4** **Given** findings-bearing exits, invalid JSON, missing rules or timeout, **When** interpreted, **Then** findings and execution failures are distinguished; **And** a public browser key is not automatically private and relevant real-secret guidance includes revoke/rotate.

## Verification plan

- [ ] Match expected rule IDs and actual file/line on labeled cases; record misses and false alarms.
- [ ] Use a public-browser-key control and fake private credentials.
- [ ] Test malformed output, timeout, findings-bearing exit codes, malicious suppression and raw-value leakage on outward surfaces.

Record the actual commands, observed results and sanitized evidence in the PR and implementation record. Use commands introduced by the real scaffold; no nonexistent build/test command is asserted here.

## Definition of done

- [ ] All acceptance criteria satisfied, including relevant failure cases.
- [ ] Required predecessors complete; one accountable assignee recorded.
- [ ] Appropriate automated/manual checks run with observed results; limitations explicit.
- [ ] Contract/types/fixtures/docs updated together when changed.
- [ ] No secrets, runtime scan data or local agent installations in the diff.
- [ ] Reviewed PR linked and story/sprint/issue status reconciled.

## Implementation record

Implemented in the source/repository batch on 2026-10-24. See [batch evidence](source-repository-batch-verification.md) for actual checks, live commit attribution and pending review. No GitHub issue or epic was closed. Rendered UI/accessibility acceptance remains pending for UI stories.

[Parent epic](../github-issues/epics/epic-01-review-a-codebase-safely-and-act-on-real-findings.md) · [All stories](README.md)


## Completion acceptance — 2026-10-24

User requested closure after the focused review and verified batch in [PR #23](https://github.com/HemantKumar822/vibeguard/pull/23). Automated and live scanner/repository checks are recorded in the batch evidence. Broader independent review and rendered keyboard/360px/200%-zoom/reduced-motion checks are deferred to Story 5.2 (#21); they are not claimed as performed.
