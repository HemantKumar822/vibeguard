# Quickstart

## Prerequisites and first run

Use PowerShell 7, uv, Python 3.12 (managed by uv), Node 24.19 or later Node 24 LTS, npm, and Docker Desktop running Linux containers. From the repository root:

```powershell
./scripts/dev/start-demo.ps1
```

This installs locked dependencies if missing, checks pinned scanner images, builds the frontend and starts the API, coordinator and frontend. Missing images produce a specific pull command; scanners never silently pull floating images while executing a job. Open http://127.0.0.1:5173. Ctrl+C stops only this launcher's process trees.

Private source and job state default to `%LOCALAPPDATA%/VibeGuard/demo-runtime`. Process logs are under `%LOCALAPPDATA%/VibeGuard/demo-logs`. Both stay outside the checkout and OneDrive. Do not run two coordinators against one runtime.

```powershell
./scripts/dev/start-demo.ps1 -SkipBuild   # Reuse an unchanged frontend build
./scripts/dev/start-demo.ps1 -SmokeCheck # Start, verify HTTP health, stop; no scans
./scripts/dev/dev-start.ps1             # Development with frontend hot reload
```

Git Bash: `bash ./scripts/dev/start.sh`. Docker-free development options start the interface/API only; they do not demonstrate successful real scans.

## Groq configuration

The launcher creates `.env` from `.env.example` if it is missing. Edit the local file:

```dotenv
VIBEGUARD_AI_ENABLED=1
VIBEGUARD_AI_PROVIDER=groq
VIBEGUARD_AI_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=your_valid_key
```

Restart after editing. API keys stay server-side. On a new submission, enable **Use AI explanations (optional)** to send bounded, sanitized finding metadata to Groq. The provider selects grounded guidance; it cannot run tools, invent findings or certify a repair. Reports and repair prompts still work when AI is off, times out or rejects the key. HTTP 401 means the provider rejected the credential; replace it locally, never paste it into an issue or chat.

## Judge walkthrough

1. Start the app and confirm API connected.
2. Select your own codebase, an authorized public repository or website. For a repeatable demonstration, explicitly label `fixtures/acceptance/vulnerable.ts` as a deliberately vulnerable sample, select that file and map it to `app/src/main.ts`. It is scanned by real tools, not a mocked response.
3. Confirm permission and optionally enable AI. Submit and show real waiting/running/completed check states and recorded event timestamps. Fast checks can finish between polls.
4. Inspect a finding's path/URL, line, confidence, masked evidence, impact, fix and verification steps. Show incomplete coverage when present.
5. Download the report and copy the consolidated repair prompt into the coding tool. Credential rotation remains a separate human action.
6. Choose **Rescan corrected input**, submit the corrected source with the same paths, and inspect the actual before/after comparison. The sample `fixtures/acceptance/corrected.ts` can use the same mapped path. Not detected does not prove fixed; unverified means evidence is not comparable.
7. For the authorized website demo, use `https://hemantkumar822.github.io/`. Website mode requires a valid recorded readiness proof. External or unsupported resources can legitimately leave partial coverage.

## Troubleshooting

- Port 8000 or 5173 occupied: stop the previous API/frontend before starting again.
- Queued scan: inspect coordinator logs and Docker availability; API health alone does not establish scanning capability.
- Missing images: pull the exact digests listed in `contracts/scanner-readiness.json` before the demo.
- Website admission unavailable: use [DEVELOPMENT](DEVELOPMENT.md) to inspect and refresh the readiness proof. Never bypass the gate.
- Reconnect: use the Scan ID in the same browser session. Lost ownership cookies cannot be restored by knowing the ID.

This launcher is a local prototype runner, not a public deployment configuration.
