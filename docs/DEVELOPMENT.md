# Development setup

Stories 1.1–1.2 provide the application foundation, shared contracts, sessions, bounded source intake and private job lifecycle. Scanning and comparison algorithms are unavailable.

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

Open `http://127.0.0.1:5173`. Vite proxies `/api` to loopback port 8000, keeping browser requests same-origin. The actual health endpoint is `GET /api/v1/health`. Its response proves API availability only. Session, capabilities, source admission and owned-read routes are implemented; see the runtime configuration below. Do not expose the development server or API to the public network.

The page displays actual coordinator/tool state and unavailable adapter coverage. Development fixtures are synthetic contract examples. Its dynamic import is eliminated in production; the built application contains no fixture payloads. Production serving/session integration belongs to subsequent stories.

## Shared contract workflow

1. Change backend models in `backend/core/contracts.py` deliberately against the [API contract](../_bmad-output/planning-artifacts/architecture/architecture-TechFest-2026-10-23/API-CONTRACT.md).
2. Update relevant `fixtures/contracts/*.json`. They are labeled examples with no real secrets or scanner results.
3. Run `uv run python scripts/export_contracts.py`, then `npm --prefix frontend run generate:types`.
4. Run all checks below and commit models, OpenAPI, generated TypeScript and fixtures together.

`contracts/openapi.json` exports the live routes and shared component schemas. Owned polling and deletion-operation routes are included. `Intake` describes repository/website JSON; `CodebaseMetadata` describes multipart metadata. The bounded source adapter enforces multipart intake; scanner/network enforcement belongs to later stories. Typed fixture declarations are generated from the same JSON examples and checked against generated TypeScript.

## Verification

```sh
uv run pytest -q
uv run python scripts/export_contracts.py
npm --prefix frontend run generate:types
npm --prefix frontend run check:contracts
npm --prefix frontend test
npm --prefix frontend run typecheck
npm --prefix frontend run build
npm --prefix frontend run lint
uv run python scripts/validate_repo_preparation.py
```

The Python suite checks live HTTP health, authorized intake routes, all ten fixture states, invalid input/location/status cases, truthful completion and checked-in schema parity. Frontend compilation checks fixture payloads against generated types. No scanner acceptance or containment is established by these tests.

## Scanner feasibility gate

Use a Linux container runtime. On Windows this can be Docker Desktop with WSL2; install/first-launch and any Windows restart must finish before the engine can be tested.

```sh
uv run python scripts/scanner_readiness.py --output contracts/scanner-readiness.json
```

Exit 1 means tools are unavailable or unverified. Do not relabel it as passing. With a working engine, the command inspects cached pinned images first, pulls exact candidate tags only for missing images, resolves immutable image digests, executes version checks by digest with restricted flags, and records observed versions. It never scans submitted content. Version probes do not establish the future workers' filesystem/network safety. Use verified digests, not candidate tags, when implementing real workers. If a pinned image is unavailable, record and validate a deliberate replacement rather than silently floating.

Keep real source, reports and SQLite files outside the checkout and OneDrive, as required by the architecture. `.env.example` lists reserved future settings; the runtime settings above are required for intake. Never put real credentials in examples.

## Compatible bootstrap versions

Observed: Node 24.19.0, Python 3.12.13, FastAPI 0.161.0, Vite 8.3.5, React 19.3.1, TypeScript 5.9.3, openapi-typescript 7.13.0 and create-vite 9.3.1 (`react-ts`). Exact transitive versions are owned by `uv.lock` and `frontend/package-lock.json`.

The planning candidates Node 24.22.1 / TypeScript 7.0.2 were not used unchanged. Node 24.19.0 is the installed compatible Node 24 runtime. TypeScript 7.0.2 exposes no `ts.factory` at its main entrypoint, while openapi-typescript 7.13.0 requires the TypeScript 5 compiler API. The observed failure was `Cannot read properties of undefined (reading 'createKeywordTypeNode')`; pinning its supported TypeScript 5.9.3 resolves generation and build. Do not upgrade the compiler independently of the generator.

On Windows, stop Vite before running `npm ci`; otherwise a loaded native module can cause an EPERM unlink error. The readiness command accepts `--pull-timeout 30` for a shorter bounded retry (default 180 seconds per image). A timeout is a blocked result, not proof an image or version is invalid.

Verified on 2026-10-24: Linux Docker engine 29.9.2 executes Gitleaks 8.30.1, Semgrep 1.182.1 and ZAP 2.17.0 by the digests recorded in `contracts/scanner-readiness.json`. Probes remain non-root, network-disabled and read-only, with a 256 MiB temporary filesystem. HOME and Java user.home point into that scratch; the probe hostname resolves only to loopback. Semgrep version-check and metrics activity are disabled. Startup resource errors prevent a passing probe even if version text appears. These probes do not establish application scanner containment.

Pre-merge review added strict TypeScript null checking, generated-file drift checks, a production fixture-exclusion gate built into `npm run build`, and in-memory frontend health tests. Health requests have a 10-second deadline. Synthetic comparison examples link actual baseline/corrected/partial Scan fixtures. Probe containers are uniquely named and forcibly removed in a finally block, including timeout/error paths.

## Story 1.2 authorized source intake

Configure private runtime storage **outside this checkout and OneDrive** before starting the API. The API rejects relative paths, checkout paths, OneDrive paths, symlinks/junctions, and HTTP origins without an explicit loopback development profile. Windows creates an owner-only inheritable ACL; POSIX uses owner-only directory permissions. SQLite stores sessions, submission choices, idempotency identity and queued scans. Source bodies use private opaque part IDs plus a validated relative-path manifest.

PowerShell example (choose your own external private directory):

```powershell
$env:VIBEGUARD_RUNTIME_DIR = Join-Path $env:LOCALAPPDATA 'VibeGuard\runtime'
$env:VIBEGUARD_ORIGIN = 'http://127.0.0.1:5173'
$env:VIBEGUARD_LOOPBACK_HTTP = '1'
uv run uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

The Origin must match the browser address exactly. HTTPS deployments omit the loopback exception. Without configured runtime storage, health remains available and data endpoints return a safe 503. Session creation requires the configured Origin; submissions additionally require the session cookie, CSRF token and Idempotency-Key. Cookie loss makes owned scans unavailable.

Directory selection preserves browser-provided relative paths. If unavailable or paths are lost, select files and explicitly map one original relative path per file. Permission is mandatory and external sharing defaults off. Repository/website intake and external AI remain unavailable. No uploaded code, hooks, dependencies, build or scanner configuration is executed. Accepted scans remain queued, with `accepted_files` separate from empty inspected coverage; exclusions carry explicit reasons. No scanner has run, and there is no fabricated progress.

Verified commands: backend pytest, contract export/generation and parity, frontend tests/build/lint. Tests exercise real 25 MiB/5,000-file/2 MiB/depth-20/240-byte boundaries plus one, chunked bodies, interrupted uploads, unsafe paths, ownership, CSRF and failed-upload cleanup. Tests require OS access to private temporary directories outside the checkout; a restricted sandbox may require permission for that test run. The multipart parser is locked to python-multipart 0.0.22. Orchestration, deletion and lifecycle recovery belong to story 1.3.


## Story 1.3 private bounded lifecycle

Run the coordinator in a **separate host terminal**, using the same private runtime settings as the API:

```powershell
uv run python -m workers.coordinator
```

Only this trusted host process controls Docker. API and worker containers must receive neither a Docker socket nor host credentials. Source workers use the verified immutable digests, fixed version-only diagnostic commands, read-only root/source, non-root identity, no network, dropped capabilities, no-new-privileges, 2 CPUs, 2 GiB memory, 128 processes, 256 MiB scratch, a 90-second tool deadline and 5 MiB output ceiling. Raw diagnostic output is discarded. Version checks are diagnostics, never completed scan coverage.

The persisted SQLite WAL queue accepts three waiting jobs and one running job. Claims and session-scoped canonical idempotency are transactional. Queue/global deadlines are 600/300 seconds. A single coordinator renews a 15-second lease; takeover marks abandoned work failed and cleans it before claiming again. Jobs are never automatically rerun. Before story 1.4 provides reviewed adapters/rules, dispatch produces explicit `trusted_adapters_unavailable` failure, zero completed coverage and deterministic manual-review guidance.

Owned GET polling exposes actual Scan/tool states. DELETE returns a durable deletion operation: access is tombstoned immediately, late writes are refused, and `/api/v1/deletions/{operation_id}` reports pending/complete/failed cleanup. Cancellation and source removal must succeed before completion. Failures remain visible and block admission; coordinator sweeps retry them. Without a coordinator, deletion remains pending and becomes failed at the next sweep after 60 seconds. Retention is 24 hours from terminal completion and 24 hours of session inactivity. Reads refuse expired resources immediately; startup and minute sweeps enqueue expiry cleanup. Orphan upload directories receive a 600-second grace before purge. Runtime cleanup errors block admission.

Physical verification (2026-10-24, Linux Docker 29.9.2):

```powershell
$env:VIBEGUARD_DOCKER_TESTS = '1'
uv run pytest tests/test_worker_isolation.py -q
```

Four tests passed, including real read-only writes, denied external network/socket access, non-root/capability/no-new-privileges checks, observed cgroup and scratch limits, output overflow, timeout and daemon-side removal. These tests are opt-in when Docker is unavailable. This establishes the tested source-worker containment profile, not scanning correctness or website egress safety. Full scanning remains unavailable until trusted adapters/rules are installed in story 1.4.
