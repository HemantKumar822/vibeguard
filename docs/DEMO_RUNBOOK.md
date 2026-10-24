# Local operator runbook

**Quickest startup:** Run `./scripts/dev-start.ps1` (Vite dev server, hot-reload) or `./scripts/start-demo.ps1` (production build) in PowerShell 7 from the repository root. See [QUICKSTART.md](QUICKSTART.md) for Groq setup, flags, and the five-minute judge walkthrough.

The manual commands below document the original measured rehearsal with AI disabled. All five epics including Groq AI, scan activity, rescan comparison, and report export are now complete and live.

Use three PowerShell terminals in `D:\TechFest`. The measured environment is Node 24.19.0, Python 3.12.13 and Docker Desktop Linux engine 29.9.2. Scanner digests and versions are recorded in `contracts/scanner-readiness.json`; the acceptance JSON records the images actually requested. Submitted source is never installed, built or executed. AI stays off.

For a new checkout, install the locked dependencies once:

```powershell
uv sync --frozen
npm --prefix frontend ci
docker info --format '{{.ServerVersion}}'
```

Existing locked dependencies were used for this rehearsal; a fresh dependency installation was not repeated. If Docker reports WSL/engine unavailable, finish the official Docker Desktop/WSL setup and restart before continuing. A version probe alone is not scan acceptance.

In terminal 1, choose a fresh private runtime outside the checkout and OneDrive:

```powershell
$env:VIBEGUARD_RUNTIME_DIR = Join-Path $env:LOCALAPPDATA 'VibeGuard\demo-runtime'
$env:VIBEGUARD_ORIGIN = 'http://127.0.0.1:5173'
$env:VIBEGUARD_LOOPBACK_HTTP = '1'
$env:VIBEGUARD_AI_ENABLED = '0'
uv run uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

In terminal 2 set the same four environment variables, then start the trusted coordinator. The API alone cannot execute or clean up scanner jobs:

```powershell
uv run python -m workers.coordinator
```

In terminal 3:

```powershell
npm --prefix frontend run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173` and wait for API connected. A health response is only API availability. Website mode also requires the measured readiness proof. If it is invalid, diagnose the implementation/image drift and rerun the approved proof command in DEVELOPMENT.md; never bypass the gate.

## Rehearsed source loop

1. Choose mapped files and select `fixtures/acceptance/vulnerable.ts`. Enter `app/src/main.ts` as its original relative path, confirm permission and submit. This is visibly a synthetic scanner corpus. Directory selection is optional; mapped files are the fallback when folder APIs are unavailable.
2. Wait for actual complete tool states. On this machine Gitleaks and Semgrep completed and located four selected candidates at lines 1–4. The public browser key produced no credential occurrence.
3. Inspect location, confidence, impact, recommended change and verification. At 360px select a finding and use Back to findings to return focus. Choose severity info to exercise the empty state, then Clear filters.
4. Copy the sanitized repair prompt. The planted value was absent from the actual clipboard and rendered DOM. If clipboard access fails, select the read-only sanitized textarea and copy manually. Credential rotation remains a separate human action.
5. Choose Rescan corrected input. Select `corrected.ts`, map the same path and confirm permission again. Submit with Enter. The baseline stays visible; the new worker job must finish before comparison. The measured corrected source report had no findings. Unsafe-input/access-check candidates were not detected; credential/TLS comparisons remained unverified because of uncertain structural identifiers. Neither absence nor a clean report proves repair or rotation.
6. At 360px, select a comparison with Enter; focus moves to Paired evidence, and Back returns to the selected item. Evidence scrolls horizontally inside its own panel. At 1440px before/after panels sit beside each other.
7. Open Delete scan. Cancel receives initial focus; Escape cancels and preserves evidence. For disposable rehearsal input, confirm deletion and wait for the coordinator to finish cleanup. Save a baseline Scan ID before deleting its child; reconnect to that baseline in the same browser session to delete it separately. Lost cookies cannot restore ownership.

## Reproducible acceptance and live observation

```powershell
uv run python scripts/run_acceptance.py --live --output _bmad-output/implementation-artifacts/epic-5-acceptance.json
```

The runner creates a separate fresh private temporary runtime, uses actual API admission, trusted coordinator and pinned scanners, performs a corrected rescan in each controlled mode, reads the paired result and verifies source cleanup. It writes sanitized JSON and a Markdown table. Network retrieval/capture fixtures are clearly marked controlled; `--live` adds real acquisition from the existing public repository and website. Do not deploy new fixtures or scan other targets without authorization. Use `--modes website` for a website-only rerun.

Expect a nonzero result with the current selected website labels: extra passive alerts remain for review, and the live website observation has incomplete capture. Never replace these with a successful mode or inflate accuracy by deleting misses. Source/repository controls and completed scanner stages remain useful evidence despite the release gate.

## Recovery and release gate

- API unavailable: start the API with the exact browser Origin and private runtime, then reload. The initial unavailable state and recovery to connected were observed.
- Queued without progress: check that the separate coordinator and Docker are running. Reconnect with the same session and Scan ID; reconnect does not submit another job. Never repeatedly submit to simulate progress.
- `cleanup_pending`: let the trusted coordinator retry cleanup before new intake. Do not manually change tombstones or disable the intake fence.
- Partial coverage: inspect actual tool status and exclusions. Same-origin omissions and unsupported checks remain explicit; no absence/security conclusion follows.
- Permission/session denied or expired: restore the authorized session if available or deliberately start a new submission. Do not use another user's scan ID or bypass CSRF.
- AI outage: deterministic guidance remains available; no paid provider is required. Failed deletion remains visible and must be retried by the coordinator.

Observed automated evidence covers adversarial intake/network/session/CSRF/retry/deletion/crash/model fallback and clipboard denial. Browser evidence covers the source repair/rescan loop, empty filters, mapped-file fallback, keyboard selection, deletion cancellation and two viewport sizes. Full rendered repository/website recovery journeys, every denial/expiry state, 200% zoom, reduced-motion emulation, assistive-technology announcements and complete contrast audit remain pending. The available browser exposes viewport controls but no zoom or motion-emulation capability; a zoom shortcut did not change the measured scale. Do not claim a full accessibility pass.

Public labeled vulnerable/corrected deployments and teammate prompt usefulness judgments are also pending. Keep Epic 5 open until these release gates and teammate review are resolved. Stop the three local processes with Ctrl+C after confirming test-source cleanup; never delete an unrelated runtime directory.
