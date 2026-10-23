# Validation Checklist and Risk Register
Status: Acceptance conditions proposed; NOT yet executed.

## Smoke tests before committing
- [ ] Gitleaks detects a **fake** deliberately planted key and its visible output is redacted.
- [ ] Gitleaks does not automatically classify a known public frontend key as a private credential.
- [ ] Semgrep detects at least one seeded risky JS/TS pattern, with correct path and line.
- [ ] Trivy reports a seeded dependency vulnerability from a valid lockfile and records its database/version.
- [ ] All tools produce machine-readable output and have observed runtime and exit-code handling.
- [ ] Running without internet or scanner database availability produces an explicit incomplete result, not a clean bill of health.
- [ ] Scanner timeouts, malformed JSON and missing tools are accurately represented.
- [ ] ZIP `../` paths, symlinks, zip bombs, excessive sizes and excessive file counts are rejected.
- [ ] Upload files cannot execute postinstall scripts or arbitrary code on the host.
- [ ] Findings referencing secrets are masked before user display and AI prompts.
- [ ] Rescan after correcting a finding marks it as absent-on-rescan; it only says verified-fixed when an appropriate repeatable test exists.
- [ ] A changed or failed rule pack cannot misleadingly mark an old finding fixed.
- [ ] AI is instructed to use only provided evidence and does not invent files or lines.
- [ ] Demo works with a clean project and with a project containing planted issues.

## URL module: mandatory additional gates
- [ ] Explicit permission for target scanning.
- [ ] Only public, permitted destination addresses; check redirects and actual connection destinations.
- [ ] Restrict crawl rate, host scope, total requests and time.
- [ ] Do not expose the ZAP API port to untrusted systems.
- [ ] Run baseline/passive mode, never full active scan for this prototype.
- [ ] Treat crawling as live HTTP traffic, even when the vulnerability checks are passive.

## Main risks
| Risk | Impact | Mitigation |
| --- | --- | --- |
| False positives | Users distrust report | Label confidence; cite file/line; suppress only with reason |
| Undetected authorization issues | False security confidence | Explicit scope and unknown areas; avoid blanket secure claims |
| Dependency DB offline | Trivy incomplete | Pre-cache database; report missing coverage |
| Scanner hangs | Demo breaks | Timeouts, independent tasks, partial results |
| Malicious upload | Infrastructure compromise | Strict archive validation; non-root isolated runners; no user-code execution |
| Secret leakage to LLM | Privacy/security incident | Redaction before model calls and logs |
| URL misuse/SSRF | Scanner accesses internal systems | Default disabled; enforce egress rules and authorization |
| Unverified rescan | Misleading success | Distinguish absent-on-rescan and verified-fixed |

## Explicit non-goals
Complete penetration testing; automatic exploitation; unrestricted shell agents; fixing the actual repository without consent; guaranteed security certification; cloud-scale multi-tenant hardening in 24 hours.

## Go/no-go decision
**GO for a constrained offline-first prototype**, subject to successful local smoke tests. **NO-GO for arbitrary-user URL scanning or running uploaded projects** until hard isolation and authorization requirements are independently satisfied.


## Acceptance demonstration
1. Upload an intentionally vulnerable, locally controlled fixture.
2. Produce true scanner findings with masked evidence and distinguish unverified warnings.
3. Generate a repair prompt based on these exact findings, without leaking credentials.
4. Update fixture in a second submission and rescan with the same scanners/rules.
5. Show resolved/remaining/new/unverified clearly; if a scanner failed, do **not** call its findings fixed.
6. Repeat with a clean fixture; show 'no findings detected within completed checks', not 'fully secure'.

## Explicit exclusions for prototype
Do not run user-submitted apps, package installs, arbitrary shell commands, browser-based exploitation or active penetration tests. Do not send unmasked keys to models. Public URL scanning remains optional and authorization-gated.
