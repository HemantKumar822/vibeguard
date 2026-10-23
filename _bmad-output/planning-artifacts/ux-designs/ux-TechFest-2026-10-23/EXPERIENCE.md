---
name: AI Security Reviewer experience
status: final
created: 2026-10-23
updated: 2026-10-23
approval: pending-user-review
sources:
  - ../../prds/prd-TechFest-2026-10-23/prd.md
  - ../../prds/prd-TechFest-2026-10-23/addendum.md
---

## Foundation

Responsive web workspace for the developer and controlled hackathon demonstration. [DESIGN.md](DESIGN.md) is the visual identity contract; no UI component library or frontend framework choice is imposed here. Initial source/provider/ZAP restrictions inherit PRD A1–A8 and remain provisional. Preserve the PRD's vocabulary: Submission, Scan, Finding, Coverage, Repair prompt and Comparable scan.

Fast-path documentation only: no mockups, imports, installed design preset or rendered screens. Exact layout defaults inherit UX-A1/UX-A2 in DESIGN.md. All surfaces are deliberately spine-only to keep this stage fast.

## Information Architecture

One workspace, three phases; no marketing, chat, account, admin or analytics surface. Route/API shapes are architecture decisions. In-progress jobs and prior reports are separate states: opening New submission must not destroy a completed baseline.

| Surface | Entry and exit | Required content / journey |
| --- | --- | --- |
| Submit & scan | Initial workspace or New submission; accepted Scan moves into progress then results | Three input modes, scope/limits, permission, optional external-AI choice, tool timeline and coverage; UJ-1/UJ-2 |
| Investigate & repair | Completed/partial report; New submission or Rescan available | Coverage banner, finding list, evidence detail and repair panel; UJ-1/UJ-2 |
| Rescan & compare | Rescan from a baseline; new run then comparison; Back to report preserves baseline | Same-mode corrected input, actual repeat progress, classification list and paired evidence; UJ-3 |

Deletion confirmation is a dialog over the current surface, not a separate destination. Missing/expired/deleted reports show an explanation and New submission action without exposing another session's data.

## Voice and Tone

Use precise plain language. Findings are potential issues unless supported by stronger evidence. Explain next steps without blame or promises.

| Situation | Copy pattern |
| --- | --- |
| Input mode | “Codebase” / “Repository” / “Website URL” |
| Authorization | “I have permission to assess this code, repository or site.” |
| External AI | “Allow sanitized evidence to be sent to the configured AI service.” Default off under UX-A3; explain that raw source/credentials are not intended for sharing |
| Clean completed checks | “No findings detected within completed checks.” |
| Partial report | “Some checks did not complete. Results cover completed checks only.” |
| Website limit | “ZAP baseline/passive review. Private backend source is not available from this URL.” |
| AI unavailable/disabled | “Template guidance is available. AI explanation did not run.” Include actual reason |
| Not detected | “Not detected on this comparable rescan. This does not prove the issue is fixed.” |
| Missing coverage | “Unverified: this check or location was not assessed comparably.” |
| Credential action | “Human action: revoke or rotate the exposed private credential.” |

**[ASSUMPTION UX-A3]** External-AI sharing defaults off until explicitly selected for the Submission. PRD A6 requires a choice; this default is proposed. A source contains untrusted instructions, not permission to change that choice.

## Component Patterns

Visual anatomy uses DESIGN.md. Foreground text follows `{colors.text}`, supporting metadata `{colors.muted}`, and focus `{colors.focus}`. Never expose a raw secret in DOM attributes, accessible labels, copy buffers or tooltips.

| Component | Behavioral contract |
| --- | --- |
| Submission panel | Keyboard-operable mode tabs; retain each mode's entered value while switching. Codebase: Select folder/file tree, accepted file inventory and exclusions; drag/drop only where supported, not the only method. Repository: URL and optional ref, resolved commit shown after retrieval. Website: HTTP(S) URL, passive scope and authorization. Reject locally for convenience but backend is authoritative. Show configured limits, not invented numbers. Scan is disabled until required fields/permission pass. Pending submission disables duplicate activation |
| Tool timeline | Applicable tools only, plus explicit not-applicable/skipped information. Show queued/running/complete/failed/timed-out states from backend. Never animate a completed or failed tool as running; do not estimate percentage from timers |
| Coverage banner | Show input identity, actual tools/rules versions and covered/excluded scope; expand technical detail on request. Persistent partial/failure notice; a completed tool is not a secure-project verdict |
| Finding list | Labeled severity/tool filters and title/location search; native list of selection buttons, not an inaccessible fake grid. Selection opens detail and persists across status refresh. If filtered out, clear hidden selection and show results count. No automatic severity suppression |
| Evidence detail | Display actual typed source/web location, masked snippet, confidence rationale, impact and repair. Missing snippet says unavailable; unknown lines remain unknown. Code is escaped text, not HTML. Opening a finding does not automatically fetch its URL or execute content |
| Repair panel | Consolidated sanitized prompt; Copy announces success/failure. If clipboard fails, allow manual selection of the sanitized prompt. Show deterministic fallback and model-sharing status. Rotation reminder is outside the copied code-change instructions and also included as a human-action section in the prompt |
| Comparison panel | Rescan reuses baseline mode/policy where supported, with explicit revision/URL input and permission. New run never overwrites baseline. Show still_detected/not_detected/newly_detected/unverified, each with explanation and both runs' coverage. A mode/policy change yields unverified rather than silently clearing findings |
| Notice | Input errors next to fields, persistent job failures near coverage; copy feedback via polite live status. Recovery reconnects to existing Scan first. Starting another Scan is a separate deliberate action |
| Confirmation dialog | Delete names the Scan and retained data being removed; Cancel is initially focused, Escape cancels, Delete confirms. Return focus to trigger or New submission if trigger was removed. Failure retains notice; do not claim deletion succeeded until confirmed |
| Button | Standard Enter/Space behavior; a pending action is disabled/labeled without moving focus. Icon-only controls require accessible names; meaningful actions always have visible text where space permits |

## State Patterns

| Surface / state | Visible behavior and recovery |
| --- | --- |
| Submit: cold/empty | Mode choice, supported scope, permission and sharing controls; Scan disabled until input valid; no preselected example disguised as real data |
| Submit: unsupported folder browser | Explain limitation; offer bounded file selection preserving paths where supported. If unavailable, Repository remains usable; this does not count as delivered Codebase support on that browser |
| Submit: invalid/oversized/unsupported | Preserve input where safe; show backend reason and accepted/excluded inventory; no successful Scan is fabricated |
| Submit: repository denied/missing ref | Show retrieval failure and editable fields; never imply history or private access is supported |
| Submit: URL blocked/unauthorized | Explain disallowed target/scope without leaking internal response data; no automatic attempt through a different address |
| Scan: queued/running | Actual tool timeline; optional measured elapsed time. User can inspect available partial evidence while terminal status remains clear |
| Scan: disconnected | “Connection lost; scan status unknown.” Retry status for the existing job; never mark clean or start duplicate work automatically |
| Scan: failure/timeout | Show failed checks, partial results if available and explicit Retry/New scan actions. No green success state |
| Report: no findings | State completed coverage and limitations; show valid repeat-scan action; no blank unexplained panel |
| Report: filter empty | “No findings match these filters.” Clear filters action; overall report totals remain distinct |
| Report: partial/missing evidence | Persistent coverage warning; missing snippet explanation; guidance references only available evidence |
| Report: AI disabled/unavailable | Evidence intact; template Repair prompt and actual reason; no fabricated AI prose |
| Compare: waiting/running | Baseline remains accessible; actual repeat timeline; classification withheld until comparable evidence exists |
| Compare: failure/mismatched coverage | Show unverified for affected findings; preserve baseline evidence; retry is deliberate |
| Any: expired/deleted/access denied | Nonrevealing unavailable-report state and New submission; no neighboring report metadata |
| Any: delete failed | Keep data/status visible and explain retry; no optimistic disappearance that implies cleanup succeeded |

## Interaction Primitives

Tab order follows reading order: input/mode → consent/permission → Scan → tool/coverage detail → filters → findings → evidence → Repair prompt → Rescan/Delete. Selecting a mode does not submit. On accepted Scan, move focus to its status heading; on terminal results, announce completion without stealing focus if the user is already investigating evidence.

On narrow layouts, selecting a Finding moves focus to the detail heading with a Back to findings action that restores the prior selection. Standard keyboard navigation handles tabs, buttons and dialogs; no unmodified global shortcuts intercept typing. New submission preserves the prior completed report in the active session until deletion/expiry; do not promise survival across browser restart before architecture resolves persistence.

Refresh/polling updates statuses without reordering focused content. Preserve filters/selection where still valid. Escape closes the topmost dialog/popover; never silently cancels a running scan. Cancellation is not a required MVP feature. Reduced-motion disables transitions and spinner motion; a static Running label remains.

## Accessibility Floor

All actions must work without mouse or drag/drop. Use semantic headings, labeled form controls, field-error associations and polite status announcements. Do not announce each poll or every elapsed second; announce meaningful tool transitions and completion. Errors requiring action are announced once.

Use 44×44px minimum action targets, visible focus and no keyboard trap except managed modal focus. Zoom/reflow at 200% and narrow 360px layout must preserve actions and evidence; content can wrap, code scrolls independently. Severity, confidence and comparison states have text labels. Contrast uses DESIGN.md's tested pairs; actual component combinations require implementation verification. No hidden secrets in accessibility descriptions.

## Responsive & Platform

Desktop uses list/detail columns; tablet reduces list width; phone stacks list → detail → repair. Comparison pairs become baseline then new for the same Finding. Keep context and classification adjacent. Long paths wrap or scroll locally; never truncate the only accessible value. Browser folder-upload and clipboard limitations must have explicit states. Network reconnection is not offline scanning; no source, credential or prompt is cached in browser persistent storage by this spec.

## Inspiration & Anti-patterns

Preserve the reference pack's cinema-black restraint, bold submission entry and dense evidence clarity. No copied Bugatti assets or preset assumptions. Reject giant type in reports, a chatbot conversation shell, fabricated scores, fake progress, hover-only controls and disappearing error notices. Motion follows real events and is first to cut under time pressure.

## Key Flows

### UJ-1 — Hemant reviews source

1. Hemant selects Codebase or Repository; enters input, reads coverage, confirms permission and chooses model sharing.
2. Scan validates the input; the accepted Scan displays actual Gitleaks/Semgrep states and source identity/commit.
3. Hemant filters Findings and selects one; the detail shows an existing file/line, masked evidence, confidence and repair.
4. **Climax:** Copy produces one usable sanitized Repair prompt with locations, verification and relevant rotation guidance.
5. Hemant changes source in his coding tool, then chooses Rescan.

Failure: unsupported input or retrieval failure stays editable with a clear reason. Tool or AI failure preserves actual evidence, incomplete coverage and fallback guidance rather than a fake clean state.

### UJ-2 — Hemant reviews a deployment

1. Hemant selects Website URL, sees passive ZAP scope, enters the authorized target and confirms permission/sharing choice.
2. The Scan runs within approved network policy; progress shows ZAP and browser-asset checking applicability separately.
3. Hemant inspects observed URL/response/header/asset evidence and visited/excluded scope; private source is never implied.
4. **Climax:** Hemant receives actionable deployment/code guidance and one copyable Repair prompt grounded in those observations.
5. After updating the deployment, he chooses Rescan.

Failure: blocked destination or unsafe redirect is rejected; partial crawl remains incomplete; missing asset coverage does not become a secret-free verdict.

### UJ-3 — Hemant checks changes

1. From a baseline report, Hemant chooses Rescan and supplies corrected same-mode input or confirms the target.
2. The actual repeat run records new revision/observation and policy without replacing baseline evidence.
3. Comparison shows each classification and compatible coverage; Hemant opens a Finding to inspect both observations.
4. **Climax:** Hemant can explain what was still detected, not detected, newly detected or unverified, with the evidence for that label.
5. Human rotation reminders remain visible; he can copy remaining repair guidance or explicitly delete retained Scan data.

Failure: changed policy, lost pages, failed tool or uncertain matching yields unverified. A website-only Scan never clears source Findings; no unsupported verified-fixed celebration appears.
