# Epics and stories validation

Date: 2026-10-23. Result: **backlog authoring complete; ready for sprint readiness review**. No implementation, team assignment, estimate or GitHub publication is implied.

## What was produced

[epics.md](epics.md) is the canonical planning backlog: five user-value epics and 16 ordered stories with dependencies, requirement references and Given/When/Then acceptance criteria. [backlog.json](backlog.json) is a derived snapshot for later GitHub import, not a separate live tracker. [epics-checks.json](epics-checks.json) records mechanical coverage and story links.

1. Review source safely and act on real findings — 5 stories.
2. Review a repository revision without manual upload — 2 stories.
3. Review a deployed website using ZAP and visible assets — 4 stories.
4. Obtain grounded AI guidance and compare genuine rescans — 3 stories.
5. Demonstrate the complete workflow with real evidence — 2 stories.

## Checks

- 21/21 functional requirements, 7/7 nonfunctional requirements, 18/18 extracted UX requirements and 12/12 architecture decisions map to story requirement fields.
- All 16 stories have a user outcome and at least three Given/When/Then acceptance criteria, including meaningful failure paths.
- Dependencies refer only to existing earlier stories: zero forward/missing dependencies and no cycles. Story numbers are contiguous within all five epics.
- Story 1.1 explicitly bootstraps the architecture's Vite react-ts starter and common schema fixtures; tables are introduced only where required.
- Epics deliver incremental user value rather than separate database/API/UI layers. Repository and website adapters have distinct risk boundaries; shared core/UI changes must use the frozen contract rather than fork it.
- Source review includes deterministic repair guidance before AI; later epics do not retroactively become dependencies for earlier user outcomes.
- Required codebase/repository/URL paths, browser-visible credentials, all issue categories, permission, masking, isolation, fallback, rotation and truthful rescans remain in scope.
- Human owners and estimates are intentionally unset. No scanner/runtime enforcement or acceptance test has run during backlog authoring.

These are direct author/structural checks, not independent review or implementation verification. Requirement-ID coverage does not prove that implemented behavior will satisfy acceptance.

## Execution notes for sprint readiness

Story 3.1 (enforced ZAP networking) is the highest feasibility risk and can begin after 1.3 while repository work proceeds. Stories 1.3, 1.4 and 3.1 require careful single-owner work on security boundaries; assess capacity before making a 24-hour commitment, and split during readiness if the actual team cannot execute them in one work unit. Do not cut required safety/modes to force an estimate.

Source inputs are the finalized PRD, both UX spines, architecture spine, API contract and safety profile, all listed in `inputDocuments`. Both original reference packs and CY-02 remain reconciled upstream. Optional Trivy/OSV/private-history/active-scan/decoration work is not inserted into P0.

All four skill steps were processed in sequence. The user's prior instruction to run whole workflows without per-step questions overrides menu/confirmation pauses; `approval: pending-user-review` explicitly avoids claiming user approval. No subagents were used. Resolved completion hook is empty.

**Next: `bmad-sprint-planning` — readiness gate, then sprint tracking when the gate permits it. Two planning/setup stages remain:** sprint readiness/tracking → repository/GitHub setup and final planning consistency audit.
