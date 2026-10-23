# Epic 4 Context: Receive grounded AI guidance and verify changes through rescans

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Give developers optional explanations grounded in sanitized scanner evidence, then let them repeat real checks on corrected codebases, repository revisions and deployed websites. Preserve baseline reports and expose comparable observations so users can judge changes without mistaking missing coverage, disappeared warnings or removed credentials for proven repairs.

## Stories

- Story 4.1: Add opt-in bounded AI explanations with fallback
- Story 4.2: Execute real rescans and classify comparable findings
- Story 4.3: Inspect paired rescan evidence and recovery

## Requirements & Constraints

External sharing defaults off and requires an explicit choice for each Submission. Disabled sharing must produce no external request. AI receives bounded sanitized evidence, never raw source or credentials, and may explain existing Findings only. Retain actual tool/rule attribution; reject invented detections, locations, exploitability or unsupported claims. Untrusted comments/pages cannot authorize sharing, tools or execution. Provider failure, invalid output, timeout and limit overflow must leave evidence and deterministic guidance usable, with the actual fallback reason.

The consolidated Repair prompt must contain relevant scan context, evidenced locations, required changes, constraints and verification steps. Every included Finding maps to supplied evidence. Separate human revoke/rotate actions from code edits, include them in the prompt and preserve relevant baseline reminders after a credential Finding disappears. Source removal never proves rotation. Sanitization applies to storage, logs, model requests, UI, accessible labels and clipboard.

Rescans execute actual applicable scanners in a new owned Scan, recording baseline lineage, new revision/observation, policy and tool/rule versions. Never overwrite the baseline or present stale results as fresh. Required delivery covers all three modes; fixtures must demonstrate vulnerable-to-corrected repeats, including line shifts, failed checks, changed scope and ambiguous matches. Classifications are `still_detected`, `not_detected`, `newly_detected` and `unverified`; MVP never emits `verified_fixed`. Reduced findings cannot establish improvement if rules/files/pages were omitted.

## Technical Decisions

Core owns transitions, sanitized report composition and comparison; workers/model adapters return bounded data rather than mutating reports. SQLite remains the single state store with transactional claims and one running job. Reuse the shared v1 API/schema and safety-v1 policy, including existing isolated intake/scanner paths. Codebase/repository repeats use Gitleaks and Semgrep; website repeats use ZAP baseline plus asset-secret checks.

Model provider configuration and credentials are server-owned. Permit one call without automatic retries: at most 30 Findings and 24 KiB sanitized structured input, 8 KiB accepted response and 15 seconds, subject to the 300-second job deadline. Remaining Findings receive deterministic guidance. Validate returned Finding IDs and locations against accepted evidence; AI cannot silently increase severity/confidence. Core always builds the master prompt. Report limits remain 1,000 Findings, 2 KiB evidence per Finding, 128 KiB master prompt and 5 MiB sanitized report; overflow yields explicit partial coverage. Repair exposes template/AI-assisted mode, complete/fallback status, sanitized prompt, reason and human actions.

Create repeats with `POST /api/v1/scans/:scan_id/rescans` using the ordinary intake shape and same mode; return a new Scan with `baseline_id`. Fetch comparison through `GET /api/v1/scans/:baseline_id/comparisons/:new_id`. Compare only terminal, same-session direct lineage with compatible mode; invalid state/lineage returns 409, inaccessible resources a nonrevealing 404. Mutations retain session ownership, CSRF and session-scoped idempotency; reconnect/retry must not dispatch duplicate jobs.

Matching uses rule, normalized location and sanitized structural context, never line alone, random public Finding IDs or a raw-secret hash. More than one plausible match stays unverified. Positive matching observations can remain still detected despite partial coverage; absence/newness require applicable scope on both sides and matching policy/tool/rule fingerprints. Website absence additionally requires comparable origin and actual reassessment of that resource; sanitized URL collisions are unverified. URL scans cannot clear source Findings. Coverage manifests, not aggregate counts alone, establish comparability.

Comparison carries both input identities/coverage summaries, comparable/partial status, per-item baseline/new Finding references, classification, reason code, evidence references and retained human actions. Deleted/expired baselines cannot be compared. Reports expire 24 hours after terminal completion; sessions after 24 hours inactivity. Tombstones block late commits, and browser persistent storage must not cache source, prompts or credentials.

## UX & Interaction Patterns

Keep the existing three-phase graphical workspace. Rescan opens same-mode corrected input/target and permission controls while baseline evidence remains accessible. Show actual repeat tool progress; withhold classifications until evidence is available. Pair baseline/new revisions or observations, sanitized evidence, coverage counts/exclusions and classification reasons. Desktop uses paired evidence columns; below 768px stack baseline before new with labels and adjacent context.

Explain not detected as an observation on a comparable rescan rather than proof of repair. Failed repeats, lost pages, changed coverage and uncertain matches show persistent limitations/unverified states. Expired or inaccessible baselines show a nonrevealing unavailable-report explanation and New submission. Disconnect recovery first reconnects by existing Scan ID; another scan is a deliberate action. Preserve filters, valid selection and baseline through refresh/new submissions.

Show model-sharing status, fallback reason and separate rotation reminder in the Repair panel. Copy announces success/failure politely; failure allows manual selection of the sanitized prompt. Reuse semantic tokens, system fonts and visible focus. Actions work by keyboard with 44px targets, meaningful transition announcements without poll spam, text labels beyond color, reduced motion, 200% zoom and 360px reflow with local code scrolling. Narrow selection focuses detail and Back restores selection; polling must not reorder focused content or steal focus.

## Cross-Story Dependencies

AI guidance depends on completed source investigation and deterministic prompts (1.5), but comparison does not depend on AI. All-mode repeat execution depends on repository review (2.2) and website investigation (3.4). Prototype source comparison and fixture repeats after 1.5 without treating all-mode execution as ready/done before those prerequisites. Paired comparison UI depends on comparison execution (4.2), independently of 4.1. Epic 5 consumes this complete loop for integrated corpus and demonstration acceptance.
