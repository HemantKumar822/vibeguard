# Epic 5 implementation and verification

Baseline: `12182217d05b224704057eba9e7a7f5f25ac1ccf`. Implemented directly; no subagents used. The user approved the full batch and subsequently requested that browser testing stop and remaining manual checks be left to them. No further browser operations followed that request.

## Delivered

Synthetic vulnerable/corrected/clean source controls, explicit occurrence labels, public-key controls, actual API/coordinator/pinned-worker acceptance runner, bounded sanitized JSON and Markdown evidence, deduplication and honest TP/FP/FN with null undefined ratios, structural guidance criteria, source cleanup checks and a concrete operator guide. Repository/source controls use identical input bytes and paths. Controlled acquisition substitutions exist only inside the explicit evaluation command, with no public API bypass or production setting.

The rendered source journey exposed missing empty-filter recovery and finding focus navigation. Report now provides Clear filters, deliberate selection focus and Back to findings. Regression tests cover both. Existing comparison uncertainty and retained rotation actions remain visible.

## Observed commands

- `uv run python scripts/run_acceptance.py --live --output _bmad-output/implementation-artifacts/epic-5-acceptance.json`: initial harness attempt encountered cleanup fencing after deletion. Fixed the harness to run trusted cleanup before the next admission. The second batch completed source/repository controls and live acquisition; controlled website callbacks failed on the keyword `active`. Fixed that evaluation callback only.
- `uv run python scripts/run_acceptance.py --modes website --output _bmad-output/implementation-artifacts/epic-5-website-acceptance.json`: reran only affected website cases with real workers. All three completed. Exit 1 correctly retained additional passive alerts as unexpected relative to frozen selected labels. Latest website rows/comparisons replaced the failed callback rows in the combined sanitized acceptance JSON; attempt history is retained. Raw vendor output/source was not copied into evidence. The temporary second evidence file was removed after consolidation.
- `uv run pytest -q tests/test_acceptance.py tests/test_intake.py tests/test_repository.py tests/test_web_capture.py tests/test_sessions.py tests/test_cleanup.py tests/test_lifecycle.py tests/test_explanations.py tests/test_comparison.py tests/test_rescans.py`: **169 passed, 3 skipped** in 49.41s. Skips were the older opt-in Docker repeat smokes; the new acceptance command independently executed all three actual worker repeats. One existing TestClient deprecation warning.
- After final metric/gate/report changes, `uv run pytest -q tests/test_acceptance.py`: **5 passed** in 0.05s. These include duplicate/distinct occurrence accounting, retained misses on failed coverage, nested privacy/output bounds, structural-versus-human utility, and rejection of partial/FP/comparison/cleanup failures.
- `npm --prefix frontend test`: **30 passed** across 4 files. Includes clipboard denial/manual copy, escaped evidence, source rescan/reconnect races, filter reset and finding focus return.
- Frontend production build, lint and contract parity all **passed**. Build excludes development fixture payloads. No schema change.

## Measured results

See [table](epic-5-acceptance.md) and [sanitized evidence](epic-5-acceptance.json). All **9/9 controlled mode/variant cases** reached complete with actual scanners. All three corrected submissions produced distinct scan identities and successful comparison responses. Source/repository vulnerable cases each measured TP4/FP0/FN0; corrected and clean controls had zero selected occurrences. Website vulnerable measured TP5/FP2/FN0; corrected and clean each retained three unexpected passive occurrences. These are FP **relative to selected labels**, not adjudicated claims that ZAP is wrong. Actual extra IDs were 10015, 10055 and 10109. Labels were not edited after observation.

Live repository acquisition and scan completed (18.219s). Live website acquisition ran both required scanners but remained partial (36.296s) because capture exclusions prevent complete scope. Neither live target has a ground-truth accuracy denominator. All 11 measured rows reported source removal; final staging directory count was zero. Source corpus includes fake credentials only; planted value was absent from tested report/prompt/comparison artifacts.

## Rendered observations before user stopped browser work

Fresh external private runtime, actual API, separate coordinator and frontend were started. Existing dependencies/images were reused; clean dependency reinstall was not repeated. API unavailable then connected was observed. Source submission found four actual candidates; corrected rescan found zero and preserved baseline with honest partial comparison uncertainty. Clipboard contents and rendered DOM did not include the planted value.

At 360px the document measured 345px wide, and at 1440px it measured 1425px: no page-wide horizontal overflow in those observed states. Evidence had independent scroll widths (for example 698px content in a 244px panel). Finding selection focused Selected finding, Back restored the trigger, Clear filters recovered the empty list. Enter activated corrected submission and comparison selection; narrow comparison selection focused Paired evidence. Delete modal initially focused Cancel; Escape preserved the reports. Disposable child deletion was requested; a reconnect to the baseline was initiated before browser work stopped. That last reconnect/cleanup was not verified afterward.

## Release/manual handoff blockers

- Human adjudication of the extra website passive alerts, without retroactively changing ground truth to improve scores.
- Live website omissions remain partial; no controlled public vulnerable/corrected deployment revisions are available. No new targets were published or changed.
- User will test remaining rendered repository/website journeys and every recovery state, 200% zoom, reduced motion, announcements and complete contrast. No full accessibility pass is claimed. Available automation exposed viewport but no zoom/motion controls; a zoom shortcut produced no measured scale change.
- Teammate prompt usefulness/signoff and reviewed PR remain pending. Structural guidance checks are not subjective utility judgments.

Epic 5 remains in progress; implementation is reviewable, but full acceptance and issue closure are not asserted. Local development services remain available for the user's testing; do not delete another runtime or stop unrelated processes.

## Inline review

User explicitly prohibited subagents, so independent review layers were skipped and review was conducted inline. Traced API permissions, deletion fence, scoped fixture substitutions, actual worker invocation, score denominators, private-value gate, incomplete coverage, comparison status and output bounds. Corrected harness cleanup ordering and callback keyword support; preserved failed attempts and extra observations. Added a JSON extension check to avoid overwriting JSON with its Markdown summary. No production safety controls or scanner rules changed. Manual and live-fixture gaps remain open above.
