# 03 — Validation, Safety and Delivery Gates

**These checks are acceptance targets; no scans have been run for this pack.**

## The smallest truthful demonstration

Prepare a controlled JS/TS example with three revisions:

- **Vulnerable:** a realistic-looking **fake** private credential and one unsafe code pattern recognized by the selected Semgrep rule configuration.
- **Corrected:** both planted risks addressed; mention that *real* leaked keys require separate revocation/rotation.
- **Clean control:** no planted vulnerabilities, with a deliberately public browser key to check obvious false alarms.

Record expected findings/rule IDs for each sample. Confirm the scanners actually detect the planted cases **before** scripting the demo. Never use live credentials or mark fixture output as production security verification.

## P0 acceptance checklist

- [ ] ZIP import rejects traversal, absolute paths, symlinks, too many files and decompression bombs with usable errors.
- [ ] Scanner runs are restricted, isolated, time-bounded, non-root where possible and do not run app code, install scripts or builds.
- [ ] Gitleaks detects planted fake credential and returns redacted location/rule evidence.
- [ ] Semgrep detects seeded JS/TS issue with the correct file and line; clean control doesn't produce that planted finding.
- [ ] Scanner timeout, broken tool, invalid JSON and missing rule pack are **visible failures**, not success with zero findings.
- [ ] Raw secret-like values do not appear in persisted reports, application logs, response bodies, LLM inputs or repair prompts.
- [ ] Findings UI is interactive and driven by live scanner data; progress and failure states are understandable.
- [ ] AI output explains observed problems, suggests specific safe changes and cites real file/line evidence. Fallback works without AI.
- [ ] One copyable repair prompt includes meaningful verification checks and separate key-rotation guidance.
- [ ] Corrected ZIP triggers the same two scanners; before/after UI displays changes and tool coverage.
- [ ] A failed second scan cannot say anything was fixed. A shifted line or changed hash does not automatically imply a verified repair.
- [ ] End-to-end test is repeated on the actual demonstration machine. Report **measured** runtime; no unsupported speed guarantee.

## Basic security boundary (must not be cut)

| Risk | Protection |
| --- | --- |
| Hostile ZIP | Canonical path checks, strict extracted size/count limits, reject links and special files |
| Untrusted code execution | No `npm install`, scripts, `next build`, repo-defined commands, or launching uploaded website |
| Scanner process access | Disposable non-root workers, read-only source mount, output limits, no host keys/socket, CPU/memory/time limits |
| Sensitive data in output | Redact early; don't keep raw tool output longer than necessary; never send raw credentials to external models |
| Scanner false confidence | Show each tool's coverage and failures; no blanket 'secure' claims |
| Prompt injection in source | Comments/strings/files are evidence, not instructions to the AI reviewer |

If full isolation is not ready, **restrict the hackathon demonstration to team-owned known-safe fixtures**, rather than exposing an unsafe general-purpose upload service to arbitrary users.

## Working in parallel: 24-hour guide, not a second issue plan

| Approximate window | Outcome, not a feature list |
| --- | --- |
| Hours 0–2 | BMAD creates approved stories; team freezes JSON/API; smoke-test scanner CLI on fixture; design owner reads `DESIGN.md` |
| Hours 2–8 | Safe upload/coordinator and two scanner adapters; visual UI built against mocks in parallel |
| Hours 8–14 | Normalized redacted results and live findings view; integrate first end-to-end scan |
| Hours 14–19 | AI repair prompt, corrected ZIP rescan and truthful before/after UI |
| Hours 19–24 | **Freeze features**, fix integration failures, test edge cases, polish and rehearse demo |

Keep ownership clear through GitHub Issues/Projects, created by your BMAD process. One owner per issue, small PRs and shared API contracts. **Do not schedule optional features before the whole P0 loop works.**

## Go / no-go and cut rules

**Go for implementation:** Scope and module responsibilities are sufficiently defined for BMAD planning.  
**Go for demo:** Real outputs from Gitleaks and Semgrep; mask applied; repair prompt usable; actual second scan; honest graphical comparison.  
**Cut first:** URL scanning → third scanner → extra rules/frameworks → ornamental animation.  
**Never cut:** safe input handling, masking, failure visibility, evidence location, rescan truthfulness or basic graphical usability.

## Handoff

Use `README.md`, `01_RESEARCH_AND_SCOPE.md`, `02_PRODUCT_AND_ARCHITECTURE.md`, this document and the team's future `DESIGN.md` as BMAD input. The team runs BMAD. **No other agent framework or ticket system is required.**
