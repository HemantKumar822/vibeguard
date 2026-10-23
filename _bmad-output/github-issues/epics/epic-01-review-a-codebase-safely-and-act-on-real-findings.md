# Epic 1 · Review a codebase safely and act on real findings

## User outcome

Users submit source, inspect masked scanner evidence, copy deterministic repair guidance and control access/deletion. Foundation work stays inside this end-to-end user outcome.

## Requirements and governing decisions

- **Functional requirements:** FR-1, FR-2, FR-5, FR-6, FR-7, FR-9, FR-10, FR-11, FR-12, FR-14, FR-15, FR-19, FR-20, FR-21.
- **Quality requirements:** NFR-1, NFR-2, NFR-3, NFR-5, NFR-6, NFR-7.
- **UX requirements:** UX-DR1, UX-DR2, UX-DR3, UX-DR4, UX-DR5, UX-DR6, UX-DR8, UX-DR9, UX-DR10, UX-DR11, UX-DR12, UX-DR13, UX-DR14, UX-DR15, UX-DR16, UX-DR17, UX-DR18.
- **Architecture decisions:** AD-1, AD-2, AD-3, AD-4, AD-5, AD-9, AD-11, AD-12.

## Delivery stories

- [ ] [Story 1.1: Set up initial project from starter template and freeze contracts](../../implementation-artifacts/1-1-set-up-initial-project-from-starter-template-and-freeze-contracts.md)
- [ ] [Story 1.2: Accept an authorized bounded source tree](../../implementation-artifacts/1-2-accept-an-authorized-bounded-source-tree.md)
- [ ] [Story 1.3: Run isolated jobs with owned status and deletion](../../implementation-artifacts/1-3-run-isolated-jobs-with-owned-status-and-deletion.md)
- [ ] [Story 1.4: Detect and sanitize source findings with trusted rules](../../implementation-artifacts/1-4-detect-and-sanitize-source-findings-with-trusted-rules.md)
- [ ] [Story 1.5: Investigate findings and copy a deterministic repair prompt](../../implementation-artifacts/1-5-investigate-findings-and-copy-a-deterministic-repair-prompt.md)

## Dependencies and ownership

**Earlier-story prerequisites:** None; this epic establishes the starting workflow.

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
