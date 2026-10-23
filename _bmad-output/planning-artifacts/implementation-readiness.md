# Implementation readiness — TechFest

Date: 2026-10-23. Intent: full sprint planning. **Gate: PASS for beginning the recorded implementation plan.** This is planning readiness, not a security review, working-product claim or 24-hour delivery commitment.

## Artifact inventory and alignment

| Planning input | Finding |
| --- | --- |
| Mary brief/addendum and source snapshots | User corrections and challenge preserved; codebase, repository and website URL required; URL uses OWASP ZAP |
| John PRD | 21 FRs, seven NFRs, evaluation criteria and indexed provisional choices |
| Sally DESIGN/EXPERIENCE | Three journeys, 10 visual/behavioral component contracts, state/recovery/accessibility and proposed tokens |
| Winston spine/API/safety profile | State/data ownership, typed common boundary, source/repository/website isolation, comparison, sharing, access/deletion and finite limits |
| epics.md | Five incremental user-value epics, 16 stories; all FR/NFR/UX/AD references covered; no future/missing dependencies |

No duplicate or competing current epic document exists. The derived backlog JSON matches the canonical epic stories and is an import snapshot only. No application code or prior implementation is assumed. Existing artifact checks were reused rather than rerun without new changes.

## Implementability judgment

A developer can begin Story 1.1 without inventing undocumented product boundaries. Each next story has observable acceptance, earlier dependencies and governing architecture. Starter/schema/toolchain setup is first; source review delivers real value before optional AI and later modes. Schema fixtures are contracts, not fake production results. Tables are introduced by the first story that needs them.

The PRD and UX provisional choices are explicitly recorded, not unresolved contradictory decisions: initial JS/TS, folder/file-tree transport, public GitHub snapshots, passive unauthenticated ZAP, independent modes, optional dependency scanning, opt-in model sharing and local session-isolated demo. Actual assignments and repository owner/name/visibility do not prevent planning the work; they must be resolved in the final setup stage.

## Build-time gates and operating order

| Gate / risk | Owning story | Required outcome |
| --- | --- | --- |
| Candidate package compatibility, starter/tool availability and immutable pins | 1.1 | Real compatible build/startup and locked artifacts; update seed if candidate pins change |
| Source intake/session and lifecycle containment | 1.2–1.3 | Safe validation, private owned state, quotas, idempotency, crash cleanup and deletion |
| Category/rule quality and secret masking | 1.4 | Real fixtures, trusted rules/license evidence, public-key controls and outward-channel tests |
| Highest-risk ZAP networking | 3.1 after 1.3 | Demonstrated actual-destination/budget controls, no bypass and private control API; fail closed if unavailable |
| Browser-visible secrets | 3.3 | Real bounded asset finding, mapped URL evidence and honest missed/excluded scope |
| Comparable genuine repeats | 4.2 | All modes repeat actual checks; failures/changed pages/policy never become repair claims |
| End-to-end demonstration | 5.1–5.2 | Real outputs, measured evidence, recovery and accessibility checks on demo machine |

Start with 1.1 → 1.2 → 1.3 → 1.4 → 1.5. Repository 2.1 and website 3.1 can begin after their recorded prerequisites; prioritize 3.1 feasibility early. AI 4.1 can begin after source review without waiting for website completion. Honor the dependency DAG rather than starting every story at once. One owner per story; capacity and time estimates are not invented.

Stories 1.3/1.4/3.1 are the largest risk units; narrow their execution plans to their stated boundaries and split before coding if the assigned developer finds a real scope/size issue. A split must preserve acceptance, stable traceability and tracking dependencies. This is an execution watchpoint, not an undocumented architectural gap. No required mode/safety criterion is silently cut to force the schedule.

## Tracker generation

The standard `sprint_plan.py` was attempted but cannot import `ruamel.yaml` in either available Python runtime. The skill's documented failure path was used: generate the initial YAML from the canonical backlog snapshot and verify against epic/story counts, preserve the defined statuses, and independently check the emitted restricted YAML subset, official key/status grammar, unique keys, story-file status floor and dependencies. The standard ruamel-based validator could not run; no general YAML parser was installed. No existing status file was overwritten or status downgraded. No package installation or subagent dispatch was needed.

At initial tracker generation, only Story 1.1 had a handoff. During the subsequent user-requested preparation, all 16 detailed handoffs were created and the story-file floor was applied: all are now `ready-for-dev` (prepared). Dependencies still control eligibility, so only Story 1.1 is initially unblocked. Epics remain `backlog`; retrospectives remain `optional`; nothing is implemented or in progress. The fallback/check evidence is stored beside `sprint-status.yaml`. Once `ruamel.yaml` is available, the standard generator can refresh this file without a migration.

## Next

**Repository/GitHub setup is complete.** The private VibeGuard repository contains shared plans and team guidance; five epics and 16 stories are published with native relationships. Three Write invitations were sent. See [publication identities](../github-issues/publication.json). Zero setup stages remain; Amelia's `bmad-build` starts Story 1.1 next. Implementation and functional/demo verification remain ahead.

## Final scope refinements applied

Comparison UI 4.3 no longer depends on optional AI 4.1. Story 5.1 uses an explicit per-mode capability matrix, with product-wide coverage of all four categories and unsupported cells explained. Build fixtures alongside adapters; prototype the source repair/rescan loop after 1.5 while retaining 4.2 final dependencies. Prove runtime availability in 1.1 and ZAP networking in 3.1 as early as its prerequisites permit; select an authorized public demo deployment consistent with safety-v1. Full-corpus release verification remains in Epic 5.
