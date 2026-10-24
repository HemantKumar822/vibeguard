# Run the real prototype

From the repository root in PowerShell 7:

```powershell
./scripts/start-demo.ps1
```

Prerequisites: Node 24 LTS, npm, uv, and Docker Desktop running its Linux engine. The launcher installs locked Python/frontend dependencies only if missing, checks that the pinned scanner images are cached, builds the production frontend, and starts the API, trusted coordinator and frontend together. Missing images produce an exact `docker pull` command. The app runs at **http://127.0.0.1:5173**. Keep the terminal open; Ctrl+C stops the three process trees it started. No scan is launched automatically.

The default private runtime is `%LOCALAPPDATA%\VibeGuard\demo-runtime`, outside the checkout and OneDrive. Local process logs are under `%LOCALAPPDATA%\VibeGuard\demo-logs`. The in-app activity log shows actual scanner states and recorded timestamps, not raw scanner output or invented per-rule events. The built application contains no mock responses or development fixture interface. Synthetic fixtures remain in the repository solely for automated tests and explicitly labeled scanner demonstrations.

## Configure Groq once

The launcher creates `.env` from `.env.example` if needed. A local `.env` is ignored by Git. Edit it locally:

```dotenv
VIBEGUARD_AI_ENABLED=1
VIBEGUARD_AI_PROVIDER=groq
VIBEGUARD_AI_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=your_key_here
```

Get a key from [Groq Console](https://console.groq.com/keys). Restart the launcher after editing `.env`. Both the API and coordinator load it; no key goes to the browser. On each submission, select **Use AI explanations (optional)**. This opt-in sends bounded sanitized finding metadata to Groq. It does not upload the codebase or raw scanner output.

The integration uses Groq's [Chat Completions API](https://console.groq.com/docs/text-chat), JSON output and `llama-3.3-70b-versatile`. AI selects grounded guidance from the verified finding's existing options. It does not invent new findings or claim fixes succeeded. Required changes, verification steps and credential rotation guidance remain in the deterministic repair prompt. A missing key, rate limit, timeout or invalid response leaves a working report and marks AI guidance as fallback. A live Groq request requires your key and is not established by the automated adapter tests.

## Five-minute judge walkthrough

1. **Start:** Open the local URL and confirm API connected. Show Codebase, Repository and Website URL modes. Only submit inputs you own or have permission to assess.
2. **Real scan:** Choose your own project directory or public GitHub repository. For a predictable demonstration, explicitly describe `fixtures/acceptance/vulnerable.ts` as a deliberately vulnerable sample, choose individual files, and map it to `app/src/main.ts`. It is scanned by real Gitleaks and Semgrep; no result is mocked.
3. **Progress:** Confirm authorization, optionally enable AI, then submit. The input panel collapses and focus moves to the review. Show each real scanner waiting, running and completing, plus the timestamped activity log. A very fast check may finish between polling intervals; its recorded events still appear.
4. **Evidence:** Select a finding. Explain its location, confidence, masked evidence, impact, recommended fix and verification. Show coverage limitations. Click **Download report** for a readable Markdown file containing literal report text, and **Copy repair prompt** for the coding tool. The preview provides a manual copy fallback.
5. **Verify:** Apply the changes in your coding tool, choose **Rescan corrected input**, and submit the corrected version with the same paths. For the controlled sample, use `fixtures/acceptance/corrected.ts` mapped to the same path. Show the real before/after comparison; unverified means coverage or identity cannot establish a comparable result. Do not promise that absent findings prove security or credential rotation.
6. **Website option:** With authorization, scan `https://hemantkumar822.github.io/`. Show passive ZAP response checks and browser-visible asset checks. Partial coverage is expected for excluded cross-origin or unsupported resources. Website mode requires its recorded safety readiness proof to match the implementation; do not bypass the gate.

## Quick startup troubleshooting

- Port 8000 or 5173 occupied: stop the previous API/frontend and rerun. The launcher never kills unrelated processes.
- Docker unavailable: open Docker Desktop and wait for Engine running; use Linux containers.
- AI fallback: check `.env`, restart the launcher and opt in on a **new** scan. Existing reports are not silently regenerated.
- Scan queued: inspect the worker log in the printed log directory. The API cannot scan without the coordinator.
- Website unavailable: see the readiness instructions in [DEVELOPMENT.md](DEVELOPMENT.md). Source/repository mode remains available.
- For a startup-only check with automatic cleanup: `./scripts/start-demo.ps1 -SmokeCheck`. It checks real HTTP health through the frontend proxy without scanning or contacting Groq.
- For a repeat start when the frontend has not changed: `./scripts/start-demo.ps1 -SkipBuild`.

The launcher is a Windows local prototype runner. Docker isolates the scanner containers; the trusted coordinator stays on the host, as required by the existing isolation design. It is not an internet deployment configuration.
