# Epic 1 Context: Review a codebase safely and act on real findings

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Enable developers to submit an authorized source tree, understand its accepted and excluded scope, inspect real masked scanner evidence, copy deterministic repair guidance, and control access and deletion. This epic delivers the source-review loop without requiring AI or website integration; unsupported coverage and execution failures must remain explicit.

## Stories

- Story 1.1: Set up initial project from starter template and freeze contracts
- Story 1.2: Accept an authorized bounded source tree
- Story 1.3: Run isolated jobs with owned status and deletion
- Story 1.4: Detect and sanitize source findings with trusted rules
- Story 1.5: Investigate findings and copy a deterministic repair prompt

## Requirements & Constraints

- Initially assess JS/TS and relevant React/Vite/Next.js/Node source/configuration. Preserve safe relative paths, relevant dotfiles and lockfiles. Identify vendor, node_modules, build outputs, unrelated languages and other exclusions with reasons; exclusions cannot inflate coverage.
- Require explicit permission confirmation. External AI sharing defaults off and needs a per-submission choice; deterministic guidance remains usable without model access. Treat source comments, configurations and instructions as untrusted data. Never execute submitted applications, install/build scripts, hooks or arbitrary commands.
- Stream bounded folder/file-tree input: 25 MiB aggregate, 5,000 files, 2 MiB/file, depth 20 and 240 UTF-8 bytes/path. Reject absolute/traversal paths, links, devices, duplicate or normalized/case-colliding paths, and missing/duplicate/unmapped multipart parts before dispatch. Errors expose safe fields/reasons, never raw source or credentials.
- Admit one running job and at most three queued jobs system-wide; excess admission returns 429. Queue wait is at most 600s; running jobs at most 300s, source tools 90s each. Workers have 2 CPU, 2 GiB RAM, 128 processes, 256 MiB scratch and 5 MiB vendor output per tool.
- Distinguish queued/running/complete/failed/skipped/timed-out outcomes. A failed or truncated check cannot become zero-findings success. Complete requires every required tool and intended scope to complete; partial requires useful sanitized evidence with incomplete checks/scope; failed means no usable report evidence/coverage.
- Detect credential, unsafe-input, insecure-configuration and selected missing-access-check candidates with labeled vulnerable/control cases. Missing local authentication is not proof of bypass; public browser keys are not automatically private secrets. Never test live credentials.
- Keep fake secret values out of persisted reports, logs, UI, model payloads, clipboard and exports. Bound raw scratch processing and test vendor fields independently of redaction flags. Reports cap at 1,000 findings, 2 KiB evidence/finding, 128 KiB repair prompt and 5 MiB sanitized report; overflow must disclose incomplete coverage.

## Technical Decisions

- Use a hexagonal modular monolith: core alone owns transitions, queue claims and sanitized report commits. SQLite is the single state store; a trusted host coordinator transactionally claims one job at a time. Workers cannot access the database. Recovery marks abandoned work failed, cleans scratch and never automatically repeats scans.
- Keep the application same-origin and loopback-only for the local team demo. Runtime storage is private, outside the checkout and outside OneDrive. API and scanners never receive a Docker socket or host secrets; only the trusted coordinator controls the runtime.
- Launch source scanners with fixed allowlisted argument arrays and reviewed pinned images/rules. Source mounts read-only; root filesystem read-only; scratch separate; workers non-root, network-disabled, capabilities dropped and no-new-privileges. Uploaded config, ignore files and inline suppressions cannot silently disable mandated checks. Immutable digests, versions and rule/policy fingerprints must be recorded.
- Use API v1 as the shared boundary and validate generated types/schema fixtures together. Codebase multipart metadata maps each part_id to one relative_path; browser filenames are not authority. Ownership checks apply to every resource. Random server sessions use HTTP-only SameSite=Strict cookies and CSRF-protected mutations; unavailable and unauthorized resources share a nonrevealing 404.
- Idempotency keys are session-scoped with canonical payload comparison and 24h expiry: identical retry returns the original Scan; changed payload returns 409. Errors use stable codes and safe messages. Progress refresh reconnects by Scan ID rather than launching work.
- Only typed sanitized findings cross persistence/API boundaries. Strip unknown vendor fields, never log raw stdout/stderr, escape snippets and sanitize display paths/URLs. Source locations reference existing relative paths and positive real lines; unknown locations stay unknown. Findings retain tool/rule, severity, confidence rationale, evidence, impact, repair, verification and human actions.
- Tombstone scans immediately on deletion, deny reads and late worker commits, stop work and remove artifacts. Deletion operations report real pending/complete/failed cleanup; deadline is 60s with safe retry. Raw scratch cleanup runs on termination/deletion/recovery; startup and 60s sweep remove abandoned/expired data. Cleanup failure is visible and blocks unrestricted intake. Sanitized reports expire 24h after terminal time; sessions expire after 24h inactivity; lost cookies have no recovery.

## UX & Interaction Patterns

- Maintain one graphical workspace with Submit & scan, Investigate & repair, and Rescan & compare phases. Preserve a completed report when opening a new submission. Codebase selection needs accessible folder/file-tree controls, inventory/exclusions, configured limits, permission and sharing choices, and disabled duplicate activation while pending. Disclose unsupported browser behavior and path-preserving fallback limitations.
- Render actual backend tool states and coverage, with no synthetic percentages, invented security score or blanket secure verdict. Clean results say “No findings detected within completed checks.” Distinguish rejected inputs, unsupported scope, disconnect, partial report, failed job and filter-empty results; reconnect existing work deliberately.
- Use labeled filters, keyboard-selectable findings, escaped masked evidence and a consolidated template repair prompt. Provide visible copy success/failure and sanitized manual selection. Keep revoke/rotate guidance as a separate human action and inside the prompt; removing source does not rotate credentials.
- Follow DESIGN.md semantic tokens, system fonts and 4-based spacing. Desktop list/detail stacks on narrow screens; preserve full locations, local code scrolling, 360px reflow and 200% zoom. Use visible focus, labeled errors, text-plus-icon status, 44px targets and reduced motion. Announce meaningful transitions without poll spam. Deletion confirmation starts on Cancel, supports Escape and restores focus; cleanup failure stays explicit. Never persist source/secrets in browser storage.

## Cross-Story Dependencies

Story 1.1 freezes the reproducible foundation and contracts; 1.2 depends on it, 1.3 on 1.2, 1.4 on 1.3 and 1.5 on 1.4. Repository retrieval later reuses source intake/scanners; controlled website networking can begin after 1.3. Neither later mode nor optional AI blocks this epic's source outcome. Genuine source comparison should be prototyped after 1.5, while final all-mode comparison remains later work.
