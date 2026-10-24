---
title: 'Epic 5: measured acceptance and accessible demo readiness'
type: feature
created: '2026-10-24'
status: in-review
baseline_commit: 12182217d05b224704057eba9e7a7f5f25ac1ccf
route: dispatch
review_loop_iteration: 0
context:
  - D:/TechFest/docs/PROJECT_RULES.md
  - D:/TechFest/_bmad-output/implementation-artifacts/epic-5-context.md
---

<frozen-after-approval reason="human-owned intent">

## Intent

Deliver stories 5.1 and 5.2 as a single final acceptance batch: a labeled real-scanner corpus, honest metrics, tested recovery/accessibility and a rehearsed operator guide. Work directly without subagents. Use focused checks for defects and one broader verification after integration.

## Boundaries & Constraints

Always exercise actual application boundaries and pinned scanner workers. Keep vulnerable/corrected/clean controls, source/repository equivalence and website passive/asset-secret checks explicit. Separate controlled transport fixtures from live public acquisition; do not count errors as mode completion. Use existing public team repository `https://github.com/HemantKumar822/vibeguard` and previously authorized site `https://hemantkumar822.github.io/` for live transport rehearsal, recording revisions/observations. Do not publish new fixtures or mutate deployed targets.

Never use live credentials, weaken public-destination enforcement, execute submitted applications, enable paid AI, invent measurements or claim accessibility from CSS alone. Keep raw source/vendor output in private external scratch; only sanitized observations and aggregate evidence may be tracked. Subjective teammate prompt judgments and unavailable browser capabilities remain explicitly unassessed until actually checked. Missing safety/required-mode evidence blocks a release-ready claim.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure |
|---|---|---|---|
| Labeled corpus | Vulnerable/corrected/clean and public-key controls | Real rules/alerts/locations, coverage, versions and elapsed time recorded | Misses and unsupported cells explicit |
| Metrics | Expected occurrence labels and observed findings | Deduplicated TP/FP/FN and denominators; null undefined ratios | Incomplete scope cannot remove misses |
| Required modes | Source, repository, website and repeats | Actual reports/new lineage; live versus controlled transport identified | Errors never count as successful mode |
| Hostile corpus | Intake/network/session/CSRF/retry/deletion/crash/model failures | Enforced bounds, private evidence, real cleanup and no duplicate work | Release blocked on failed boundary |
| Privacy | Planted synthetic values and injected instructions | Absent from tested outward surfaces; instructions never executed | Explicit blocking sanitizer failure |
| Rendered journeys | Desktop/360px, 200% zoom, keyboard/reduced motion | Actions, labels, focus, status and paired evidence usable | Record defect and repair, not guessed pass |
| Recovery | Empty/partial/denied/expired, clipboard/folder unsupported | Deliberate reconnect/retry/manual copy without losing baseline | No false success or silent duplicate scan |
| Clean start | Operator follows documented commands | Versioned setup, actual scan/repair/rescan and cleanup rehearsed | Pending/live-target limitations visible |

</frozen-after-approval>

## Code Map

- `tests/test_source_pipeline.py`, `test_repository.py`, `test_website.py`, `test_rescans.py`: reuse existing real-worker and controlled transport seams without duplicating production policy.
- `backend/api/main.py`, `workers/coordinator.py`, `workers/launcher.py`: actual admission, orchestration, pinned execution and cleanup; fix only demonstrated defects.
- `backend/core/comparison.py`, `backend/core/repair.py`: report/lineage/guidance outcomes to score, not new evaluation substitutes.
- `frontend/src/SourceIntake.tsx`, `Report.tsx`, `Comparison.tsx`, `index.css`: preserve current visual system; repair observed keyboard, reflow, clipboard and recovery problems.
- `contracts/scanner-readiness.json`, `website-readiness.json`, `docs/DEVELOPMENT.md`: existing runtime evidence and observed startup commands.

## Tasks & Acceptance

**Execution:**
- [x] `fixtures/acceptance/` — add explicit occurrence labels and safe source/website controls for supported category cells; use synthetic values only.
- [x] `scripts/run_acceptance.py`, `backend/evaluation/` — reproducible corpus runner and occurrence scoring; bounded sanitized JSON/Markdown artifacts, versions/runtime/coverage and per-criterion guidance checks; no hidden mocked success.
- [x] `tests/test_acceptance.py` and existing adversarial tests — exercise scoring, misses/duplicates, sanitization, limits, all-mode real repeats and safety failures; record selected test commands as evidence.
- [ ] `frontend/src/` and focused UI tests — verify/fix rendered keyboard/reflow/status/recovery behavior, including clipboard/folder limitations and preserved before/after context.
- [x] `docs/DEMO_RUNBOOK.md`, `_bmad-output/implementation-artifacts/epic-5-verification.md` — document clean-start setup, genuine corpus/demo/recovery/cleanup commands, measured results and release blockers.
- [x] Story/sprint records — distinguish implemented tooling, observed acceptance, unassessed checks and teammate-review status.

**Acceptance Criteria:**
- Given the labeled corpus, when run with actual workers, then reproducible sanitized evidence includes expected/observed occurrences, misses, tool/policy versions, coverage and measured runtimes across supported modes/categories.
- Given hostile/failure cases, when checked, then required safety boundaries hold or release remains blocked, and no planted private value crosses tested public surfaces.
- Given rendered journeys and recovery states, when exercised, then core actions remain accessible at required view/zoom/motion settings or remaining gaps are explicit blockers.
- Given a clean-start rehearsal, when following the runbook, then the real workflow and cleanup are reproducible without pretending fixture transport or missing checks are live acceptance.

## Implementation Notes

Baseline is the pushed Epic 4 commit `12182217d05b224704057eba9e7a7f5f25ac1ccf`. Both existing team repositories/website are public. Creating or deploying new public fixture versions is outside this batch; missing controlled live revision/deployment labels will be reported rather than fabricated.

## Spec Change Log

## Review Triage Log

- medium / patch: Harness deletion left cleanup pending and blocked later admissions; now waits for trusted cleanup between cases. Verified by completed later matrix rows.
- medium / patch: Controlled website callback rejected the active keyword; corrected local callback signature and reran only website cases. All three completed.
- medium / patch: Empty filters lacked recovery and finding detail lacked focus return; fixed and checked with regression tests and rendered observations.
- low / patch: Non-JSON output extension could overwrite evidence with its summary; parser now requires .json.
- medium / deferred acceptance: Additional web alerts, partial live capture, remaining manual accessibility checks and teammate judgment are recorded in epic-5-verification.md. User will perform browser checks; no claim of final release acceptance.
- Review conducted inline per explicit no-subagents instruction.

## Verification

After integration, run the corpus with real Docker workers, selected existing adversarial checks, frontend recovery checks and one build/lint/contract pass. Inspect the rendered application using an available browser at required viewports/settings and rehearse clean-start operation. Record actual output; rerun only checks affected by fixes. Never mark unexecuted browser, live transport or teammate judgments as passing.

## Delivery handoff

Implementation delivered for merge at the user's request. The remaining frontend manual task and release checks stay open in epic-5-verification.md; the user explicitly stopped browser testing and will test personally. GitHub publication/merge is authorized.
