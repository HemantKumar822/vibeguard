# Epic 3 · Review a deployed website with ZAP and visible-asset evidence

## User outcome

Users scan an authorized public deployment, understand passive coverage and inspect ZAP plus browser-visible credential observations.

## Requirements and governing decisions

- **Functional requirements:** FR-1, FR-4, FR-5, FR-7, FR-8, FR-9, FR-10, FR-11, FR-12, FR-14, FR-19, FR-20.
- **Quality requirements:** NFR-1, NFR-3, NFR-4, NFR-7.
- **UX requirements:** UX-DR1, UX-DR2, UX-DR3, UX-DR5, UX-DR6, UX-DR15, UX-DR18.
- **Architecture decisions:** AD-1, AD-3, AD-4, AD-7, AD-11, AD-12.

## Delivery stories

- [ ] [Story 3.1: Enforce authorized website networking and budgets](../../implementation-artifacts/3-1-enforce-authorized-website-networking-and-budgets.md)
- [ ] [Story 3.2: Produce located ZAP baseline findings](../../implementation-artifacts/3-2-produce-located-zap-baseline-findings.md)
- [ ] [Story 3.3: Detect secrets in bounded visible assets](../../implementation-artifacts/3-3-detect-secrets-in-bounded-visible-assets.md)
- [ ] [Story 3.4: Investigate website findings in the shared workspace](../../implementation-artifacts/3-4-investigate-website-findings-in-the-shared-workspace.md)

## Dependencies and ownership

**Earlier-story prerequisites:** [Story 1.3](../../implementation-artifacts/1-3-run-isolated-jobs-with-owned-status-and-deletion.md), [Story 1.4](../../implementation-artifacts/1-4-detect-and-sanitize-source-findings-with-trusted-rules.md), [Story 1.5](../../implementation-artifacts/1-5-investigate-findings-and-copy-a-deterministic-repair-prompt.md)

Assign one accountable owner per child story. Use each story’s Blocked by / Unblocks links; do not assume all children can start together. Actual assignees and GitHub issue numbers remain unset.

## Epic acceptance

- [ ] Every linked child story meets its acceptance criteria with reviewed evidence.
- [ ] The user outcome works end to end on real authorized inputs.
- [ ] Required failure/recovery, privacy and safety boundaries are exercised.
- [ ] Evidence and metrics state actual coverage and limitations.
- [ ] Relevant documentation and sprint/GitHub statuses agree.

## Scope rules

Preserve the required codebase, repository and ZAP website flow, masked evidence, repair guidance and genuine rescans. Optional features never replace required safety or a required mode. No claim of completion from planning documents alone.

[Canonical epic backlog](../../planning-artifacts/epics.md) · [Team story board](../README.md)
