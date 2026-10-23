# VibeGuard

Evidence-backed security review for AI-built websites: **submit → inspect → repair → rescan**.

Built for the CY-02 hackathon challenge. The application will accept a full codebase, a repository, or an authorized deployed website URL; explain candidate security findings; produce one repair prompt for the developer's coding tool; and compare a real repeat scan.

**Current status:** Source upload, owned jobs, isolated Gitleaks/Semgrep checks, masked findings and deterministic repair guidance are implemented. Public GitHub snapshots use the same pipeline and retain the requested ref and full resolved commit. Stories 1.2–2.2 are in review; neither Epic 1 nor Epic 2 is closed. Website/ZAP review, AI and rescans remain unimplemented. See the [batch verification record](_bmad-output/implementation-artifacts/source-repository-batch-verification.md) for observed checks and remaining UI review. The team repository is [HemantKumar822/vibeguard](https://github.com/HemantKumar822/vibeguard) (private).

**Run locally:** follow [development setup](docs/DEVELOPMENT.md) for installation, two-terminal startup, type generation and verification.

## What we are building

| Input | Planned checks | Evidence |
| --- | --- | --- |
| Codebase | Gitleaks + selected Semgrep rules | Relative file, actual line, rule and masked snippet |
| Repository | The same source checks on a recorded public GitHub commit | Repository, commit and source evidence |
| Website URL | OWASP ZAP baseline/passive review + bounded visible-asset credential checks | Observed URL/header/response/asset location and assessed scope |

The required journey is a graphical workspace, not a chatbot. Findings remain candidates for review; a missing warning does not certify safety. Potentially exposed private credentials require separate human revocation/rotation. URL review cannot reveal private backend source.

## Start here as a teammate

Use the [team delivery guide](docs/TEAM_DELIVERY.md) for the five milestones, their 16 stories and parallel-work guidance.

1. Read the [team story board](_bmad-output/github-issues/README.md) and coordinate a story with the team.
2. Read that story's description, dependencies, acceptance criteria and verification plan. Every story has its own file in [_bmad-output/implementation-artifacts/](_bmad-output/implementation-artifacts/README.md).
3. Follow [CONTRIBUTING.md](CONTRIBUTING.md) and the [project rules](docs/PROJECT_RULES.md). Claim one story before changing shared files.
4. Use [development setup](docs/DEVELOPMENT.md) for actual setup/build/test commands and locked dependencies. Start the API, trusted coordinator and frontend separately. Real source checks require the verified pinned Linux Docker images.

Python and Git can also run the preparation checks:

```bash
python scripts/validate_repo_preparation.py
```

This validates stories, dependency links, shared-file policy and documentation. It does not install or run the application. It uses a temporary Git directory to test ignore behavior, without initializing this project's repository.

## Shared documents

| Document | Purpose |
| --- | --- |
| [Product brief](_bmad-output/planning-artifacts/briefs/brief-TechFest-2026-10-23/brief.md) | Problem, users and scope |
| [PRD](_bmad-output/planning-artifacts/prds/prd-TechFest-2026-10-23/prd.md) | Numbered requirements and evaluation |
| [DESIGN.md](_bmad-output/planning-artifacts/ux-designs/ux-TechFest-2026-10-23/DESIGN.md) | Proposed visual tokens and component appearance |
| [EXPERIENCE.md](_bmad-output/planning-artifacts/ux-designs/ux-TechFest-2026-10-23/EXPERIENCE.md) | Interaction, state, accessibility and flows |
| [Architecture spine](_bmad-output/planning-artifacts/architecture/architecture-TechFest-2026-10-23/ARCHITECTURE-SPINE.md) | Boundaries, ownership and execution policy |
| [API contract](_bmad-output/planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md) | Shared frontend/backend boundary |
| [Safety profile](_bmad-output/planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md) | Finite limits, retention and release gates |
| [Epics and stories](_bmad-output/planning-artifacts/epics.md) | Canonical planning backlog |
| [Sprint tracker](_bmad-output/implementation-artifacts/sprint-status.yaml) | Implementation status; readiness is distinct from dependency eligibility |
| [Repository setup checklist](docs/REPOSITORY_SETUP.md) | Steps to perform later, before publishing |

## Repository shape

Present now: `frontend/` React/TypeScript workspace, `backend/` FastAPI/core/adapters, `workers/` trusted coordinator and restricted launchers, locally authored `rules/`, typed `contracts/`, synthetic `fixtures/`, tests, team documentation and `_bmad-output/` planning/implementation records. Local agent installations remain excluded by `.gitignore`.

Exact compatible dependencies are recorded in `uv.lock` and `frontend/package-lock.json`. Submitted code, SQLite, scanner output and runtime artifacts belong outside the checkout and OneDrive.

## Contribution and safety

Use a story branch and a focused pull request. Include tests, observed results and related issue/story IDs. Keep lockfiles, generated API types and deliberate schema changes consistent. Never commit credentials, submitted source, raw scanner outputs, scan databases or local tool installations.

Only assess code and sites you are authorized to review. Read [SECURITY.md](SECURITY.md) before reporting a sensitive issue. A permissions checkbox does not replace worker or network enforcement.

License, GitHub repository identity, maintainers and remote branch protections will be confirmed during publication setup. Until a license is selected, this workspace does not claim an open-source license. No application demo link or passing CI badge is advertised before one exists.
