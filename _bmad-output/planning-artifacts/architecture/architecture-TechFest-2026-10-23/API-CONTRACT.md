# API contract v1 — cold-start boundary

Authority: AD-3. This is the common specification for backend models, frontend generated types and fixture payloads. No independently maintained UI/vendor schema. Names below are binding until replaced by a jointly validated generated OpenAPI contract.

## Endpoints and intake

All endpoints begin `/api/v1`, require the initiating session, use same-origin requests and CSRF on mutations. `POST /session` creates a session and returns its CSRF token; it requires an allowed Origin and does not replace an existing session. Session cookie is random/HTTP-only/SameSite=Strict, Secure under HTTPS; only the explicitly loopback HTTP development profile permits a non-Secure cookie. No wildcard CORS.

| Method / path | Request | Response |
| --- | --- | --- |
| GET /capabilities | none | 200 active policy ID, permitted modes, numeric limits and configured AI availability |
| POST /scans | JSON for repository/website; multipart for codebase | 202 accepted Scan or validation error; session-scoped Idempotency-Key required |
| GET /scans/:scan_id | none | 200 Scan with current coverage/report, or nonrevealing 404 |
| POST /scans/:scan_id/rescans | Same intake shape as initial, same mode required | 202 new Scan with baseline_id; old Scan unchanged |
| GET /scans/:baseline_id/comparisons/:new_id | none | 200 Comparison; 409 if either run nonterminal or lineage/mode incompatible |
| DELETE /scans/:scan_id | none | 202 deletion operation; Scan becomes unavailable immediately |
| GET /deletions/:operation_id | none | 200 pending/complete/failed cleanup status for owning session |

JSON intake: `mode` = repository/website, `repository_url` and optional `ref` OR `target_url`, `authorization_confirmed: true`, `allow_external_ai: boolean`. Unknown fields rejected. Mode-incompatible fields rejected. Server rejects credentials in repository/website URLs rather than logging them. A URL whose path/query contains detected secret-like material is rejected with a safe message; public findings URLs use sanitized display values.

Codebase multipart: `metadata` JSON contains mode=codebase, permission/sharing choice and `files: [{part_id, relative_path}]`; each part_id maps exactly one file body. Do not trust browser filenames. Reject missing/duplicate/unmapped parts, duplicate/case-colliding normalized paths, links and traversal. Aggregate limits apply before complete buffering. Preserve only safe relative paths. Supported tree-based input is required; archive transport is optional.

Idempotency scope: session + key + canonical payload digest, with 24h expiry. Same key/payload returns the original Scan; differing payload returns 409. Payload digests remain internal. Admission validates inputs and queue bounds before assigning accepted Scan status. Repository/website input validation cannot claim remote content already assessed.

## Scan and state ownership

Required Scan fields: `contract_version: "v1"`, `scan_id`, `baseline_id: string|null`, `mode`, `status`, `policy_id`, `policy_fingerprint`, `created_at`, `started_at|null`, `finished_at|null`, `input`, `tools`, `coverage`, `findings`, `repair`, `warnings` and safe `error|null`.

`input`: safe display name, source revision/commit or target observation ID, repository identity or sanitized target origin/path; never raw credential-bearing URLs. Source locations use relative paths. Actual fetched URLs remain in temporary bounded processing only; coverage uses normalized sanitized URL identifiers, and collisions are unverified.

Scan status: `queued → running → complete|partial|failed`. Tool status: `queued → running → complete|failed|timed_out`; explicit `skipped` is terminal with reason. Tool names: `gitleaks`, `semgrep`, `zap`, `asset_secrets`. Source/repository require gitleaks+semgrep; website requires zap+asset_secrets. Other tools are not applicable, represented explicitly with `applicable:false`, `status:skipped`, `reason:not_applicable`, and excluded from required counts.

Each tool record includes `name`, `applicable`, `required`, `status`, `version|null`, `rules_fingerprint|null`, `started_at|null`, `finished_at|null`, `coverage` and `error|null`. Partial result data is sanitized and valid even when execution ends failed, but that tool cannot establish absence conclusions.

Overall complete requires all required tools complete with valid nontruncated output and intended scope assessed. Partial means useful sanitized output exists but a required check/scope did not complete. Failed means no usable report evidence/coverage can be delivered. No findings is not a state. All terminal results include explicit report limitations and deterministic repair guidance, including when AI did not run.

Admission rejection returns an HTTP error without creating a successful Scan. Worker crash/deadline closes tool states and the Scan; core alone performs these transitions. Deletion is an operation state outside Scan status; tombstoned Scan commits are forbidden.

## Findings and coverage

Finding required fields: `id`, `scanner`, `rule_id`, `category`, `title`, `severity`, `confidence`, `confidence_reason`, `location`, `evidence_redacted`, `explanation`, `fix_guidance`, `verification_steps: string[]`, `human_actions: string[]` and `match_context`.

- `category`: `credential|unsafe_input|insecure_configuration|access_check|other`.
- `severity`: `critical|high|medium|low|info`; `confidence`: `high|medium|needs_review`. A trusted adapter mapping owns values; AI cannot silently increase them. Unknown vendor severity maps to info with reason, not omitted data.
- `location.kind=source`: `path`, `line_start: integer|null`, `line_end: integer|null`. Positive existing lines only; unknown stays null. No absolute host path.
- `location.kind=web`: `url_redacted`, `resource_key`, `part: header|response|asset|url`, `parameter_redacted|null`, `line_start: integer|null`. No fabricated source path/line; asset line only if the fetched text supports it.
- `match_context`: internal-safe structural/rule/location identity; no raw-secret hash. Public Finding IDs are random and need not be stable between Scans.

Coverage includes required/completed counts, inspected safe file/resource keys, exclusions with reasons, applicable rule fingerprint, source snapshot or website observation, and `scope_complete: boolean`. Manifest entries support per-finding comparison; aggregate counts alone are insufficient. Bounds apply to manifests too; exceeding a bound makes affected coverage incomplete.

Report grouping may link overlapping Findings but preserves originating tool evidence. No automatic claim of confirmed vulnerability or blanket secure status. Confidence rationale and limitations are available to the UI.

`repair`: `mode: ai_assisted|template`, `status: complete|fallback`, `prompt_redacted`, `model_reason|null`, `human_actions`. Core always supplies a deterministic master prompt; accepted AI may contribute bounded explanations. An external call never receives the raw source or credentials. Keep relevant baseline human-action reminders in the Comparison even if absent on repeat.

## Comparison

Required: `baseline_id`, `new_id`, `status: comparable|partial`, both input labels and coverage summaries, `items` and `human_actions`. Each item has `baseline_finding_id|null`, `new_finding_id|null`, `status: still_detected|not_detected|newly_detected|unverified`, `reason_code` and both available evidence references.

Compare same-session direct baseline lineage, same mode and compatible policy/tool/rules. A positive matching observation can remain still_detected despite partial coverage; absence/newness conclusions require the applicable scope on both sides. Ambiguous matching, lost pages, changed fingerprints or failed tools produce unverified. More than one plausible match is not silently resolved. A Finding on a deleted/expired baseline cannot be compared; return 404/409 safely.

## Errors and boundary fixtures

Errors: `{error:{code,message,request_id,details}}`; details contain safe field names/reasons only, never source fragments. 400 malformed request, 403 CSRF/permission failure, 404 inaccessible resource, 409 idempotency/state/lineage conflict, 413 size, 422 validation, 429 admission cap, 503 runtime unavailable. UI must not reinterpret transport errors as empty reports.

Bootstrap creates validated fixtures for running source, partial source, complete clean source, finding-bearing website, AI fallback, comparable corrected repeat, unverified coverage change and deletion failure. Those fixtures are explicitly development data; a demo must consume actual scanner results. Generate and check the OpenAPI snapshot/types and test fixture conformance before separate frontend/backend stories integrate.

Story 1.2 contract clarification: Scan adds `accepted_files: string[]` (default empty for existing fixtures) and `allow_external_ai: boolean` (default false). Accepted inventory is explicitly distinct from `coverage.inspected`, which remains empty until tools actually run. Permission remains strictly true and missing sharing defaults false with strict boolean validation. Session returns `{csrf_token}`; capabilities exposes policy ID/fingerprint, numeric limits, permitted/unavailable modes and AI availability. These generated v1 additions preserve all existing required Scan fields and truthful completion invariants.
