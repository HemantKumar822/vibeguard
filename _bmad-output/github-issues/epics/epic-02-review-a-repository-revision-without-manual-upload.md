# Epic 2 · Review a repository revision without manual upload

## User outcome

Users retrieve a public repository snapshot and receive the same trustworthy source review with resolved commit attribution.

## Requirements and governing decisions

- **Functional requirements:** FR-1, FR-3, FR-5, FR-10, FR-11, FR-19.
- **Quality requirements:** NFR-3, NFR-4.
- **UX requirements:** UX-DR1, UX-DR3, UX-DR15, UX-DR18.
- **Architecture decisions:** AD-1, AD-3, AD-6, AD-11.

## Delivery stories

- [ ] [Story 2.1: Retrieve a bounded public repository snapshot](../../implementation-artifacts/2-1-retrieve-a-bounded-public-repository-snapshot.md)
- [ ] [Story 2.2: Review repository findings with commit attribution](../../implementation-artifacts/2-2-review-repository-findings-with-commit-attribution.md)

## Dependencies and ownership

**Earlier-story prerequisites:** [Story 1.4](../../implementation-artifacts/1-4-detect-and-sanitize-source-findings-with-trusted-rules.md), [Story 1.5](../../implementation-artifacts/1-5-investigate-findings-and-copy-a-deterministic-repair-prompt.md)

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
