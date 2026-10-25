# VibeGuard

A security review workspace for AI-built code and websites. Submit authorized input, follow real scanner activity, inspect masked evidence, copy repair guidance, and compare a corrected rescan.

| Input | Checks | Evidence |
| --- | --- | --- |
| Codebase | Gitleaks + Semgrep | Source path, line, rule and masked evidence |
| Public GitHub repository | Same source checks on one resolved commit | Repository revision and source evidence |
| Website URL | Passive OWASP ZAP + captured-asset credential checks | Observed URL, response/header or asset location |

Findings are candidates for review. Completed checks and missing findings do not certify security. Exposed credentials require separate revocation or rotation.

## Run

Requires Python 3.12 via uv, Node 24 LTS, npm and Docker Desktop's Linux engine. Run from the repository root:

```powershell
./scripts/dev/start-demo.ps1
```

Open http://127.0.0.1:5173. Keep the terminal open; Ctrl+C stops the processes started by the launcher. For development with hot reload, use `./scripts/dev/dev-start.ps1`; Git Bash users can run `bash ./scripts/dev/start.sh`.

The launcher creates an ignored `.env` if needed. Optional Groq configuration and first-run scanner setup are in [QUICKSTART](docs/QUICKSTART.md). Production screens use real API results; synthetic fixtures are test inputs only.

## Repository

```text
backend/                 Python application
  api/                   HTTP routes and browser sessions
  core/                  Contracts, policy, lifecycle, repair and comparison
  adapters/              Storage, input/network/scanner and AI boundaries
  evaluation/            Acceptance metrics
workers/                 Trusted coordinator and isolated scanner execution
frontend/
  src/app/               Application shell and shared styles
  src/features/          Intake, scan activity, reports and comparison
  src/shared/api/        Generated public API types
  src/test/              Generated test fixtures and contract type checks
contracts/               OpenAPI and measured scanner-readiness evidence
rules/                   Trusted scanner configuration and its license
fixtures/                Synthetic contract and acceptance inputs
scripts/
  dev/                   Local startup commands
  checks/                Demo, website readiness and acceptance checks
  contracts/             Schema and test-fixture generation
  scanner_readiness.py   Shared Docker discovery and scanner version probe
tests/                  Backend checks grouped by subsystem
```

Frontend tests live beside the features they check. Runtime source, SQLite, logs and reports belong outside the checkout and OneDrive. Agent skills remain machine-local.

## Five core documents

- [README](README.md): product and entry point.
- [QUICKSTART](docs/QUICKSTART.md): configuration and judge walkthrough.
- [ARCHITECTURE](docs/ARCHITECTURE.md): component boundaries and data flow.
- [DEVELOPMENT](docs/DEVELOPMENT.md): contribution, generation and verification commands.
- [SECURITY](SECURITY.md): authorization, isolation, redaction and reporting rules.

Historical research, stories and verification records were archived outside the working repository before consolidation. GitHub issues and milestones remain the team delivery tracker. No application license is implied; the locally authored scanner rules have their own license in `rules/`.
