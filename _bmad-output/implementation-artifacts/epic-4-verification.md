# Epic 4 verification — 2026-10-24

Baseline: `c04dd6eab28d85b735b50132453468dd4e1ded3e`.

## Delivered

- Story 4.1: optional server-owned HTTPS JSON explanation selection; sharing and configuration both required. One request, no redirects/retries, 30 Findings, 24 KiB request, 8 KiB response and 15-second whole-call limit within remaining job budget. Only supplied trusted guidance options for existing IDs/locations can be accepted. Raw source, invented prose and model-controlled execution are excluded. Core always retains deterministic guidance and human actions.
- Story 4.2: shared all-mode rescan admission, fresh Scan identity, direct lineage, lineage-bound idempotency, transactional baseline ownership/mode/expiry/tombstone recheck and owned comparison. Existing workers perform new execution. Matching uses compatible policy/tool/image/rule versions, per-resource coverage and conservative structural identity. Unknown identifiers, duplicate candidates and redacted URL identity remain uncertain. Baseline actions are snapshotted at admission and survive later baseline expiry.
- Story 4.3: same-mode repeat form, renewed permission/sharing choices, preserved baseline, real new-run progress, paired evidence and coverage, four classifications/reasons, retained human actions and explicit recovery. Identity fences prevent late reconnect/poll/comparison results from replacing newer work or showing mismatched comparisons.

## Observed verification

One broad batch run was executed after implementation, followed only by checks affected by fixes:

| Check | Observed result |
|---|---|
| `VIBEGUARD_DOCKER_TESTS=1 uv run --no-cache pytest -q` | 218 passed; one generated OpenAPI parity failure. Actual scanner repeats for codebase, repository and website all passed in this run. |
| Regenerate OpenAPI and frontend types | Passed; stale handler operation metadata corrected. |
| `pytest tests/test_comparison.py tests/test_explanations.py tests/test_rescans.py tests/test_bootstrap.py::test_generated_schema_matches_live_app -q` after review patches | 44 passed, three opt-in real repeats intentionally skipped; these had already run in the batch. |
| Final unknown-identifier ambiguity regression | One passed. |
| Final actual codebase repeat after structural-identity correction | One passed using pinned Gitleaks/Semgrep containers. |
| Initial frontend batch | 26 passed; one existing polling-race test needed explicit renewed consent under the new per-submission consent behavior. Expectations preserving the newer accepted report were retained. |
| Affected SourceIntake and Comparison suites after fixes | 19 passed. |
| Final UI identity/consent tests after ref correction | Three passed; remaining tests intentionally deselected. |
| Generated contract parity | Passed. |
| Production build and production fixture-exclusion gate | Passed. |
| Lint | Passed; ref-during-render warning fixed and lint rerun clean. |
| Measured website readiness | Passed against existing authorized team target `https://hemantkumar822.github.io/`; both ZAP and asset stages complete, six inspected resources, private source removed. Result is explicitly partial where capture scope omitted resources. |

Existing upstream Starlette/httpx TestClient deprecation warning remains. No broad suite was repeated after targeted fixes, per the user's batch-testing preference.

## Review and limitations

Independent review was completed before the user requested no further subagents. All subsequent fixes, checks and completion work were performed directly. Every finding and disposition is recorded in the build spec's Review Triage Log. Review patches cover stale UI identity, deadlines, baseline reminder expiry/prompt overflow, constrained AI text, uncertain structural matching and missing transport/website identity regressions. No unresolved review blocker is intentionally deferred.

Repository retrieval and response capture in all-mode repeat smoke tests are labeled controlled fixtures; scanner launches are real. The separate measured website proof uses the team target. These are not claims of live public repository revision retrieval during a repeat or arbitrary public-target safety. Live paid-provider integration was not attempted; AI stays disabled until a compatible configured gateway is provided. Browser visual inspection, zoom and screen-reader walkthrough were not performed; DOM interactions and responsive CSS were checked through code/tests only.

Implementation is ready for teammate/PR review. No remote push, PR, deployment or GitHub issue closure is part of this batch.
