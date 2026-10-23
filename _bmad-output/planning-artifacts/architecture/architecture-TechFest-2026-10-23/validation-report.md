# Architecture checks and handoff

Date: 2026-10-23. Result: **architecture planning complete; ready for epics/stories**. No worker/runtime/network implementation or security assurance is claimed.

## Evidence and scope

The PRD's 21 FRs and seven NFRs are represented in the spine's capability map. UX remains the visual/behavioral authority. Codebase, repository and website are all required; website uses ZAP plus the explicit browser-asset credential pass. Source/repository are not conflated with deployed backend visibility.

The single API contract fixes mode-specific intake, typed evidence, coverage, required tool sets, failure states, idempotency, session ownership, deletion and comparison. The safety profile fixes finite budgets and retention, with enforcement tests required before delivery. Design/runtime choices are fast-path assumptions, not user approval.

## Direct reviewer checks

Following the user's speed/no-subagent preference, the configured freshness and incompatible-unit lenses and rubric were applied directly rather than independently dispatched. This is an author check; it does not count as independent review.

| Lens | Result / remaining build gate |
| --- | --- |
| Mechanical spine lint | PASS: 12 unique ascending ADs, required fields present, no template placeholders or missing Stack versions; zero findings in `lint-results.json` |
| Technology freshness | Official registry/release metadata checked; Python/SQLite observed locally. Candidate versions are pinned in seed, but install/build compatibility and container digests remain bootstrap evidence |
| Incompatible frontend/adapters | Closed drift points through AD-3 and API-CONTRACT: one status/coverage/location shape and generated types/fixtures |
| Incompatible mutation paths | AD-2 and AD-9 make core the only state owner, transactional claims and tombstone checks prevent duplicate/late writes |
| Comparison ambiguity | AD-8 and contract distinguish stable match from absence conclusions, page coverage and changed-policy uncertainty; cross-mode clearing prohibited |
| Security boundary | Source network disabled; URL egress separate; repository shares validation; raw evidence never crosses persistence boundary; opt-in model cannot execute tools |
| Operational breadth | Loopback single-team deployment, session access, private runtime storage, crash recovery, expiry/deletion, queue/deadline/resource limits and public-release gates explicit |
| Source reconciliation | Preserves real evidence, manual rotation, fallback, graphical UX and all required modes; reference ZIP-only/optional-ZAP and conflicting API/raw-storage proposals remain superseded |

`checks.json` confirms local links, sources/companions and AD continuity. No Mermaid renderer, dependency installation, rule detection, full API-schema implementation or runtime isolation was tested. Diagram syntax was inspected directly.

## Implementation risks to schedule first

1. Verify available container runtime and pinned tool/startup compatibility. The API must not receive the Docker socket.
2. Prove ZAP/asset traffic cannot bypass actual-destination and request/byte/time enforcement; startup hostname checks alone are insufficient.
3. Validate minimal trusted rules for all required categories, public-key controls and browser-visible fake credentials; include licensing and suppression tests.
4. Generate API schema/frontend types and fixtures from this contract before independent UI/backend integration.
5. Exercise session/CSRF/idempotency/deletion/crash cleanup and coverage-aware rescan behavior using the finite profile.

These are build acceptance tasks, not unrecorded architecture choices. Failed feasibility blocks required-mode delivery rather than silently shrinking scope. A labeled team-fixture fallback cannot be advertised as arbitrary-user readiness.

## Memlog accounting and next step

The memlog captures the paradigm trade-off, three-mode requirement, direct-review override, AD ownership/security/compare rules, local-deployment assumptions and version evidence. Invariants are distilled into the spine; shared data and numerical policy are in companions. No extra deck or speculative provider architecture was produced. External handoffs/hooks are empty.

**Next: `bmad-create-epics-and-stories`. Three planning/setup stages remain:** epics/stories → sprint readiness/tracking → repository/GitHub setup with final consistency audit. The existing PRD already supplies the requirements contract, so adding another spec stage is optional and unnecessary for this fast path.
