# AI-Built Website Security Reviewer — Research and Decisions
Date: 23 October 2026 | Status: Proposed architecture; tools not yet smoke-tested

## Problem, from first principles
A website can work visually and still expose credentials, trust user input incorrectly, use vulnerable dependencies, or expose unsafe configuration. Builders who rely on AI may not know where to check or how to validate repairs. The product should translate repeatable checks into evidence-backed, understandable repair instructions, followed by another scan.

## Assumed target ecosystem
Prioritize TypeScript/JavaScript source, React, Vite/Next.js/TanStack-based apps, Node API routes/functions, npm lockfiles, and Supabase configurations. Python support is opportunistic because Semgrep and Trivy support it. This is a coverage choice, **not** a proven market-share ranking; official builder documentation and general developer surveys cannot establish the percentage of all vibe-coded projects on each stack.

## Evaluated tools
| Tool | Job | Strength | Limitation | Decision |
| --- | --- | --- | --- | --- |
| Gitleaks | Detect potential secrets in files | Focused rules and structured output | False positives; not every key is private | MVP |
| Semgrep Community Edition | Detect risky source patterns | Source-level file/line evidence; extensible rules | Cannot prove all access-control or business-logic flaws | MVP |
| Trivy filesystem | Known vulnerable dependencies and optionally configuration | Reads lockfiles; broad language/package coverage | Database updates and lockfile availability affect results | MVP, dependency scanner enabled explicitly |
| OWASP ZAP baseline | Passive alerts from deployed site | HTTP-response evidence; non-active baseline | Crawling still makes requests; authorization/network policy needed | Optional phase 2 |

### Documentation-derived cautions
- Trivy filesystem scanning enables vulnerability and secret checks by default; configuration checks must be enabled. Restrict to vulnerability checks to avoid duplicating Gitleaks and avoid surprises.
- ZAP baseline spiders the site (default one minute) then runs passive checks. It is **not** equivalent to not contacting the target or verifying access-control vulnerabilities.
- ZAP baseline exit code 2 can mean warnings, not a broken scan; interpret its structured report and execution status separately.
- A clean static scan does not prove application security, especially for authorization or business logic.
- User-submitted URLs create server-side request forgery risk: reject internal and metadata destinations, validate resolved addresses at connection time, limit redirects and scope.

## Critical scope choice
**Ship source-project scanning, evidence, repair prompt, and rescan.** Consider passive URL scanning only after core acceptance tests pass. Do not execute uploaded package scripts, build steps, or arbitrary repository commands in the MVP.

## Remaining unknowns
- Exact installed versions, parser compatibility and output schemas.
- Reproducible scan speed on the hackathon machines.
- Available Trivy vulnerability database and first-run update time.
- Rule packs' real false-positive rate on representative AI-built samples.
- Whether deployed URL scan authorization and egress controls can be implemented safely in time.

## Primary sources
- OWASP secure code review: https://owasp.github.io/DevSecOpsGuideline/2-Process/2-2-Develop/2-2-3-Secure-Code-Review/
- OWASP SSRF prevention: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- Semgrep: https://github.com/semgrep/semgrep
- Trivy filesystem: https://trivy.dev/docs/dev/target/filesystem/
- ZAP baseline: https://www.zaproxy.org/docs/docker/baseline-scan/
- ZAP Docker overview: https://www.zaproxy.org/docs/docker/
- Gitleaks upstream: https://github.com/gitleaks/gitleaks

## Decisions for BMAD to challenge, not blindly assume
- Source ZIP first, optionally repository import later. No running user projects in MVP.
- AI is an *explainer*, not the authority for what was detected.
- Each tool adapter must distinguish clean, findings, partial, failed and skipped.
- DESIGN.md will be supplied separately by the team; do not infer its visual identity.
- Validate tool behavior with actual fixtures before describing integrations as production-ready.

## Real-world sample research to collect
Use 3–5 public, permission-appropriate sample apps: a Vite/React client, a Next.js full-stack app, a Supabase-backed app and a clean control. For each, record framework, package manager, server-side code, deployment assumptions, lockfiles, scanner results, runtime and false alarms. Do not equate scanner warnings with proven vulnerabilities.

## Official background reading
- Lovable docs: https://docs.lovable.dev/
- v0 docs: https://v0.app/docs
- OWASP Top 10: https://owasp.org/Top10/
- Stack Overflow developer survey: https://survey.stackoverflow.co/2026/
