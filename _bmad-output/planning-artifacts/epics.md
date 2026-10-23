---
title: TechFest epics and stories
status: final
created: 2026-10-23
updated: 2026-10-23
approval: pending-user-review
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - prds/prd-TechFest-2026-10-23/prd.md
  - architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md
  - architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md
  - architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md
  - ux-designs/ux-TechFest-2026-10-23/DESIGN.md
  - ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md
---

# TechFest — Epics and Stories

## Overview

Implementation backlog for the three required input modes, evidence, repair and real rescans. Stories are unimplemented. User authorized complete batched steps and no routine subagents; menu pauses are bypassed under that instruction.

## Requirements Inventory

### Functional Requirements

FR-1 — Three submission modes. Users can independently select Codebase, Repository or Website URL. Acceptance: each mode completes a real controlled fixture scan and produces a report. A failure message alone does not satisfy delivery; ZIP cannot be the sole input mode.
FR-2 — Full codebase submission. Accept a bounded source tree, preserve relative paths and identify accepted/excluded files. [ASSUMPTION A2: browser folder/file-tree upload is the initial transport; archive upload is optional.] Acceptance: a multi-directory JS/TS fixture retains its paths; invalid or oversized content is rejected with reasons; unsupported or unknown projects show explicit coverage rather than false success.
FR-3 — Repository submission. Retrieve a bounded source snapshot and record repository, requested reference and resolved commit. [ASSUMPTION A2: public GitHub HTTPS repositories first; private access and history scanning are deferred.] Acceptance: equivalent repository and uploaded-source fixtures yield the same seeded source findings under the same policy. Failed retrieval never starts a fictitious successful scan.
FR-4 — Website submission. Accept an authorized HTTP(S) target and use OWASP ZAP. [ASSUMPTION A3: baseline/passive, unauthenticated public targets; no active attacks.] Acceptance: the controlled deployment produces actual ZAP observations with target, policy and visited/excluded scope; disallowed destinations and unsafe redirects are rejected. Partial crawling is identified.
FR-5 — Recognized scope. Show project inventory for source and target scope for website scans. [ASSUMPTION A1: initial source coverage is JS/TS, including relevant React/Vite/Next.js/Node patterns.] Acceptance: unrelated languages/files and skipped checks cannot inflate completed coverage.
FR-6 — Source checks. Run Gitleaks and selected trusted Semgrep rules on codebase/repository submissions. Acceptance: planted fake private-credential and unsafe-input cases produce real rule/location evidence; tool/rule versions are recorded; submitted configuration cannot silently suppress mandated checks.
FR-7 — Required issue categories. Provide selected, validated detection coverage for credentials, unsafe input, insecure configuration and missing-access-check candidates. Acceptance: each category has at least one labeled vulnerable/control pair with expected rule/alert and observed evidence. An unsupported category is reported as a delivery gap, not claimed as implemented. Missing local authentication alone is not proof of bypass.
FR-8 — Browser-visible secrets. Check an explicitly bounded set of authorized browser-visible text assets for credential candidates. Acceptance: a fake private credential in the deployed fixture's visible asset is detected with asset URL and masked evidence. Record fetched/excluded asset scope. Do not assume stock ZAP alone supplies this capability or imply access to private backend source.
FR-9 — Public-key distinction. Explain credential confidence using available type/context. Acceptance: an intentionally public browser key control is not automatically labeled a private secret; potentially privileged credentials receive review and revoke/rotate guidance. Never test live credentials.
FR-10 — Actual tool states. Report queued, running, complete, failed, skipped and timed-out outcomes as applicable. Acceptance: timeout, missing tools/rules, malformed output and findings-bearing exit codes are distinguished using execution outcome plus valid report content. Failed checks cannot become zero-findings success.
FR-11 — Attributed findings. Each Finding includes originating tool/rule or alert, severity, confidence with rationale, source revision or target, actual location, sanitized evidence, explanation and repair guidance. Acceptance: source cases reference existing relative file/line; website cases reference observed URL/header/response or asset location. Unknown locations remain unknown rather than invented.
FR-12 — Interactive investigation. Users can filter by severity/tool, search title or location, select a Finding and inspect its evidence. Acceptance: filters alter the displayed set consistently; keyboard selection works; empty-filter results differ from a completed scan detecting nothing.
FR-13 — Grounded explanations. AI may explain bounded sanitized evidence, without inventing detections, locations or verified exploitability. Acceptance: explanations retain actual tool/rule references; unsupported claims are rejected or replaced with deterministic guidance. Report evidence remains usable if AI is disabled, unavailable or times out.
FR-14 — Consolidated repair prompt. Generate one copyable prompt containing relevant project/scan context, affected locations, required changes, constraints and verification steps. Acceptance: every included Finding maps to supplied evidence; copy success/failure is visible; fallback works without the model; all copied values remain sanitized.
FR-15 — Credential follow-up. Keep manual revoke/rotate instructions separate from code edits. Acceptance: relevant Findings and the Repair prompt retain this reminder after a finding disappears; the app never claims that source removal rotated a credential.
FR-16 — Real repeat execution. Repeat the checks for corrected codebase, new repository commit and updated website. Acceptance: a new Scan records its baseline relationship, revision/target, policy and tool versions; it does not reuse fabricated or stale findings as fresh output.
FR-17 — Honest classifications. Classify Findings as `still_detected`, `not_detected`, `newly_detected` or `unverified`. Acceptance: line shifts alone do not imply repair; failed/changed rules, uncertain matches or missing page coverage produce unverified outcomes. URL-only repeats cannot clear source Findings. Reserve `verified_fixed` for a repeatable behavior check proving removal of the failure condition; that label is not required in MVP.
FR-18 — Comparison evidence. Users can inspect both runs' evidence and coverage. Acceptance: show baseline/new revision or observation, completed-check counts, exclusions and status labels without relying only on color; retained key-rotation reminders remain visible.
FR-19 — Cohesive graphical workflow. Present submit/scan → investigate/repair → compare as three phases of one workspace. Acceptance: progress comes from actual events; loading, rejected input, partial scan, disconnected/retry, AI fallback, no findings and failed rescan states are distinct. Completed clean checks say “No findings detected within completed checks,” never “secure.”
FR-20 — Authorization and data choice. Require users to confirm permission for code, repositories and sites. Explain scope and external-model sharing before sending evidence. [ASSUMPTION A6: external AI can be disabled; only sanitized relevant evidence is shared after an explicit user choice.] Acceptance: disabling sharing prevents external model calls and still yields a usable deterministic Repair prompt. The permission statement does not replace network isolation.
FR-21 — Deletion and access. Restrict reports to the initiating operator/session and support deleting a Scan's retained source/report data. [ASSUMPTION A7: a single-team demonstration, not an unrestricted multiuser service.] Acceptance: another session cannot retrieve the report merely by guessing its ID; deletion prevents subsequent reads, removes retained artifacts and reports cleanup failures. Exact expiry policy must be fixed in architecture before implementation.

### NonFunctional Requirements

- NFR-1 — Secret handling: fake planted secret values must be absent from persisted reports, logs, model payloads, UI, clipboard and exports in the acceptance corpus. Test vendor fields independently of redaction flags. Bound temporary raw processing and clean it up; do not promise mathematically perfect detection/redaction.
- NFR-2 — Untrusted content: no submission can trigger app execution, installs, build scripts, arbitrary shell commands or model-controlled tools. Test hostile source comments/pages as data, including prompt-injection attempts.
- NFR-3 — Restricted execution: source retrieval and scanners must operate within documented finite input/output/time/resource limits. Reject traversal, links, special files and archive bombs where applicable. Test the approved limits and one over-limit case; architecture must fix numeric values before implementation.
- NFR-4 — Network isolation: website and asset requests must enforce target scope and permitted actual destination addresses, including DNS changes and redirects. Block internal/metadata destinations; bound request count, bytes and duration; protect the ZAP control interface. Test initial and redirected blocked destinations.
- NFR-5 — Reproducibility: record scanner/rules/policy versions and applicable coverage; keep lockfiles. Retrying or refreshing progress must not silently launch duplicate scans or change baseline identity.
- NFR-6 — Accessible presentation: all core actions work by keyboard with visible focus, text labels and readable contrast; support reduced motion. At 360px width, the workspace fits without page-wide horizontal overflow; code panels may scroll independently. [ASSUMPTION A8: 360px is the proposed narrow-layout acceptance viewport.] Sally specifies visual tokens and checks contrast.
- NFR-7 — Bounded failure: every accepted job reaches a terminal outcome within its documented deadline; model failure cannot block the evidence report. Measure actual elapsed times on the demonstration machine rather than promising untested latency.

### Additional Requirements

- AD-1 — Required independent intake [ADOPTED]
- AD-2 — One state owner
- AD-3 — One external contract
- AD-4 — Sanitized persistence boundary
- AD-5 — Fixed restricted source execution
- AD-6 — Repository retrieval shares intake policy
- AD-7 — Separate controlled website network
- AD-8 — Coverage-aware comparison
- AD-9 — Session ownership and deletion
- AD-10 — Model is a constrained explainer
- AD-11 — One finite profile
- AD-12 — Deployment and operational gate
- First story bootstraps the verified Vite react-ts starter, API and schema fixtures; immutable image/rule/lockfile checks precede safe execution.
- Shared API-CONTRACT v1 and safety-v1 profile are binding; SQLite is the single core-owned state store; no Redis/Celery or model-driven execution.

### UX Design Requirements

UX-DR1: Submission panel: three accessible mode tabs; path inventory/ref/URL fields, scope and limits, permission and model-sharing choice, pending duplicate prevention.
UX-DR2: Tool timeline: applicable tools and real backend states, measured elapsed time only, no synthetic percentage or completed spinner.
UX-DR3: Coverage banner: identity, versions, inspected/excluded scope and persistent partial/failure notices.
UX-DR4: Finding list: labeled search/severity/tool filters, selectable buttons, stable selection and distinct filter-empty state.
UX-DR5: Evidence detail: typed source/web locations, sanitized escaped snippets, rationale and impact; unavailable evidence explicit.
UX-DR6: Repair panel: consolidated sanitized prompt, copy success/failure and manual selection, fallback reason and rotation reminder.
UX-DR7: Comparison panel: preserved baseline, genuine repeat progress, four classifications, paired evidence and compatible coverage.
UX-DR8: Notice: inline field errors, persistent job failures, polite copy status, reconnect existing Scan rather than duplicate work.
UX-DR9: Confirmation dialog: named deletion scope, Cancel focus, Escape, focus restoration and truthful cleanup failure.
UX-DR10: Button: labeled keyboard action, stable pending/disabled behavior, accessible names and visible focus.
UX-DR11: Implement DESIGN.md semantic tokens, system fonts, 4-based spacing and component styles; no copied brand assets or remote-font dependency.
UX-DR12: Responsive list/detail desktop and stacked narrow workspace; 360px no page overflow, 200% zoom, local code scrolling and full location access.
UX-DR13: Keyboard reading-order navigation, focus management, 44px action targets, labeled errors and meaningful live announcements without poll spam.
UX-DR14: Reduced-motion handling and text-plus-icon status; tested foreground/background/focus combinations, no color-only classifications.
UX-DR15: All intake, scan, report, comparison, expired/access-denied/deletion states in EXPERIENCE.md have explicit recovery; no fake success.
UX-DR16: Codebase folder-browser fallback and clipboard failure behavior; unsupported browsers are disclosed, not falsely counted as supported.
UX-DR17: Preserve filters/baseline on refresh/new Submission and reconnect by Scan ID; no persistent browser secret/source cache.
UX-DR18: Retain source-grounded UJ-1/UJ-2/UJ-3 and three-phase evidence-first visual workspace; no chatbot or fake score.

### FR Coverage Map

FR-1: Epic 1, 2, 3
FR-2: Epic 1
FR-3: Epic 2
FR-4: Epic 3
FR-5: Epic 1, 2, 3
FR-6: Epic 1
FR-7: Epic 1, 3
FR-8: Epic 3
FR-9: Epic 1, 3
FR-10: Epic 1, 2, 3
FR-11: Epic 1, 3
FR-12: Epic 1
FR-13: Epic 4
FR-14: Epic 1, 4
FR-15: Epic 1, 4
FR-16: Epic 4
FR-17: Epic 4
FR-18: Epic 4
FR-19: Epic 1, 3, 4
FR-20: Epic 1, 3, 4
FR-21: Epic 1

## Epic List

### Epic 1: Review a codebase safely and act on real findings
Users submit source, inspect masked scanner evidence, copy deterministic repair guidance and control access/deletion. Foundation work stays inside this end-to-end user outcome.
**FRs covered:** FR-1, FR-2, FR-5, FR-6, FR-7, FR-9, FR-10, FR-11, FR-12, FR-14, FR-15, FR-19, FR-20, FR-21.

### Epic 2: Review a repository revision without manual upload
Users retrieve a public repository snapshot and receive the same trustworthy source review with resolved commit attribution.
**FRs covered:** FR-1, FR-3, FR-5, FR-10; inherits completed Epic 1 evidence/prompt behavior.

### Epic 3: Review a deployed website with ZAP and visible-asset evidence
Users scan an authorized public deployment, understand passive coverage and inspect ZAP plus browser-visible credential observations.
**FRs covered:** FR-1, FR-4, FR-5, FR-7, FR-8, FR-9, FR-10, FR-11, FR-19, FR-20.

### Epic 4: Receive grounded AI guidance and verify changes through rescans
Users optionally enable sanitized AI explanation, then genuinely repeat all supported input modes and compare observations without false repair claims.
**FRs covered:** FR-13, FR-14, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20.

### Epic 5: Demonstrate the complete workflow with repeatable evidence
The team can operate and evaluate every required mode on the demo machine, with accessible recovery and honest measured results.
**FRs covered:** cross-check all FR-1–FR-21 and NFR-1–NFR-7; no new product scope.

Epic 2 and Epic 3 can proceed independently after their Epic 1 prerequisites. Epic 4 builds on earlier modes; Epic 5 gates demonstration. No earlier epic requires a later epic to provide its stated user outcome. All are required for complete delivery; early partial milestones are not completion of the entire product.

## Epic 1: Review a codebase safely and act on real findings

Users can submit source, inspect real masked findings, copy deterministic guidance and delete retained data. No AI or website integration is needed for this epic's outcome.

### Story 1.1: Set up initial project from starter template and freeze contracts

As a team developer,
I want a reproducible starter and shared boundary fixtures,
So that separate UI and scanner work integrates without incompatible assumptions.

**Depends on:** none.
**Requirements:** FR-19; NFR-5; UX-DR11; AD-3, AD-12.
**Acceptance Criteria:**

- **Given** a clean checkout, **When** the documented bootstrap runs, **Then** the Vite react-ts workspace and FastAPI health endpoint build/start using recorded compatible locks; **And** candidate version changes are documented rather than silently floating.
- **Given** API-CONTRACT v1, **When** backend models/OpenAPI and frontend types are generated, **Then** source-running, partial, clean, website, AI-fallback, comparison and deletion fixtures validate against the same schema; **And** fixture UI is visibly development-only.
- **Given** the intended container runtime, **When** pinned scanner images are checked, **Then** actual Gitleaks/Semgrep/ZAP versions and immutable digests are recorded; **And** unavailable runtime/tooling creates a blocking feasibility result rather than fake scan success.
- **Given** no feature needs a table yet, **When** the starter is created, **Then** no speculative full database/entity set is created; **And** runtime data and credentials remain outside version control.

### Story 1.2: Accept an authorized bounded source tree

As a developer,
I want to submit my full source tree with clear limits,
So that I know exactly what the review will inspect.

**Depends on:** 1.1.
**Requirements:** FR-1, FR-2, FR-5, FR-20; NFR-2, NFR-3; UX-DR1, UX-DR15, UX-DR16; AD-1, AD-11.
**Acceptance Criteria:**

- **Given** valid folder/file-tree multipart input and permission confirmation, **When** submitted, **Then** relative paths, inventory, exclusions and external-sharing choice are recorded under the initiating session; **And** model sharing defaults off.
- **Given** traversal, absolute paths, links, special files, duplicate/case-colliding paths or missing multipart mappings, **When** validated, **Then** input is rejected safely before scanner dispatch; **And** field errors do not include raw source/credentials.
- **Given** each safety-v1 file/count/byte/path bound and one over-limit case, **When** streamed, **Then** the allowed boundary succeeds and over-limit input is rejected without unbounded buffering.
- **Given** unsupported project/browser input, **When** selected, **Then** inventory/coverage or browser limitation is explicit; **And** unsupported Codebase behavior is not counted as delivered support.

### Story 1.3: Run isolated jobs with owned status and deletion

As a submitting developer,
I want bounded private scans that I can track and delete,
So that failures and retained data stay under control.

**Depends on:** 1.2.
**Requirements:** FR-10, FR-21; NFR-3, NFR-5, NFR-7; UX-DR9; AD-2, AD-5, AD-9, AD-11.
**Acceptance Criteria:**

- **Given** accepted work, **When** the coordinator claims a job, **Then** one transactional core-owned claim dispatches restricted workers; **And** source is read-only, network disabled, quotas applied and no Docker socket/host secrets reach API or scanner jobs.
- **Given** duplicate Idempotency-Key requests, **When** retried, **Then** matching payload returns the original Scan and changed payload returns 409; **And** queue/deadline caps produce the documented status/error.
- **Given** another session, missing CSRF, timeout or coordinator crash, **When** access/recovery occurs, **Then** ownership/CSRF are enforced, abandoned work becomes explicitly failed and scratch cleanup runs.
- **Given** a running or completed Scan, **When** deletion is requested, **Then** it is immediately inaccessible, late commits are blocked and a deletion operation reports actual cleanup success/failure within policy; **And** expiry follows safety-v1.

### Story 1.4: Detect and sanitize source findings with trusted rules

As a developer,
I want real, located source findings without exposed secret values,
So that I can identify relevant repairs safely.

**Depends on:** 1.3.
**Requirements:** FR-6, FR-7, FR-9, FR-10, FR-11, FR-15; NFR-1, NFR-2; UX-DR5; AD-4, AD-5.
**Acceptance Criteria:**

- **Given** labeled fake-credential, unsafe-input, insecure-configuration and selected access-check fixtures plus protected/clean controls, **When** trusted Gitleaks/Semgrep rules run, **Then** expected rule/file/line evidence and actual misses/false alarms are recorded; **And** missing access checks remain candidates rather than proven bypasses.
- **Given** submitted config, ignore files or inline suppressions, **When** scanning, **Then** mandatory trusted checks cannot be silently disabled; **And** approved rule versions, hashes and distribution rights are recorded.
- **Given** vendor JSON with secret-bearing fields, **When** normalized, **Then** only typed sanitized findings cross persistence/log/API boundaries; **And** fake raw values are absent on tested outward surfaces, including unknown vendor fields.
- **Given** findings-bearing exits, invalid JSON, missing rules or timeout, **When** interpreted, **Then** findings and execution failures are distinguished; **And** a public browser key is not automatically private and relevant real-secret guidance includes revoke/rotate.

### Story 1.5: Investigate findings and copy a deterministic repair prompt

As a developer,
I want one accessible workspace for source evidence and repair guidance,
So that I can act without interpreting raw scanner output.

**Depends on:** 1.4.
**Requirements:** FR-12, FR-14, FR-15, FR-19, FR-20, FR-21; NFR-6; UX-DR2, UX-DR3, UX-DR4, UX-DR5, UX-DR6, UX-DR8, UX-DR9, UX-DR10, UX-DR11, UX-DR12, UX-DR13, UX-DR14, UX-DR15, UX-DR16, UX-DR17, UX-DR18; AD-3, AD-4.
**Acceptance Criteria:**

- **Given** an actual source report, **When** opening/filtering/selecting findings, **Then** tokens, list/detail, real timeline and coverage match the UX contracts; **And** typed locations, confidence, impact and repair use sanitized escaped text.
- **Given** findings or completed clean checks, **When** composing guidance, **Then** one deterministic prompt includes reported locations, required changes, verification and separate rotation actions; **And** no model is needed and no blanket secure verdict appears.
- **Given** clipboard failure, partial report, disconnect or delete failure, **When** the action fails, **Then** the specified recovery remains visible, copy permits sanitized manual selection, and reconnect checks the existing Scan without duplicating it.
- **Given** keyboard, reduced-motion, 360px viewport and 200% zoom, **When** core actions are exercised, **Then** focus/labels/contrast and local code scrolling meet the UX contract; **And** no hidden raw secrets or persistent source cache exists.

## Epic 2: Review a repository revision without manual upload

Users obtain equivalent source review from a recorded public repository snapshot. This epic reuses completed source review and introduces no Git history claim.

### Story 2.1: Retrieve a bounded public repository snapshot

As a developer,
I want to select a public repository and reference,
So that the review identifies the exact source revision assessed.

**Depends on:** 1.4.
**Requirements:** FR-3, FR-5, FR-10; NFR-3, NFR-4; AD-6, AD-11.
**Acceptance Criteria:**

- **Given** an allowed GitHub HTTPS identity/ref, **When** retrieved, **Then** fixed provider endpoints resolve a full commit and bounded archive; **And** only permitted public destinations/redirects are contacted.
- **Given** unsafe URL/ref, credential-bearing URL, blocked redirect, traversal/link archive, size/ratio abuse or timeout, **When** retrieved/extracted, **Then** validation rejects safely under safety-v1 with explicit failure rather than an empty successful scan.
- **Given** a valid snapshot, **When** passed through shared intake and scanners, **Then** source inventory, exclusions and attributed findings match equivalent uploaded source; **And** no clone hooks, submodule/LFS retrieval, install or build runs.

### Story 2.2: Review repository findings with commit attribution

As a developer,
I want repository submission and evidence in the same workspace,
So that manual upload is unnecessary and results remain reproducible.

**Depends on:** 2.1, 1.5.
**Requirements:** FR-1, FR-3, FR-11, FR-19; UX-DR1, UX-DR3, UX-DR15, UX-DR18; AD-1, AD-3.
**Acceptance Criteria:**

- **Given** Repository mode, **When** submitting a valid ref, **Then** the workspace displays requested/ref-resolved commit, actual progress, source findings and a usable prompt from live API output.
- **Given** denied repository/missing ref/retrieval failure, **When** rejected, **Then** input remains editable with a safe reason; **And** unsupported private/history capability is explicit.
- **Given** mode switching or refresh, **When** returning, **Then** accepted Scan identity and valid selected input/report state follow EXPERIENCE.md without duplicate retrieval.

## Epic 3: Review a deployed website with ZAP and visible-asset evidence

Users assess authorized public deployments with real passive alerts and bounded browser-visible credential observations.

### Story 3.1: Enforce authorized website networking and budgets

As a developer,
I want URL checks restricted to permitted destinations and scope,
So that a submission cannot access internal systems or crawl without limits.

**Depends on:** 1.3.
**Requirements:** FR-4; NFR-3, NFR-4, NFR-7; AD-7, AD-11, AD-12.
**Acceptance Criteria:**

- **Given** an allowed public origin, **When** ZAP/asset traffic connects, **Then** all traffic uses enforced connection-time public-destination checks and trusted request/response counters; **And** direct egress is blocked and ZAP control is private.
- **Given** private/reserved/metadata addresses, mapped IPv6, DNS rebinding, unsafe redirects, alternate ports or over-budget responses, **When** attempted, **Then** connections are rejected/terminated under safety-v1 and coverage is explicitly incomplete.
- **Given** the selected runtime cannot demonstrate these controls, **When** readiness is checked, **Then** arbitrary URL submission stays disabled and the missing required capability is reported; **And** fixture-only operation is not declared delivery.

### Story 3.2: Produce located ZAP baseline findings

As a developer,
I want real passive deployment observations,
So that exposed configuration risks have actionable URL evidence.

**Depends on:** 3.1, 1.4.
**Requirements:** FR-4, FR-7, FR-10, FR-11; AD-1, AD-3, AD-7.
**Acceptance Criteria:**

- **Given** a controlled vulnerable site, **When** pinned ZAP baseline runs, **Then** actual alert IDs, sanitized URL/header/response evidence, version/policy and visited/excluded resources are normalized; **And** no active attacks or private-source claims occur.
- **Given** WARN/FAIL finding exits, execution error, invalid/truncated JSON or timeout, **When** adapted, **Then** valid findings and execution failure are distinguished and no failed crawl becomes clean success.
- **Given** a corrected/clean deployment, **When** checked, **Then** actual expected alerts and other observed warnings are recorded without suppressing inconvenient output.

### Story 3.3: Detect secrets in bounded visible assets

As a developer,
I want exposed browser-readable credentials identified,
So that deployment-visible risks are not missed by relying on ZAP alerts alone.

**Depends on:** 3.2.
**Requirements:** FR-8, FR-9, FR-10, FR-11; NFR-1, NFR-4; AD-4, AD-7.
**Acceptance Criteria:**

- **Given** same-origin linked text assets with a planted fake private credential, **When** fetched/scanned through the enforced network and trusted detector, **Then** masked asset URL/actual text location evidence is returned and temporary filenames are mapped correctly.
- **Given** public-key controls, runtime-loaded/unvisited or cross-origin assets, **When** assessed, **Then** no automatic private-key claim occurs and omitted coverage is explicit; **And** no JavaScript/application code executes.
- **Given** asset/request/byte/time/output bounds or sanitization failure, **When** exceeded, **Then** the asset check is incomplete, raw values do not reach outward channels and overall completeness reflects the failure.

### Story 3.4: Investigate website findings in the shared workspace

As a developer,
I want website submission, evidence and repair guidance together,
So that I can act on deployment observations with clear limitations.

**Depends on:** 3.3, 1.5.
**Requirements:** FR-1, FR-4, FR-5, FR-12, FR-14, FR-19, FR-20; UX-DR1, UX-DR2, UX-DR3, UX-DR5, UX-DR6, UX-DR15, UX-DR18; AD-1, AD-3.
**Acceptance Criteria:**

- **Given** Website URL mode and permission, **When** an accepted scan runs, **Then** actual ZAP/asset states, passive scope, observed URL evidence and coverage are rendered without invented source paths.
- **Given** blocked input, partial crawl, no alerts or missing asset evidence, **When** reported, **Then** the exact UX limitation/recovery appears, completed-count semantics remain truthful and prompt guidance uses available evidence only.
- **Given** a successful live report, **When** copied, **Then** one sanitized repair prompt and relevant human rotation reminder are usable without the model.

## Epic 4: Receive grounded AI guidance and verify changes through rescans

Users can explicitly choose sanitized AI explanation and compare genuine repeat checks across all required modes.

### Story 4.1: Add opt-in bounded AI explanations with fallback

As a developer,
I want optional AI explanations grounded in my findings,
So that repair advice is understandable without sharing raw source or losing the fallback.

**Depends on:** 1.5.
**Requirements:** FR-13, FR-14, FR-15, FR-20; NFR-1, NFR-7; UX-DR6; AD-10.
**Acceptance Criteria:**

- **Given** sharing disabled, **When** a report is composed, **Then** no external request occurs and deterministic guidance remains usable.
- **Given** sharing enabled and a configured provider, **When** bounded sanitized findings are sent once, **Then** only valid existing IDs/locations are accepted and core composes the master prompt; **And** injected source/page instructions cannot trigger tools or widen sharing.
- **Given** timeout, invalid/invented output, unavailable provider or limit overflow, **When** processed, **Then** deterministic guidance covers affected/remaining Findings with an explicit reason and preserves rotation advice.

### Story 4.2: Execute real rescans and classify comparable findings

As a developer,
I want a corrected submission assessed again against its baseline,
So that changes are supported by comparable evidence.

**Depends on:** 2.2, 3.4.
**Requirements:** FR-16, FR-17, FR-18; NFR-5; AD-2, AD-8, AD-9.
**Acceptance Criteria:**

- **Given** source/repository/website baselines, **When** corrected same-mode inputs are submitted, **Then** actual scanners execute in new owned Scans with revision/observation and lineage; **And** baselines are preserved.
- **Given** compatible rules/scope and deterministic matches, **When** compared, **Then** still_detected/not_detected/newly_detected are correct for labeled cases; **And** shifted lines alone do not imply repair.
- **Given** failed tools, lost pages, changed fingerprints, ambiguous duplicate matches or cross-mode input, **When** comparison is requested, **Then** uncertainty yields unverified or the contract's conflict response; **And** URL results never clear source findings.
- **Given** no behavior-proof test, **When** a finding disappears, **Then** verified_fixed is never emitted and relevant baseline human rotation actions remain available.

### Story 4.3: Inspect paired rescan evidence and recovery

As a developer,
I want before/after findings and coverage in the workspace,
So that I can explain what changed and what remains uncertain.

**Depends on:** 4.2.
**Requirements:** FR-16, FR-17, FR-18, FR-19; UX-DR7, UX-DR13, UX-DR14, UX-DR15, UX-DR17, UX-DR18; AD-3, AD-8.
**Acceptance Criteria:**

- **Given** a baseline, **When** Rescan is selected, **Then** same-mode inputs, permission and actual progress appear while baseline evidence stays accessible.
- **Given** terminal comparison, **When** a Finding is selected, **Then** both revisions/observations, paired sanitized evidence, classification reason and coverage are available; **And** narrow view stacks baseline then new with text labels.
- **Given** failed repeat, expired baseline, disconnect or changed coverage, **When** displayed, **Then** no fixed-success state appears and deliberate retry/recovery follows EXPERIENCE.md; **And** keyboard focus/selection remain stable.

## Epic 5: Demonstrate the complete workflow with repeatable evidence

The team can operate and verify all required modes on the actual demonstration machine. This epic verifies earlier features rather than adding optional product scope.

### Story 5.1: Run the labeled acceptance and adversarial corpus

As a hackathon evaluator,
I want a repeatable real-output demonstration and failure evidence,
So that detection, repair and comparison claims can be assessed honestly.

**Depends on:** 4.3.
**Requirements:** FR-7, FR-8, FR-9, FR-10, FR-13, FR-16, FR-17, FR-21; NFR-1, NFR-2, NFR-3, NFR-4, NFR-5, NFR-7; AD-12.
**Acceptance Criteria:**

- **Given** a labeled vulnerable/corrected/clean matrix covering all four issue categories across the product and all three input modes within their supported capabilities, **When** run on the demo machine, **Then** expected/observed rules/alerts, locations, versions, coverage and elapsed runtime are saved as sanitized evidence; **And** source/repository cases validate selected unsafe-input and access-check rules, website cases validate actual passive alerts and visible-asset secrets, unsupported matrix cells have explicit reasons, and required mode completion is 3/3 rather than three error screens.
- **Given** the hostile path/config/network/session/CSRF/idempotency/deletion/crash and model-outage corpus, **When** exercised, **Then** documented boundaries hold or failures block release; **And** fake private values are absent from all outward tested surfaces.
- **Given** recorded outcomes, **When** metrics and guidance are assessed, **Then** issue-occurrence TP/FP/FN, denominators, misses and per-criterion prompt utility are reported without invented accuracy/speed; **And** incomplete coverage cannot game results.

### Story 5.2: Verify accessible recovery and rehearse the honest demo

As a team presenter,
I want a usable, rehearsed application and operator guide,
So that the demonstration is reliable and its limitations are clear.

**Depends on:** 5.1.
**Requirements:** FR-19; NFR-6; UX-DR11, UX-DR12, UX-DR13, UX-DR14, UX-DR15, UX-DR16, UX-DR17, UX-DR18; AD-12.
**Acceptance Criteria:**

- **Given** all three UX journeys, **When** tested at desktop/360px, 200% zoom, keyboard and reduced motion, **Then** core actions, focus, labels, status announcements, contrast and evidence reflow pass; **And** findings/fixes are recorded rather than asserting accessibility from tokens alone.
- **Given** each specified error/empty/partial/denied/expired state and unsupported clipboard/folder behavior, **When** encountered, **Then** recovery copy and actions match EXPERIENCE.md without data loss or duplicate scans.
- **Given** a clean start on the demo machine, **When** the operator guide is followed, **Then** versioned setup, real scan/repair/rescan, cleanup and failure recovery are rehearsed; **And** fixture-only limitations and pending issues are disclosed, not hidden behind mock output.

## Delivery and assignment notes

All stories are proposed and unimplemented; actual people are unassigned. Assign one owner per GitHub story and link its PR; use these stable IDs in downstream issues. No estimate or commitment fits an unknown remaining time/team capacity. After prerequisites, repository and website work can proceed in parallel; optional AI work can start after source review. The ZAP egress feasibility story is the highest-risk parallel path and must not wait until final integration.

Trivy/OSV, private/history access, active/authenticated scanning, combined modes and decorative motion have no P0 stories. Required categories, modes, safety, masking and truthful comparison cannot be cut silently. Readiness reviews coverage and blockers next; GitHub publication happens only after that stage, using this backlog rather than a second competing list.


## Final scope refinements — 2026-10-23

Story 4.3 requires comparison backend 4.2, not optional AI 4.1. AI remains a planned feature with its own acceptance; disabling it must not block comparison. Story 4.2 retains its final repository/website prerequisites and all-mode acceptance, but developers should prototype and test source comparison once 1.5 is complete, without marking 4.2 ready or done ahead of its dependencies.

Create vulnerable/corrected/clean fixtures alongside each scanner adapter and rehearse source scan → deterministic repair prompt → corrected rescan early. Story 1.1 proves runtime availability; start Story 3.1 as soon as 1.3 permits it to prove ZAP egress and choose an authorized public demo target compatible with safety-v1. A local target cannot silently bypass the public-origin policy. Epic 5 remains the final integrated corpus gate. Team capacity and actual timings must determine the delivery commitment.
