# AI Security Reviewer — Final Hackathon Reference Pack

**Version:** MVP Freeze · 23 October 2026  
**Status:** Research-backed implementation proposal, not yet benchmarked or implemented.  
**Team:** Multiple developers, 24-hour hackathon.  
**Workflow:** The team will run **BMAD** itself. These are **reference inputs**, not BMAD commands, stories, or a second tracker.

## Product in one sentence
A **graphical security reviewer for AI-built websites** that scans uploaded source code, shows trustworthy evidence, generates a copyable repair prompt, and compares results after developers make changes.

### The only required user journey

`Upload ZIP → scan with Gitleaks + Semgrep → inspect findings → copy one AI repair prompt → upload corrected ZIP → see before/after comparison`

The result must be **real scanner output**, not sample warnings disguised as live analysis. The product does not certify that a website is safe.

## Frozen scope

| P0 — Build this | P1 — Only if P0 works end-to-end | Explicitly out of scope |
| --- | --- | --- |
| Safe source ZIP upload | One dependency scanner: Trivy **or** OSV-Scanner | Multi-agent frameworks / LangGraph |
| Restricted Gitleaks source scan | 1–2 validated custom Semgrep rules | MCP/editor automation; automatic code changes |
| Restricted Semgrep JS/TS scan | Authorized passive deployed-URL checks | Attack chains and multi-account penetration tests |
| Redacted file/line evidence, confidence and tool coverage | Git import and history scan | Slopsquatting engine, fabricated security scores |
| One AI explainer + consolidated repair prompt | Additional languages | Running uploaded application/build/install scripts |
| Re-upload + honest rescan comparison |  | Large dashboard/analytics platform |
| Polished graphical UI based on team's future `DESIGN.md` |  | Separate chat-first experience |

**Scope rule:** No P1 item starts until the P0 flow works with a vulnerable fixture **and** a clean control. If P0 slips, cut P1 entirely.

## Files and reading order

1. [`01_RESEARCH_AND_SCOPE.md`](01_RESEARCH_AND_SCOPE.md) — target ecosystem, tool choices, scope reasoning and sources.
2. [`02_PRODUCT_AND_ARCHITECTURE.md`](02_PRODUCT_AND_ARCHITECTURE.md) — user experience, modules, data flow, sample contracts.
3. [`03_VALIDATION_AND_SAFETY.md`](03_VALIDATION_AND_SAFETY.md) — acceptance criteria, safety constraints and 24-hour gates.
4. [`04_FRONTEND_UX.md`](04_FRONTEND_UX.md) — full graphical experience, screen behavior, state handling and Bugatti-inspired `DESIGN.md` handoff.

## BMAD handoff (you execute BMAD)

- Feed BMAD **this pack (including the standalone frontend UX document) plus your `DESIGN.md`** when ready. `DESIGN.md` is the visual style authority; these files describe required behavior.
- Have BMAD derive **epics, stories, issue dependencies and acceptance criteria**. We are deliberately **not** maintaining a competing backlog here.
- Use **GitHub Issues/Projects** for live assignments and progress. Maintain one owner per issue; PRs link issues.
- Freeze the common scanner-result and report JSON before independent frontend/backend work.
- Verify actual tool versions, command flags, rule configurations and execution times on the team's machines. None have been measured for this pack.

**This pack supersedes our earlier broader research plans for implementation scope.** The teammate CY-02 and ARGON documents remain useful background; their more ambitious features are not MVP requirements.
