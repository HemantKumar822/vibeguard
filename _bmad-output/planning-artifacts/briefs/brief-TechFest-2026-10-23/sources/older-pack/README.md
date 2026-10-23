# Security Reviewer — Research Reference Pack

Prepared for a 24-hour multi-developer hackathon, 23 October 2026. These are **input documents for your own BMAD workflow**, not BMAD-generated plans or tickets.

| Document | Purpose |
|---|---|
| [01 Research & Scope](01_RESEARCH_AND_SCOPE.md) | Evidence, target ecosystem, scanner decisions |
| [02 Product & Architecture](02_PRODUCT_AND_ARCHITECTURE.md) | User journey, modular architecture, contracts |
| [03 Validation & Threats](03_VALIDATION_AND_THREATS.md) | Acceptance tests, security boundaries, risks |
| [04 UX Requirements](04_UX_AND_DESIGN_REQUIREMENTS.md) | Graphical screen and interaction requirements; style comes from your `DESIGN.md` |
| [05 BMAD Handoff](05_BMAD_HANDOFF.md) | Concise context and references for your BMAD process |

**Status:** Research-backed proposal, not tested integration. No scanner benchmark, repo setup, BMAD execution or GitHub issue creation has been performed.

**Scope:** Upload source -> inspect with Gitleaks/Semgrep/Trivy -> explain evidence -> repair prompt -> rescan and compare. Optional passive URL inspection only with sufficient safety protections.
