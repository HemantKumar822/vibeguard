# Architecture

## Execution flow

```text
Browser / React
  -> same-origin /api proxy
FastAPI
  -> session + CSRF + authorization + bounded intake
  -> SQLite-backed scan lifecycle and owned reports
Trusted coordinator
  -> retrieves/captures authorized input within policy
  -> starts immutable, restricted Docker scanner containers
  -> validates and sanitizes tool observations
  -> publishes typed findings + coverage + repair guidance
Browser
  -> polls actual status, investigates evidence, exports report
  -> submits corrected input as a separate owned rescan
```

The API handles admission and ownership; it does not start Docker containers. The host coordinator is the trusted process with Docker CLI access. Submitted applications are never installed, built or executed.

## Ownership of code

| Location | Responsibility |
| --- | --- |
| `backend/api/` | Public routes, session handling, input admission and owned report access |
| `backend/core/` | Typed contracts, safety policy, lifecycle state, cleanup, repair and comparison rules |
| `backend/adapters/` | Bounded storage, source/repository/website input, scanner normalization and optional AI transport |
| `backend/evaluation/` | Acceptance metrics derived from labeled observations |
| `workers/` | Persistent queue coordination, leases, isolated launchers and source/website jobs |
| `frontend/src/app/` | Shell, connection status and shared styles |
| `frontend/src/features/` | Intake, scanner activity, report investigation/export and rescan comparison |
| `frontend/src/shared/api/` | Generated backend-owned API types; do not hand-edit |
| `frontend/src/test/` | Test-only synthetic fixtures and compile-time contract checks |

## Scanning modes

Source and public-repository modes run trusted Gitleaks and Semgrep rules against bounded source snapshots. Repository identity includes the actual resolved commit. Git history, private repositories, hooks and application builds are outside scope.

Website mode captures bounded exact-origin public GET responses on the host. The transport validates public DNS results, pins the actual destination and enforces redirect/size/request/time limits. Captured HAR responses are imported into an offline ZAP container; ZAP does not independently spider or attack the target. Captured text assets are checked for credential candidates. Browser JavaScript, authenticated pages and private backend source are outside scope.

Scanner containers use pinned image digests, no network, non-root identity, a read-only root/source and bounded temporary storage, CPU, memory and PIDs. Raw source and scanner bytes remain inside the bounded private processing path. Only sanitized typed observations are published.

## Reports, AI and rescans

A completed tool is distinct from complete coverage. Partial, skipped, failed and timed-out checks remain explicit. Live activity comes from recorded backend states and timestamps; the UI does not invent per-rule execution events.

Deterministic repair guidance is always the baseline. Per-scan opt-in allows a bounded provider call with sanitized existing finding metadata; exact identity/location/grounding validation protects the report. Provider failure preserves template guidance and human actions.

A rescan is a new scan linked to an owned baseline. Classification depends on compatible rule/policy/input/tool coverage; unknown or incompatible observations remain unverified. Neither absence nor a successful scan proves security or credential rotation.

## Contracts and operator evidence

`backend/core/contracts.py` owns public schemas. `scripts/contracts/export.py` exports OpenAPI and typed test fixtures; npm generates public TypeScript types. Both outputs are checked for drift.

`contracts/scanner-readiness.json` records immutable scanner identities. `contracts/website-readiness.json` is bound to hashes of security-critical implementation files and pinned images. Routine folder cleanup must not rewrite or manufacture a passing proof. See [SECURITY](../SECURITY.md) for non-negotiable boundaries.
