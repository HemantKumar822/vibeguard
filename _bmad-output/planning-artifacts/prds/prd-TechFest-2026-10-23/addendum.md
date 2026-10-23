# PRD supporting decisions

Date: 2026-10-23. Product requirements live in [prd.md](prd.md). This file preserves source depth and mechanism candidates, not a second requirements list or implementation approval.

## Input reconciliation

Mary's [brief](../../briefs/brief-TechFest-2026-10-23/brief.md), [addendum](../../briefs/brief-TechFest-2026-10-23/addendum.md) and [validation](../../briefs/brief-TechFest-2026-10-23/validation.md) remain the upstream planning record. All 11 original documents and the problem-statement image are preserved in that brief's `sources/`; their [manifest](../../briefs/brief-TechFest-2026-10-23/sources/manifest.json) records provenance. No reference command or preset was executed.

| Source input | Content preserved in PRD / downstream handoff |
| --- | --- |
| CY-02 problem image/transcription | Required categories, masked evidence, prompt, rescan and evaluation; FR-7/8 explicitly preserve browser-visible secrets and access-check candidates |
| Newer README | End-to-end workflow and time constraint; direct user overrides its ZIP-only, URL-stretch and repository-stretch clauses |
| Newer 01 | Initial ecosystem, two source scanners, public/private key distinction and honest limits |
| Newer 02 | Module separation retained as architecture input; evidence/status/compare/fallback requirements retained; sample API not treated as final |
| Newer 03 | Controlled vulnerable/corrected/clean cases, hostile-input tests, failure visibility and actual timings |
| Newer 04 | Three workspace phases, filters/evidence/copy, narrow layouts, focus, contrast, reduced motion and all error states |
| Older README | Untested reference status and proposed modular scope; Trivy P0 proposal remains optional assumption because packs conflict |
| Older 01 | ZAP baseline behavior, dependency DB caveats, representative samples and local smoke-test requirement |
| Older 02 | Source tree intake, project recognition, worker isolation and URL controls; rejected raw-evidence persistence proposal in favor of sanitized reports |
| Older 03 | Authorization, request bounds, malformed-output/offline cases, honest rescan and no submitted execution |
| Older 04 | Graphical interactions, masked copying and visual hierarchy; six screens can be three phases |
| Older 05 | Shared contract before parallel implementation, GitHub tracking and no competing agent framework/backlog |

Direct user additions require codebase, repository and URL input and OWASP ZAP for the URL. Embedded ZIP-only/optional-URL scope and URL-first cut rules are superseded. Public GitHub-only, passive-only and private/history exclusions remain tagged assumptions, not direct user instructions.

## Technical candidates for Winston

React/TypeScript, FastAPI, bounded workers, status polling, SQLite metadata and temporary storage are proposed in the source packs, not mandated here. Select one canonical API rather than combining their incompatible endpoint sketches.

Use normalized typed source/web evidence, stable finding identity, source commit or target observation, tool applicability and coverage. Comparison requires per-finding scope, rule/policy versions and confidence in matching; disappearing pages cannot clear website findings. Gitleaks/Semgrep and ZAP adapters must parse valid findings-bearing outcomes independently from process failure.

Browser-visible credential coverage needs a bounded asset detector in addition to ZAP if stock alerts cannot meet FR-8. All fetched assets inherit destination, byte and request limits. Do not execute the submitted application to obtain source findings. Any team-controlled vulnerable demo server is separately operated by the team; it is not launched from untrusted uploaded code.

Architecture exit conditions: finite validated input/repository/crawl/output/deadline budgets; restricted runtime available on demo machine; trusted rules and suppression policy; licensing/distribution checked; model/provider and sharing behavior; source/report expiry, cleanup and session access; no exposed ZAP API or host keys/socket. Their absence blocks implementation readiness, not writing UX.

## Visual depth for Sally

Preserve an original premium identity: cinema-black surfaces, restrained monochrome, striking entry typography, precise separators and controlled event-driven motion. Dense findings favor legible monospace and evidence over giant display type. This is inspiration from the source pack, not an installed Bugatti design system, copied brand asset or approved token set. Sally creates the actual `DESIGN.md` and `EXPERIENCE.md`, adapting contrast and focus to the evidence-heavy workspace. No marketing site, chat-first interface or fabricated analytics.

## Research and untested claims

Primary documentation was refreshed during PRD discovery:

- [ZAP baseline](https://www.zaproxy.org/docs/docker/baseline-scan/): spiders then passively analyzes; live requests; JSON reports; WARN/FAIL alert exits differ from execution failure.
- [Gitleaks](https://github.com/gitleaks/gitleaks): directory and history modes differ; target config/ignore mechanisms require a trusted policy; a redaction flag does not prove all outward fields safe.
- [Semgrep CE comparison](https://semgrep.dev/products/semgrep-vs-ce/): selected analysis limitations and existing remediation offerings constrain novelty and authorization-coverage claims.

No local scanner execution, benchmark, precision/recall, integration, redaction proof, network enforcement or model-quality result exists. The PRD's success criteria are test targets, not reported achievements.

## Final verification to perform after setup

Check problem statement → requirements → UX/architecture decisions → epics/stories → GitHub issues for omissions and contradictions. Confirm every required input and safety criterion has an owner and testable acceptance. Check repository README, agent instructions, environment example, setup commands, CI plan, dependency/rule versions and issue dependencies against the actual implementation plan. Confirm original references and generated artifacts are versioned without secrets or unnecessary runtime files.

This planning consistency check does not establish functional correctness. After implementation, repeat scanner, safety and full workflow acceptance tests on the demo machine with real evidence. GitHub setup will need the actual repository owner/name/visibility and available team identities; those are not guessed in the PRD.
