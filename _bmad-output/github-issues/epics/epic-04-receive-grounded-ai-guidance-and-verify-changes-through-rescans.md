# Epic 4 · Receive grounded AI guidance and verify changes through rescans

## User outcome

Users optionally enable sanitized AI explanation, then genuinely repeat all supported input modes and compare observations without false repair claims.

## Requirements and governing decisions

- **Functional requirements:** FR-13, FR-14, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20.
- **Quality requirements:** NFR-1, NFR-5, NFR-7.
- **UX requirements:** UX-DR6, UX-DR7, UX-DR13, UX-DR14, UX-DR15, UX-DR17, UX-DR18.
- **Architecture decisions:** AD-2, AD-3, AD-8, AD-9, AD-10.

## Delivery stories

- [ ] [Story 4.1: Add opt-in bounded AI explanations with fallback](../../implementation-artifacts/4-1-add-opt-in-bounded-ai-explanations-with-fallback.md)
- [ ] [Story 4.2: Execute real rescans and classify comparable findings](../../implementation-artifacts/4-2-execute-real-rescans-and-classify-comparable-findings.md)
- [ ] [Story 4.3: Inspect paired rescan evidence and recovery](../../implementation-artifacts/4-3-inspect-paired-rescan-evidence-and-recovery.md)

## Dependencies and ownership

**Earlier-story prerequisites:** [Story 1.5](../../implementation-artifacts/1-5-investigate-findings-and-copy-a-deterministic-repair-prompt.md), [Story 2.2](../../implementation-artifacts/2-2-review-repository-findings-with-commit-attribution.md), [Story 3.4](../../implementation-artifacts/3-4-investigate-website-findings-in-the-shared-workspace.md)

Assign one accountable owner per child story. Use each story’s dependency links to coordinate parallel work and integration. Claim actual owners on GitHub; preserve acceptance before closing work.

## Epic acceptance

- [ ] Every linked child story meets its acceptance criteria with reviewed evidence.
- [ ] The user outcome works end to end on real authorized inputs.
- [ ] Required failure/recovery, privacy and safety boundaries are exercised.
- [ ] Evidence and metrics state actual coverage and limitations.
- [ ] Relevant documentation and sprint/GitHub statuses agree.

## Scope rules

Preserve the required codebase, repository and ZAP website flow, masked evidence, repair guidance and genuine rescans. Optional features never replace required safety or a required mode. No claim of completion from planning documents alone.

[Canonical epic backlog](../../planning-artifacts/epics.md) · [Team story board](../README.md)
