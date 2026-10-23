---
title: 'AI Security Reviewer — Product Requirements'
status: final
created: 2026-10-23
updated: 2026-10-23
workflow: bmad-prd
mode: headless-create
approval: pending-user-review
---

# PRD: AI Security Reviewer

## Purpose and vision

This PRD defines the CY-02 hackathon product for UX, architecture and story creation. It builds on [Mary's brief](../../briefs/brief-TechFest-2026-10-23/brief.md) and its preserved research. Final means this authoring stage is complete; it does not mean user approval, implementation or technical readiness.

A developer submits a **full codebase, repository, or website URL**, receives real security findings with masked evidence, copies one repair prompt into their coding tool, then repeats the scan to inspect changes. **Website URLs are checked using OWASP ZAP.** All three input modes are required. The product helps users act on evidence; it does not certify security.

The proposed value is a focused graphical workflow connecting detection, understandable guidance and repeat checks. Existing products already provide scanning and AI remediation; no unique detection technology or proven competitive advantage is claimed.

## Users and journeys

Primary user: a developer shipping an AI-built website who needs practical security guidance. Evaluators need a reproducible demonstration and honest coverage. No account system, administrative dashboard or enterprise rollout is required.

The following journeys reconstruct the user's supplied workflow; they are planning scenarios, not new interview findings.

- **UJ-1 — Hemant reviews source.** Select Codebase or Repository, submit the project, inspect actual scanner progress, filter findings, read masked file/line evidence, and copy the repair prompt. Rejected input gives an actionable reason.
- **UJ-2 — Hemant reviews a deployment.** Submit an authorized website URL, see ZAP progress and visited scope, inspect URL-based evidence and limitations, then copy the repair prompt. Blocked destinations and incomplete crawls remain visible.
- **UJ-3 — Hemant checks changes.** Upload corrected source, select a new repository revision, or rescan the website. Compare compatible runs; distinguish remaining, newly detected, not detected and unverified findings. Failure never appears as a repair.

## Vocabulary

- **Submission:** supplied codebase, repository reference or website URL.
- **Scan:** one execution against a recorded source revision or website observation, using recorded policy and tools.
- **Finding:** an evidence-backed candidate issue, with severity and confidence; not automatically a proven vulnerability.
- **Coverage:** tools, rules, files/pages and exclusions actually assessed, including incomplete checks.
- **Repair prompt:** one consolidated instruction set for the user's coding tool, containing evidence, changes and verification steps.
- **Comparable scan:** a repeat scan with compatible input mode, scope and policy sufficient to assess a finding again.

## Functional requirements

### Intake and project scope — UJ-1, UJ-2

**FR-1 — Three submission modes.** Users can independently select Codebase, Repository or Website URL. Acceptance: each mode completes a real controlled fixture scan and produces a report. A failure message alone does not satisfy delivery; ZIP cannot be the sole input mode.

**FR-2 — Full codebase submission.** Accept a bounded source tree, preserve relative paths and identify accepted/excluded files. [ASSUMPTION A2: browser folder/file-tree upload is the initial transport; archive upload is optional.] Acceptance: a multi-directory JS/TS fixture retains its paths; invalid or oversized content is rejected with reasons; unsupported or unknown projects show explicit coverage rather than false success.

**FR-3 — Repository submission.** Retrieve a bounded source snapshot and record repository, requested reference and resolved commit. [ASSUMPTION A2: public GitHub HTTPS repositories first; private access and history scanning are deferred.] Acceptance: equivalent repository and uploaded-source fixtures yield the same seeded source findings under the same policy. Failed retrieval never starts a fictitious successful scan.

**FR-4 — Website submission.** Accept an authorized HTTP(S) target and use OWASP ZAP. [ASSUMPTION A3: baseline/passive, unauthenticated public targets; no active attacks.] Acceptance: the controlled deployment produces actual ZAP observations with target, policy and visited/excluded scope; disallowed destinations and unsafe redirects are rejected. Partial crawling is identified.

**FR-5 — Recognized scope.** Show project inventory for source and target scope for website scans. [ASSUMPTION A1: initial source coverage is JS/TS, including relevant React/Vite/Next.js/Node patterns.] Acceptance: unrelated languages/files and skipped checks cannot inflate completed coverage.

### Detection and truthful execution — UJ-1, UJ-2

**FR-6 — Source checks.** Run Gitleaks and selected trusted Semgrep rules on codebase/repository submissions. Acceptance: planted fake private-credential and unsafe-input cases produce real rule/location evidence; tool/rule versions are recorded; submitted configuration cannot silently suppress mandated checks.

**FR-7 — Required issue categories.** Provide selected, validated detection coverage for credentials, unsafe input, insecure configuration and missing-access-check candidates. Acceptance: each category has at least one labeled vulnerable/control pair with expected rule/alert and observed evidence. An unsupported category is reported as a delivery gap, not claimed as implemented. Missing local authentication alone is not proof of bypass.

**FR-8 — Browser-visible secrets.** Check an explicitly bounded set of authorized browser-visible text assets for credential candidates. Acceptance: a fake private credential in the deployed fixture's visible asset is detected with asset URL and masked evidence. Record fetched/excluded asset scope. Do not assume stock ZAP alone supplies this capability or imply access to private backend source.

**FR-9 — Public-key distinction.** Explain credential confidence using available type/context. Acceptance: an intentionally public browser key control is not automatically labeled a private secret; potentially privileged credentials receive review and revoke/rotate guidance. Never test live credentials.

**FR-10 — Actual tool states.** Report queued, running, complete, failed, skipped and timed-out outcomes as applicable. Acceptance: timeout, missing tools/rules, malformed output and findings-bearing exit codes are distinguished using execution outcome plus valid report content. Failed checks cannot become zero-findings success.

### Findings and guidance — UJ-1, UJ-2

**FR-11 — Attributed findings.** Each Finding includes originating tool/rule or alert, severity, confidence with rationale, source revision or target, actual location, sanitized evidence, explanation and repair guidance. Acceptance: source cases reference existing relative file/line; website cases reference observed URL/header/response or asset location. Unknown locations remain unknown rather than invented.

**FR-12 — Interactive investigation.** Users can filter by severity/tool, search title or location, select a Finding and inspect its evidence. Acceptance: filters alter the displayed set consistently; keyboard selection works; empty-filter results differ from a completed scan detecting nothing.

**FR-13 — Grounded explanations.** AI may explain bounded sanitized evidence, without inventing detections, locations or verified exploitability. Acceptance: explanations retain actual tool/rule references; unsupported claims are rejected or replaced with deterministic guidance. Report evidence remains usable if AI is disabled, unavailable or times out.

**FR-14 — Consolidated repair prompt.** Generate one copyable prompt containing relevant project/scan context, affected locations, required changes, constraints and verification steps. Acceptance: every included Finding maps to supplied evidence; copy success/failure is visible; fallback works without the model; all copied values remain sanitized.

**FR-15 — Credential follow-up.** Keep manual revoke/rotate instructions separate from code edits. Acceptance: relevant Findings and the Repair prompt retain this reminder after a finding disappears; the app never claims that source removal rotated a credential.

### Rescan and comparison — UJ-3

**FR-16 — Real repeat execution.** Repeat the checks for corrected codebase, new repository commit and updated website. Acceptance: a new Scan records its baseline relationship, revision/target, policy and tool versions; it does not reuse fabricated or stale findings as fresh output.

**FR-17 — Honest classifications.** Classify Findings as `still_detected`, `not_detected`, `newly_detected` or `unverified`. Acceptance: line shifts alone do not imply repair; failed/changed rules, uncertain matches or missing page coverage produce unverified outcomes. URL-only repeats cannot clear source Findings. Reserve `verified_fixed` for a repeatable behavior check proving removal of the failure condition; that label is not required in MVP.

**FR-18 — Comparison evidence.** Users can inspect both runs' evidence and coverage. Acceptance: show baseline/new revision or observation, completed-check counts, exclusions and status labels without relying only on color; retained key-rotation reminders remain visible.

### Workspace, privacy and control — all journeys

**FR-19 — Cohesive graphical workflow.** Present submit/scan → investigate/repair → compare as three phases of one workspace. Acceptance: progress comes from actual events; loading, rejected input, partial scan, disconnected/retry, AI fallback, no findings and failed rescan states are distinct. Completed clean checks say “No findings detected within completed checks,” never “secure.”

**FR-20 — Authorization and data choice.** Require users to confirm permission for code, repositories and sites. Explain scope and external-model sharing before sending evidence. [ASSUMPTION A6: external AI can be disabled; only sanitized relevant evidence is shared after an explicit user choice.] Acceptance: disabling sharing prevents external model calls and still yields a usable deterministic Repair prompt. The permission statement does not replace network isolation.

**FR-21 — Deletion and access.** Restrict reports to the initiating operator/session and support deleting a Scan's retained source/report data. [ASSUMPTION A7: a single-team demonstration, not an unrestricted multiuser service.] Acceptance: another session cannot retrieve the report merely by guessing its ID; deletion prevents subsequent reads, removes retained artifacts and reports cleanup failures. Exact expiry policy must be fixed in architecture before implementation.

## Cross-cutting requirements

- **NFR-1 — Secret handling:** fake planted secret values must be absent from persisted reports, logs, model payloads, UI, clipboard and exports in the acceptance corpus. Test vendor fields independently of redaction flags. Bound temporary raw processing and clean it up; do not promise mathematically perfect detection/redaction.
- **NFR-2 — Untrusted content:** no submission can trigger app execution, installs, build scripts, arbitrary shell commands or model-controlled tools. Test hostile source comments/pages as data, including prompt-injection attempts.
- **NFR-3 — Restricted execution:** source retrieval and scanners must operate within documented finite input/output/time/resource limits. Reject traversal, links, special files and archive bombs where applicable. Test the approved limits and one over-limit case; architecture must fix numeric values before implementation.
- **NFR-4 — Network isolation:** website and asset requests must enforce target scope and permitted actual destination addresses, including DNS changes and redirects. Block internal/metadata destinations; bound request count, bytes and duration; protect the ZAP control interface. Test initial and redirected blocked destinations.
- **NFR-5 — Reproducibility:** record scanner/rules/policy versions and applicable coverage; keep lockfiles. Retrying or refreshing progress must not silently launch duplicate scans or change baseline identity.
- **NFR-6 — Accessible presentation:** all core actions work by keyboard with visible focus, text labels and readable contrast; support reduced motion. At 360px width, the workspace fits without page-wide horizontal overflow; code panels may scroll independently. [ASSUMPTION A8: 360px is the proposed narrow-layout acceptance viewport.] Sally specifies visual tokens and checks contrast.
- **NFR-7 — Bounded failure:** every accepted job reaches a terminal outcome within its documented deadline; model failure cannot block the evidence report. Measure actual elapsed times on the demonstration machine rather than promising untested latency.

## Scope and non-goals

Required scope is FR-1–FR-21 and NFR-1–NFR-7, subject to the explicitly indexed assumptions. All three input paths, source checks, ZAP, browser-visible credential coverage, safe evidence, repair and real comparison remain required.

[ASSUMPTION A4: dependency scanning with Trivy or OSV is optional; do not add it before required integration.] [ASSUMPTION A5: independent modes suffice; combined source-plus-URL linkage is optional.] Additional languages, private repository authentication, Git history, authenticated ZAP sessions, active testing, automatic code edits and decorative animation are deferred. No chatbot-first UI, security score, account-system expansion or security certification is required. These boundaries may be revisited explicitly; they must not silently remove a required input.

The 24-hour reference is the challenge constraint, not a claim about time remaining. Prioritize feasibility checks and integration of required paths; cut optional work before evidence, masking, failure visibility or required intake support.

## Evaluation and success

Acceptance targets below are not measured results.

- **SM-1 — Required loop completion:** all three input modes complete a controlled vulnerable scan and corrected repeat scan with real reports (FR-1–FR-4, FR-16–FR-18). Explicit failures are necessary negative tests, not substitutes for successful mode completion.
- **SM-2 — Detection evidence:** publish expected/observed cases for all four categories, public-key and clean controls, plus browser-visible fake secrets (FR-6–FR-9). Count a labeled issue occurrence as the unit; duplicate tool reports do not count as extra true positives. Report true positives, false positives and false negatives; precision/recall are omitted when denominators are zero. No invented percentage target.
- **SM-3 — Guidance utility:** a teammate checks each controlled case for correct location, understandable impact, actionable change, usable verification and required rotation guidance (FR-11–FR-15). Record pass/fail per criterion; unsupported claims fail.
- **SM-4 — Safe failure and honesty:** exercise missing tools, invalid output, timeout, AI outage, unsafe input/redirects, secret-output checks and incomparable rescan cases (FR-10, FR-13, FR-17, FR-20–FR-21; NFR-1–NFR-7). No planted raw secret may appear on tested outward surfaces.
- **SM-C1 — Coverage countercheck:** reduced findings or runtime do not count as improvement if files/pages/rules were excluded or checks failed. Report coverage with every result.
- **SM-C2 — False-confidence countercheck:** track false alarms, missed expected cases and unsupported AI assertions alongside detection counts. A larger warning count is not inherently better.

## Assumptions and downstream decisions

| ID | Provisional scope | Owner / revisit gate |
| --- | --- | --- |
| A1 | JS/TS initial source ecosystem | John/Winston; before source stories |
| A2 | Folder/file-tree upload and public GitHub snapshot; private/history deferred | Winston; before intake architecture is finalized |
| A3 | ZAP baseline/passive, public unauthenticated HTTP(S), no active attacks | Winston; before website architecture is finalized |
| A4 | Optional Trivy or OSV dependency scanning | John; only after required loop integration |
| A5 | Independent input modes; combined linkage optional | John/Winston; before scan identity contract |
| A6 | User choice for external sanitized-evidence sharing; model optional | Winston; before model integration |
| A7 | Single-team demo with session-isolated reports | Winston; before report access/deployment design |
| A8 | Proposed 360px narrow viewport | Sally; UX acceptance definition |

No unanswered question prevents UX or architecture planning. Before implementation, Winston must resolve numeric budgets, expiry/cleanup, runtime, trusted rules/licensing, typed evidence and comparison contracts, and the browser-asset detector. Sally must establish `DESIGN.md` and `EXPERIENCE.md`; no existing visual tokens are assumed. Actual team assignments, remaining time and GitHub owner/name/visibility are supplied at sprint/repository setup rather than invented here. See [addendum.md](addendum.md).
