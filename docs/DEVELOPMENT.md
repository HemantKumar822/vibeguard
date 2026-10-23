# Development setup

Story 1.1 provides the application foundation and shared data shapes. It does not implement intake, sessions, scanning, persistence or comparison algorithms.

## Install from a clean checkout

Prerequisites: Node 24.19.x or newer Node 24 LTS, npm, uv and Python 3.12.13. uv can install the Python version from `.python-version`. The lockfiles are committed.

From the repository root:

```sh
uv sync --frozen
npm --prefix frontend ci
uv run python scripts/export_contracts.py
npm --prefix frontend run generate:types
```

Two terminals, both starting in the repository root:

```sh
uv run uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

```sh
npm --prefix frontend run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to loopback port 8000, keeping browser requests same-origin. The actual health endpoint is `GET /api/v1/health`. Its response proves API availability only. Health is the only implemented application endpoint; the session requirement will apply to future user-data endpoints. Do not expose the development server or API to the public network.

The page clearly states scanning is unavailable. A development-only selector shows synthetic contract fixtures. Its dynamic import is eliminated in production; the built application contains no fixture payloads. Production serving/session integration belongs to subsequent stories.

## Shared contract workflow

1. Change backend models in `backend/core/contracts.py` deliberately against the [API contract](../_bmad-output/planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md).
2. Update relevant `fixtures/contracts/*.json`. They are labeled examples with no real secrets or scanner results.
3. Run `uv run python scripts/export_contracts.py`, then `npm --prefix frontend run generate:types`.
4. Run all checks below and commit models, OpenAPI, generated TypeScript and fixtures together.

`contracts/openapi.json` exports the live health route and shared component schemas. Unimplemented feature routes are deliberately absent. `Intake` describes repository/website JSON; `CodebaseMetadata` describes multipart metadata. These shapes do not perform network, multipart or scanner enforcement. Their owning stories add actual boundary validation and APIs. Typed fixture declarations are generated from the same JSON examples and checked against generated TypeScript.

## Verification

```sh
uv run pytest -q
uv run python scripts/export_contracts.py
npm --prefix frontend run generate:types
npm --prefix frontend run typecheck
npm --prefix frontend run build
npm --prefix frontend run lint
uv run python scripts/validate_repo_preparation.py
```

The Python suite checks live HTTP health, absent scan routes, all eight fixture states, invalid input/location/status cases, truthful completion and checked-in schema parity. Frontend compilation checks fixture payloads against generated types. No scanner acceptance or containment is established by these tests.

## Scanner feasibility gate

Use a Linux container runtime. On Windows this can be Docker Desktop with WSL2; install/first-launch and any Windows restart must finish before the engine can be tested.

```sh
uv run python scripts/scanner_readiness.py --output contracts/scanner-readiness.json
```

Exit 1 means tools are unavailable or unverified. Do not relabel it as passing. With a working engine, the command pulls exact candidate tags, resolves immutable image digests, executes version checks by digest with restricted flags, and records observed versions. It never scans submitted content. Version probes do not establish the future workers' filesystem/network safety. Use verified digests, not candidate tags, when implementing real workers. If a pinned image is unavailable, record and validate a deliberate replacement rather than silently floating.

Keep real source, reports and SQLite files outside the checkout and OneDrive, as required by the architecture. `.env.example` lists reserved future settings; the health-only bootstrap does not yet load them. Never put real credentials in examples.

## Compatible bootstrap versions

Observed: Node 24.19.0, Python 3.12.13, FastAPI 0.161.0, Vite 8.3.5, React 19.3.1, TypeScript 5.9.3, openapi-typescript 7.13.0 and create-vite 9.3.1 (`react-ts`). Exact transitive versions are owned by `uv.lock` and `frontend/package-lock.json`.

The planning candidates Node 24.22.1 / TypeScript 7.0.2 were not used unchanged. Node 24.19.0 is the installed compatible Node 24 runtime. TypeScript 7.0.2 exposes no `ts.factory` at its main entrypoint, while openapi-typescript 7.13.0 requires the TypeScript 5 compiler API. The observed failure was `Cannot read properties of undefined (reading 'createKeywordTypeNode')`; pinning its supported TypeScript 5.9.3 resolves generation and build. Do not upgrade the compiler independently of the generator.

On Windows, stop Vite before running `npm ci`; otherwise a loaded native module can cause an EPERM unlink error. The readiness command accepts `--pull-timeout 30` for a shorter bounded retry (default 180 seconds per image). A timeout is a blocked result, not proof an image or version is invalid.
