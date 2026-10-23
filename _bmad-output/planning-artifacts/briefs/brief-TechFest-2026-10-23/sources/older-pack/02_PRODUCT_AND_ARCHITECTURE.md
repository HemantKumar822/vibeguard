# Modular Architecture — 24-Hour Security Reviewer
Status: Design baseline, not implemented or benchmarked

## System diagram
```
React/TypeScript UI
        |
FastAPI (submit/scan/status/report/rescan)
        |
Submission validation and safe ZIP extraction
        |
Coordinator + project recognizer
        |
Restricted runners: Gitleaks | Semgrep | Trivy
        |
Result adapters -> normalized findings -> deduplicate/redact
        |
AI reviewer (structured evidence, no raw secrets)
        |
Report + single repair prompt + comparison against previous scan

Optional independently gated: authorized URL -> ZAP baseline -> adapter
```

## Module responsibilities and contracts
1. **Intake**: accept ZIP or bounded source-tree upload. Enforce maximum size, file count, path traversal/symlink restrictions, decompressed size and extraction time limits. Never execute upload code.
2. **Project recognizer**: infer languages, manifests, lockfiles and relevant scanner options. Avoid claiming framework certainty from one filename.
3. **Coordinator**: invoke allowlisted scanner commands with fixed arguments; enforce hard timeouts and file/memory/CPU limits; assign scanner runs to a unique job ID. No free-form AI-generated shell commands.
4. **Adapters**: translate vendor JSON into one schema. Preserve source-tool rule IDs and raw technical evidence in restricted storage, but mask credentials in user-visible and model-visible outputs.
5. **Finding engine**: normalize paths and severity; group overlapping findings without discarding source evidence. Stable fingerprint from tool/rule/path/location where possible. Never assume disappearance = verified repair if scanning failed or coverage changed.
6. **AI reviewer**: receive bounded, redacted snippets and structured finding records. Explain impact, confidence, recommended code change and verification method. AI statements are hypotheses until supported by evidence; no silent severity inflation.
7. **Report/rescan**: retain run settings and hashes so baseline vs corrected scans are comparable. States: still-present, absent-on-rescan, newly-detected, and unverified (failed/changed coverage). Reserve verified-fixed for a repeatable check that tests the failure condition.
8. **Optional website scanner**: require authorization, URL validation and strict network egress control. Passive ZAP baseline only; no active scan.

## Normalized finding object
```json
{
  "id": "stable-fingerprint",
  "scanner": "semgrep",
  "rule_id": "javascript.example.rule",
  "title": "Potential unsafe input handling",
  "severity": "medium",
  "confidence": "needs_review",
  "path": "src/api/example.ts",
  "line": 42,
  "evidence_redacted": "User value flows into sensitive operation",
  "explanation": "...",
  "fix_guidance": "...",
  "verification": "...",
  "scan_status": "complete"
}
```

## API sketch
- `POST /projects` -> project ID, accepted files, validation errors.
- `POST /projects/{id}/scans` -> scan ID.
- `GET /scans/{id}` -> status, scanner outcomes and partial progress.
- `GET /scans/{id}/report` -> normalized findings + generated repair prompt.
- `POST /scans/{id}/compare` -> compare against a later scan ID (validate both belong to same project).

## Sandbox approach
- Scanners run in separate disposable, non-root containers or equivalent least-privilege workers, not in the API process.
- Read-only mount for uploaded files; separate scratch output location; no host Docker socket, no privileged flag, no mount of host secrets.
- Disable network for scanners that do not require it; provide controlled cached vulnerability databases for Trivy where possible.
- Pin image versions/digests; enforce CPU/memory/process/disk/time limits; scan uploads for path bombs and unsafe links before extraction.
- Never install dependencies, run package lifecycle scripts, start submitted code, or hand the agent unrestricted shell/network privileges.
- For URL scanning: isolate network, enforce public-address-only egress at connection time, protect against DNS rebinding and redirects, and require target ownership/authorization.

## Failure rules
Scanner failure is *scan incomplete*, not *zero vulnerabilities*. Unparseable scanner output is a failed adapter. AI timeout returns evidence report without AI prose. Rescan with a failed scanner gets `unverified`, never `fixed`.

## Source references
https://trivy.dev/docs/dev/target/filesystem/
https://www.zaproxy.org/docs/docker/baseline-scan/
https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
https://owasp.github.io/DevSecOpsGuideline/2-Process/2-2-Develop/2-2-3-Secure-Code-Review/


## User-facing product requirements
The main application is **not a chatbot**. It needs a project submission view, progress view with per-scanner statuses, filterable findings explorer, details pane with masked evidence and source location, one-click repair prompt, and before/after rescan comparison. Visual hierarchy and interactions must follow the user-supplied `DESIGN.md` once available; do not invent a competing style guide. Accessibility, loading/empty/error states and responsive behavior are required.

## Module boundary rules
- Scanner adapters never directly write UI copy; they return structured evidence and metadata.
- UI must render reports even if AI analysis is disabled or unavailable.
- API contracts and fixture JSON are agreed before parallel frontend/backend work.
- Comparison keys include rule, file and scanner version context. A missing finding is not automatically a verified fix.
- Record what scanner types did **not** run. Never display a blanket 'secure' verdict.

## Suggested repository modules (illustrative)
```text
frontend/             React/TypeScript visual app
backend/api/          FastAPI upload, scans, reports
backend/core/         coordinator, contracts, compare
backend/scanners/     gitleaks, semgrep, trivy adapters
backend/ai/           evidence-grounded explanations
backend/security/     intake, redaction, worker policy
fixtures/             known-safe and intentionally unsafe samples
docs/                 these references plus supplied DESIGN.md
```
