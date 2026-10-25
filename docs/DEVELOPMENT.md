# Development

## Setup and commands

Use Python 3.12 via uv and Node 24 LTS. Run commands from the repository root unless specified.

```powershell
uv sync --frozen
npm --prefix frontend ci
./scripts/dev/dev-start.ps1
```

For the built judge demo and configuration, use [QUICKSTART](QUICKSTART.md). Startup scripts live in `scripts/dev/`; operator checks in `scripts/checks/`; schema tooling in `scripts/contracts/`. `scripts/scanner_readiness.py` is also imported by the trusted launcher, so treat it as runtime support, not disposable setup tooling.

Manual API/worker startup requires the same private `VIBEGUARD_RUNTIME_DIR`, origin and loopback settings in both terminals:

```powershell
uv run --env-file .env uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
uv run --env-file .env python -m workers.coordinator
npm --prefix frontend run dev
```

Keep the private runtime outside the repo and OneDrive. `.env`, keys, source uploads, scanner output, SQLite and local logs are never committed.

## Code organization

- `backend/api` handles HTTP and sessions, `core` owns contracts/state/policy, `adapters` owns external boundaries, and `workers` owns execution. Avoid moving business rules into HTTP routes or giving the API Docker control.
- Frontend code lives by feature under `frontend/src/features/{intake,scans,report,comparison}`. Keep feature tests beside their components. The application shell and styles live in `src/app`.
- Generated public types live in `src/shared/api/generated.ts`. Synthetic generated data lives in `src/test/fixtures.generated.ts` and must not enter production screens.
- Backend tests are grouped under `tests/{api,core,adapters,workers,contracts,evaluation,tooling}`. Synthetic inputs stay under `fixtures`; trusted scanner rules under `rules`.

## Contract changes

Change `backend/core/contracts.py`, then the corresponding JSON examples under `fixtures/contracts`. Regenerate both checked-in outputs:

```powershell
uv run python scripts/contracts/export.py
npm --prefix frontend run generate:types
npm --prefix frontend run check:contracts
```

Do not hand-edit generated files. Contract checking validates OpenAPI, public API types and typed synthetic fixtures against their sources.

## Focused verification

```powershell
npm --prefix frontend test
npm --prefix frontend run build
npm --prefix frontend run lint
uv run pytest tests/contracts tests/tooling -q
uv run pytest tests/adapters/test_explanations.py -q
uv run pytest --collect-only -q
```

Use checks for the changed boundary. A frontend/doc refactor does not require replaying the Docker acceptance corpus. Real scanner/isolation changes do:

```powershell
$env:VIBEGUARD_DOCKER_TESTS='1'
uv run pytest tests/workers/test_worker_isolation.py tests/workers/test_website.py -q
```

Full acceptance is an explicit operator run, not part of routine cleanup:

```powershell
uv run python scripts/checks/run_acceptance.py --output "$env:LOCALAPPDATA/VibeGuard/acceptance.json"
```

The runner writes sanitized evidence, uses real scanners and labels controlled synthetic inputs. Add `--live` only for existing targets you are authorized to assess. Store evidence outside the checkout rather than regenerating old planning documents.

For a startup-only check: `./scripts/dev/start-demo.ps1 -SmokeCheck`. For configuration diagnosis without a live model call: `uv run --env-file .env python scripts/checks/verify_demo.py --skip-groq`.

## Scanner readiness

The launcher never silently updates scanner digests or bypasses website readiness. Version probes do not establish worker containment:

```powershell
uv run python scripts/scanner_readiness.py --output contracts/scanner-readiness.json
uv run python scripts/checks/verify_website_readiness.py --help
```

Run the website measurement only with an authorized target and its required confirmation flag. A stale proof means URL admission stays unavailable until actual verification succeeds. Never edit a fingerprint to imply a measurement took place.

## Team delivery

Use GitHub issues/milestones as the live tracker. Claim a task, work on a branch, and keep shared contract/state changes coordinated. PRs explain the problem, resulting behavior, checks actually run and remaining limitations. Use `Closes #...` only when all issue requirements are delivered. Request teammate review before merge.

Preserve observable behavior during structural cleanup. Keep safety rules in [SECURITY](../SECURITY.md), package boundaries in [ARCHITECTURE](ARCHITECTURE.md), and startup instructions in [QUICKSTART](QUICKSTART.md). New functionality belongs in a focused change, not a folder reorganization.
