# BMAD Input Handoff — Reference Material Only

These files are **research and engineering input**, not generated BMAD artifacts. The team will operate BMAD itself. Do not treat suggested module boundaries as already implemented or validated.

## Reading order
1. `01_RESEARCH_AND_SCOPE.md` — problem, ecosystem and tool choices.
2. `02_PRODUCT_AND_ARCHITECTURE.md` — product behavior, modules and contracts.
3. `03_VALIDATION_AND_THREATS.md` — tests, safety and evidence standard.
4. `04_UX_AND_DESIGN_REQUIREMENTS.md` — interaction requirements, complemented by team's `DESIGN.md`.

## Inputs BMAD should preserve
- 24-hour, multi-developer hackathon: realistic scope, parallelizable modules and explicit integration seams.
- Strong graphical UI, not a chat-first product.
- Source code scan -> evidence-backed report -> AI repair prompt -> rescan comparison is the required end-to-end path.
- P0 tools: Gitleaks, Semgrep, Trivy. ZAP baseline is stretch-only with safe URL policies.
- No executing untrusted project code in the MVP; model never controls unrestricted shell.
- Scanner confidence is not proof; verify actual fixes where possible.
- User supplies `DESIGN.md` independently.

## What BMAD should produce later (by the user)
Use this reference material to decide final requirements, architecture, epics, story dependencies, issue ownership and acceptance criteria. Keep GitHub as the operational tracking source once stories are approved. This document does **not** create or run any BMAD workflow.

## BMAD official documentation checked on 2026-10-23
- https://docs.bmad-method.org/
- https://docs.bmad-method.org/reference/skills-and-agents/
- https://docs.bmad-method.org/existing-codebases/set-and-maintain-project-context/
- https://docs.bmad-method.org/start/install-bmad/

Note: Current docs describe v7 preview alpha and v6.12 stable; the team should deliberately choose its installed version rather than mixing commands.
