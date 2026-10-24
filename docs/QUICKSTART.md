# Quickstart — VibeGuard

Everything you need to run the prototype and walk a judge through it.

---

## Start in one command

```powershell
# PowerShell 7, from the repository root:
./scripts/dev-start.ps1
```

Open **http://127.0.0.1:5173**

### Flags

| Flag | Effect |
|------|--------|
| *(none)* | Full stack — API + coordinator + Vite dev server. Real scans need Docker Desktop. |
| `-NoDocker` | API + Vite only. UI is fully interactive; scans stay "queued". Good for UI demos without Docker. |

### Alternate: production build (more realistic demo)

```powershell
./scripts/start-demo.ps1            # builds frontend, then starts everything
./scripts/start-demo.ps1 -SkipBuild # reuse existing build for a fast repeat start
```

---

## Prerequisites

| Tool | Install |
|------|---------|
| **uv** | `pip install uv` or [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| **Node 18+ LTS** | [nodejs.org](https://nodejs.org) (any LTS — 18, 20, 22, 24) |
| **Docker Desktop** | [docker.com](https://docker.com) — start with **Linux engine** |

Python 3.12 is installed automatically by `uv` from `.python-version`.

---

## Configure Groq AI (optional but impressive)

1. Get a free key at [console.groq.com/keys](https://console.groq.com/keys)
2. Edit `.env` (created automatically on first run):

```dotenv
VIBEGUARD_AI_ENABLED=1
VIBEGUARD_AI_PROVIDER=groq
VIBEGUARD_AI_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_your_key_here
```

3. Restart the launcher. On each new scan, check **"Use AI explanations (optional)"** to opt in.

The key stays server-side — it never reaches the browser or reports.

---

## Five-minute judge walkthrough

### Step 1 — Confirm connection

Open **http://127.0.0.1:5173**. The header shows **"API connected · contract v1"** in green when the backend is healthy.

### Step 2 — Submit a codebase scan

1. Leave mode as **Codebase**
2. Click **Choose individual files instead**
3. Select `fixtures/acceptance/vulnerable.ts` from the repo
4. Enter `app/src/main.ts` as its relative path (this is a deliberately vulnerable sample file)
5. Check the permission box
6. Optionally check "Use AI explanations"
7. Click **Submit source tree**

> For a repository scan: switch to **Repository**, enter `https://github.com/HemantKumar822/vibeguard`, leave ref blank.
> For a website scan: switch to **Website URL**, enter `https://hemantkumar822.github.io/`.

### Step 3 — Watch live scan activity

The input panel collapses. The **Checks and coverage** section shows:
- Each scanner's real state: Waiting → Running → Completed
- Timestamped activity log
- Coverage breakdown

> Point out: this is real scanner output, not simulated. A very fast check may finish between 1-second polling intervals — its timestamps still appear in the log.

### Step 4 — Explore findings

Once the scan completes:
- **Filter by severity** or search by rule/path
- **Click a finding** to expand location (real file + line), masked evidence, fix guidance, and verification steps
- **Copy repair prompt** — paste it directly into Cursor, GitHub Copilot Chat, or any AI coding tool
- **Download report** — generates a Markdown file with the full scan results

> Point out: the raw credential value is never shown — only masked evidence. Revocation remains a separate human action.

### Step 5 — Rescan and compare

1. Click **Rescan corrected input**
2. Select `fixtures/acceptance/corrected.ts`, map to the same path `app/src/main.ts`
3. Check permission and submit
4. After the second scan completes, the **before/after comparison** appears showing:
   - Which findings were resolved
   - Which are new
   - Which remain unverified (partial coverage or structural identity issues)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 or 5173 busy | Stop previous processes, then rerun |
| Docker not detected | Open Docker Desktop, wait for "Engine running", use Linux containers |
| Scan stays "queued" | The coordinator needs Docker to dispatch scanners. Check logs in `%LOCALAPPDATA%\VibeGuard\dev-logs\` |
| AI shows "fallback" | Verify `.env` has your `GROQ_API_KEY`, restart launcher, opt in on a **new** scan |
| Website mode unavailable | The website readiness proof may be stale. See [DEVELOPMENT.md](DEVELOPMENT.md) — source/repository mode is always available |
| First scan is slow | Docker is pulling the scanner images (~1.5 GB total). Subsequent scans use cached images. |

---

## What the scanners find

| Scanner | Finds |
|---------|-------|
| **Gitleaks 8.30.1** | Exposed credentials, API keys, private keys in source code |
| **Semgrep 1.182.1** | Unsafe eval, disabled TLS verification, missing auth middleware, credential assignments |
| **OWASP ZAP 2.17.0** | Passive response/header checks on captured website traffic |

All scanners run in **network-disabled, non-root, read-only** Docker containers with hard resource limits. Your source is never installed, built, or executed.
