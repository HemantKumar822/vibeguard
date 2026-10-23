# Story 3.2 · Produce located ZAP baseline findings

> **Epic 3** · Required scope · Proposed owner role: **Security / ZAP adapter** · Actual assignee: **unassigned**

## Summary

Turn a real ZAP baseline into understandable deployment findings, without treating alerts or a failed crawl as successful security verification.

## User story

As a developer, I want real passive deployment observations, so that exposed configuration risks have actionable URL evidence.

## Requirements and source of truth

- **FR-4 — Website submission**
- **FR-7 — Required issue categories**
- **FR-10 — Actual tool states**
- **FR-11 — Attributed findings**

**All references:** FR-4, FR-7, FR-10, FR-11; AD-1, AD-3, AD-7.

- [Canonical backlog](../../planning-artifacts/epics.md) and [PRD](../../planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md).
- [Architecture decisions](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md), [API contract](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) and [safety-v1](../../planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md).
- [Visual contract](../../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) and [behavior/state contract](../../planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md).

## Dependencies

**Depends on — coordination guidance:**

- [Story 3.1: Enforce authorized website networking and budgets](../../implementation-artifacts/3-1-enforce-authorized-website-networking-and-budgets.md)
- [Story 1.4: Detect and sanitize source findings with trusted rules](../../implementation-artifacts/1-4-detect-and-sanitize-source-findings-with-trusted-rules.md)

**Downstream work:**

- [Story 3.3: Detect secrets in bounded visible assets](../../implementation-artifacts/3-3-detect-secrets-in-bounded-visible-assets.md)

Dependencies are coordination guidance. Team members may start parallel work by agreeing shared contracts and ownership; acceptance and integration must still satisfy the listed prerequisites. No native GitHub blockers are used.

## In scope / implementation checklist

- [ ] Run the pinned passive/baseline profile through the enforced network path.
- [ ] Normalize real alert IDs, sanitized web locations and assessed/excluded resources.
- [ ] Distinguish WARN/FAIL finding-bearing exits from execution/JSON/timeout failures.

## Out of scope

- No active ZAP scan, authenticated crawl or private backend-source inference.
- No broad exposed-secret promise from stock ZAP alone.

## Acceptance criteria

- [ ] **AC-1** **Given** a controlled vulnerable site, **When** pinned ZAP baseline runs, **Then** actual alert IDs, sanitized URL/header/response evidence, version/policy and visited/excluded resources are normalized; **And** no active attacks or private-source claims occur.
- [ ] **AC-2** **Given** WARN/FAIL finding exits, execution error, invalid/truncated JSON or timeout, **When** adapted, **Then** valid findings and execution failure are distinguished and no failed crawl becomes clean success.
- [ ] **AC-3** **Given** a corrected/clean deployment, **When** checked, **Then** actual expected alerts and other observed warnings are recorded without suppressing inconvenient output.

## Verification plan

- [ ] Scan a controlled vulnerable deployment and assert actual alert/location evidence.
- [ ] Scan corrected/clean variants and retain any additional observed warnings.
- [ ] Test finding exits, broken/truncated JSON and timeout; verify truthful partial/failed coverage.

Record the actual commands, observed results and sanitized evidence in the PR and implementation record. Use commands introduced by the real scaffold; no nonexistent build/test command is asserted here.

## Definition of done

- [ ] All acceptance criteria satisfied, including relevant failure cases.
- [ ] Required predecessors complete; one accountable assignee recorded.
- [ ] Appropriate automated/manual checks run with observed results; limitations explicit.
- [ ] Contract/types/fixtures/docs updated together when changed.
- [ ] No secrets, runtime scan data or local agent installations in the diff.
- [ ] Reviewed PR linked and story/sprint/issue status reconciled.

[Implementation handoff](../../implementation-artifacts/3-2-produce-located-zap-baseline-findings.md)
