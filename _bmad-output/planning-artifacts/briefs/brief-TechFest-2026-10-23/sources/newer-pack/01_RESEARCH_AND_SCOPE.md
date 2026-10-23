# 01 — Research, Problem and Scope

## The problem from first principles
AI coding assistants can produce websites that look finished while still containing exposed credentials, unsafe code patterns or weak access controls. A non-security specialist needs a way to locate **plausible risks with evidence**, understand them, change the code and rerun checks. The product should not claim every warning is exploitable or every undiscovered issue is absent.

## What we are targeting first

| Area | MVP support | Why |
| --- | --- | --- |
| Language | **JavaScript/TypeScript** | Practical starting point for modern AI-generated web apps |
| Frontend | React, Vite, Next.js source patterns | Useful coverage of builder-style projects |
| Backend | Node / Next.js route files if present | Detect risk patterns in uploaded server code |
| Secrets | Common API keys and credential patterns | Strong demonstration with exact source evidence |
| Data services | Relevant Supabase key patterns | Frequent source of public-versus-privileged key confusion |
| Input | **Source ZIP only** | Avoid live-network and repository-permission complexity |

These are **engineering priorities, not measured market share** of every AI-builder project. Builder documentation and general developer surveys are not conclusive market-share evidence.

## Why only two security scanners?

| Tool | What it actually checks | Limits |
| --- | --- | --- |
| **Gitleaks**, directory/file mode | Potential passwords, tokens, private keys and credential strings in submitted files | May flag test/public keys; does **not** scan history missing from a ZIP |
| **Semgrep Community Edition** | Known suspicious code patterns; reports rule, file and line | Does **not** prove every access-control issue or trace arbitrary business logic |

Our advantage is **usable evidence → repair → rescan**, not writing new parsers or claiming universal detection. Normalize scanner findings into one UI experience. Scanner findings and AI explanations are **candidates for review**, not vulnerability certificates.

### Important security distinctions

- **Public ≠ private key:** Supabase publishable/legacy anonymous keys can be intentionally public. Supabase `sb_secret_` and privileged `service_role` keys must remain server-side. Check context before assigning severity.
- **Missing visible authentication ≠ proven bypass:** Middleware or infrastructure may check authorization elsewhere. Do not mark absence of a local call as confirmed exploitability.
- **Source ZIP ≠ deployed website:** It cannot prove what was included in live bundles or whether a deployed database policy is safe. State this limitation clearly.
- **Secret removed ≠ secret rotated:** If a real private credential was exposed, recommend revocation/rotation as a **human action**.
- **Disappeared rule hit ≠ verified repair:** Rescan comparison shows what was detected again, with status for missing coverage.

## What we retained from teammates' research
From the CY-02 blueprint and ARGON specification: strong pre-model secret masking, evidence with exact file/line, false-positive controls, one copyable repair prompt, rotation guidance, and honest rescan differences. These improvements **fit the core scope**. We explicitly deferred their browser crawlers, role testing, multi-agent loops, MCP, attack-chain synthesis and package-existence engine.

Two corrections are important if stretch features are ever revisited: **keep dependency lockfiles** (do not delete them during cleanup), and never assume a consent checkbox or a hostname suffix alone makes remote URL scanning safe.

## Stretch decision, made only after working MVP

If time genuinely remains, choose **one** small improvement based on observed gaps: (a) Trivy **or** OSV-Scanner lockfile vulnerability scan; (b) one or two tested custom Semgrep rules; or (c) authorized, restricted passive URL analysis. No parallel stretch investigations before core integration.

## Primary official references

- [Gitleaks upstream README](https://github.com/gitleaks/gitleaks)
- [Semgrep documentation](https://semgrep.dev/docs/)
- [OWASP Top 10](https://owasp.org/Top10/)
- [OWASP secure code review guidance](https://owasp.org/www-project-code-review-guide/)
- [Supabase API keys](https://supabase.com/docs/guides/api/api-keys)
- Optional only: [Trivy filesystem scanner](https://trivy.dev/docs/target/filesystem/), [OSV-Scanner](https://google.github.io/osv-scanner/), [ZAP baseline](https://www.zaproxy.org/docs/docker/baseline-scan/), [SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html).

**Research confidence:** Tool capabilities are supported by vendor documentation; integration performance, reliability and detection accuracy must be tested locally before making claims.
