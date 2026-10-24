<div align="center">

<img src="https://raw.githubusercontent.com/HemantKumar822/vibeguard/main/frontend/src/assets/react.svg" width="60" height="60" alt="VibeGuard logo" />

# VibeGuard

**Evidence-backed security review for AI-built code and websites.**

*Submit → Scan → Inspect → Repair → Rescan*

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.161-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-required-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

</div>

---

## What is VibeGuard?

VibeGuard is a **security review workspace** purpose-built for AI-generated code. It accepts your codebase, a GitHub repository URL, or a live website, runs **real scanners** (Gitleaks + Semgrep + OWASP ZAP) in isolated Docker containers, and delivers structured findings with masked evidence, fix guidance, and a one-click repair prompt you can paste directly into your coding tool.

> **Built for the CY-02 Hackathon.** All five delivery epics are complete. No mocks in the production UI — every finding comes from a real scanner run.

---

## Features at a glance

| | Feature | Details |
|---|---------|---------|
| 🔍 | **Three input modes** | Upload a local codebase, any public GitHub repo/branch/commit, or a live website URL |
| 🐳 | **Isolated real scanners** | Gitleaks 8.30.1 + Semgrep 1.182.1 + OWASP ZAP 2.17.0 in pinned, network-disabled containers |
| 🎭 | **Masked evidence** | Findings show file/line/rule — never raw credential values |
| 🤖 | **Optional AI guidance** | Groq (llama-3.3-70b) selects grounded remediation; deterministic guidance works without it |
| 🔄 | **Real rescan + compare** | Submit a corrected version and get a real before/after finding comparison |
| 📊 | **Live scan activity** | Real-time scanner states, timestamps, and coverage — no invented progress |
| 📋 | **Report export** | Download a full Markdown report or copy the consolidated repair prompt |
| 🔒 | **Session-scoped ownership** | Scans belong to browser sessions; CSRF protection; no credential storage |

---

## Quick start (one command)

**Prerequisites:** [uv](https://docs.astral.sh/uv/), Node 18+ LTS, npm, Docker Desktop (Linux engine)

```powershell
# In PowerShell 7 from the repository root:
./scripts/dev-start.ps1
```

Open **http://127.0.0.1:5173** — done.

> **No Docker?** Use `./scripts/dev-start.ps1 -NoDocker` to start the UI + API only. Scans stay queued but the entire UI is fully interactive.

### What the launcher does automatically

1. Checks for `uv`, `node`, `npm`, and Docker Desktop
2. Creates `.env` from `.env.example` if missing
3. Installs locked Python deps (`uv sync`) only if needed
4. Installs locked frontend deps (`npm ci`) only if needed
5. Starts: **FastAPI** (port 8000) + **coordinator worker** + **Vite dev server** (port 5173)
6. Waits for health confirmation, then prints the URL

---

## Setup guide

### 1. Install prerequisites

| Tool | Version | Install |
|------|---------|---------|
| **uv** | latest | `pip install uv` or [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| **Node.js** | 18+ LTS | [nodejs.org](https://nodejs.org) |
| **npm** | bundled with Node | — |
| **Docker Desktop** | any recent | [docker.com](https://docker.com/products/docker-desktop/) — **start it with Linux containers** |
| **Python** | 3.12 | `uv` installs it automatically from `.python-version` |

### 2. Clone and configure

```powershell
git clone https://github.com/HemantKumar822/vibeguard.git
cd vibeguard

# .env is created automatically on first run, or create it manually:
Copy-Item .env.example .env
```

### 3. (Optional) Enable AI explanations with Groq

Get a free API key at [console.groq.com/keys](https://console.groq.com/keys), then edit `.env`:

```dotenv
VIBEGUARD_AI_ENABLED=1
VIBEGUARD_AI_PROVIDER=groq
VIBEGUARD_AI_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_your_key_here
```

Restart the launcher after saving. On each submission, check **"Use AI explanations (optional)"** to opt in per scan. The key never reaches the browser.

### 4. Pull the scanner images (first time, once)

Real scans need the three pinned Docker images (~1.5 GB total). Docker Desktop will pull them automatically on the first scan, or pull ahead of time:

```powershell
docker pull ghcr.io/gitleaks/gitleaks@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f
docker pull semgrep/semgrep@sha256:451b3d875c00dac7ed5db5293e584a07de11449a409c10b3c2d2652f429630b6
docker pull ghcr.io/zaproxy/zaproxy@sha256:5ccfff9a411743ab2615136a2edd7416bec9ce41572fa94e935df38c14adb2b6
```

---

## Running the demo

### Option A — Dev server (fastest, hot-reload)

```powershell
./scripts/dev-start.ps1           # full stack with Docker
./scripts/dev-start.ps1 -NoDocker # UI + API only (no real scans)
```

### Option B — Production build (judge demo)

```powershell
./scripts/start-demo.ps1          # builds frontend, then starts all three processes
./scripts/start-demo.ps1 -SkipBuild  # reuse existing build (faster repeat start)
./scripts/start-demo.ps1 -SmokeCheck # startup health check then auto-exit
```

Both options open at **http://127.0.0.1:5173**. Press **Ctrl+C** to stop all processes.

---

## Five-minute judge walkthrough

### 1. Start and confirm connection

Run the launcher, open the URL, and confirm the **"API connected · contract v1"** status in the top right.

### 2. Submit a scan

Choose one of three modes:

| Mode | What to enter | What runs |
|------|--------------|-----------|
| **Codebase** | Select `fixtures/acceptance/vulnerable.ts`, map it to `app/src/main.ts` | Real Gitleaks + Semgrep |
| **Repository** | `https://github.com/HemantKumar822/vibeguard` | Same checks on a recorded commit |
| **Website URL** | `https://hemantkumar822.github.io/` | OWASP ZAP + asset credential checks |

Check permission, optionally enable AI, hit submit.

### 3. Watch live scan activity

The input panel collapses. The **Checks and coverage** panel shows each scanner's real state (Waiting → Running → Completed) with timestamps. A very fast check may finish between polling intervals — its recorded events still appear.

### 4. Explore a finding

Select any finding. Show:
- **Location:** real file + line number
- **Masked evidence:** the finding is shown without the actual secret value
- **Fix guidance + verification steps**
- **Download report** → full Markdown file
- **Copy repair prompt** → paste into your coding tool (Cursor, Copilot, etc.)

### 5. Rescan and compare

Click **Rescan corrected input**, submit `fixtures/acceptance/corrected.ts` (same mapped path), and submit. After the scan completes, the **before/after comparison** appears automatically showing which findings were resolved, which are new, and which remain unverified.

---

## Architecture

```
Browser (React/TypeScript)
        │  CORS-same-origin  │  Cookie + CSRF
        ▼
FastAPI (port 8000)          ← session + intake + lifecycle
        │  SQLite WAL queue
        ▼
Trusted Coordinator          ← only process with Docker CLI access
        │  pinned digests, network-disabled, read-only containers
        ├── Gitleaks 8.30.1  (secrets/credentials)
        ├── Semgrep 1.182.1  (code security rules)
        └── OWASP ZAP 2.17.0 (website passive review)
```

**Key design decisions:**

- **API never controls Docker.** Only the separate trusted coordinator process has Docker CLI access.
- **Containers are network-disabled, read-only, non-root** with cgroup memory/CPU limits.
- **Source is never installed, built, or executed.** Files are read-only inside the scanner container.
- **Evidence is masked.** Raw credential values are never stored or displayed.
- **AI is opt-in and bounded.** At most 30 sanitized finding descriptions, 24 KiB request cap, 15-second timeout, no redirect following.

---

## Project structure

```
vibeguard/
├── backend/
│   ├── api/main.py          FastAPI routes and lifecycle
│   ├── adapters/            intake, storage, scanner, AI explanations
│   └── core/                contracts, policy, lifecycle, repair
├── frontend/src/
│   ├── App.tsx              Shell with health check
│   ├── SourceIntake.tsx     Main workspace — forms, polling, state
│   ├── ScanActivity.tsx     Live scanner progress panel
│   ├── Report.tsx           Findings, filters, repair prompt
│   ├── Comparison.tsx       Before/after diff view
│   └── reportExport.ts      Markdown download utility
├── workers/
│   ├── coordinator.py       Trusted worker loop (has Docker access)
│   ├── launcher.py          Container isolation wrapper
│   ├── source.py            Gitleaks + Semgrep execution
│   └── website.py           ZAP + asset scan execution
├── contracts/
│   ├── openapi.json         Canonical shared API schema
│   └── scanner-readiness.json  Verified pinned image digests
├── fixtures/acceptance/     Deliberately vulnerable/corrected test files
├── rules/                   Locally authored Gitleaks + Semgrep rules
├── scripts/
│   ├── dev-start.ps1        ← one-command dev launcher (this file)
│   └── start-demo.ps1       Production build launcher
└── tests/                   Backend + frontend unit tests
```

---

## Development commands

```powershell
# Install dependencies
uv sync --frozen
npm --prefix frontend ci

# Regenerate types from OpenAPI schema
uv run python scripts/export_contracts.py
npm --prefix frontend run generate:types

# Run backend tests
uv run pytest -q

# Run frontend tests
npm --prefix frontend test

# Type check + build + lint
npm --prefix frontend run typecheck
npm --prefix frontend run build
npm --prefix frontend run lint

# Verify scanner images
uv run python scripts/scanner_readiness.py --output contracts/scanner-readiness.json
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| **Port 8000 or 5173 in use** | Stop the previous process (`taskkill /F /IM node.exe` / stop uvicorn) then rerun |
| **Docker unavailable** | Open Docker Desktop → wait for "Engine running" → switch to Linux containers |
| **Scan stays "queued"** | The coordinator must be running. Check dev logs in `%LOCALAPPDATA%\VibeGuard\dev-logs\` |
| **AI returns fallback** | Check `.env` has `GROQ_API_KEY`, restart the launcher, opt in on a **new** scan |
| **Website mode unavailable** | Website readiness proof may be stale; see [DEVELOPMENT.md](docs/DEVELOPMENT.md) |
| **Missing scanner images** | Run the `docker pull` commands above or let the first scan pull them automatically |
| **`uv sync` fails** | Ensure Python 3.12 is available; `uv` installs it automatically from `.python-version` |

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript 5.9, Vite 8, Vanilla CSS |
| Backend | Python 3.12, FastAPI 0.161, uvicorn, SQLite WAL |
| Scanners | Gitleaks 8.30.1, Semgrep 1.182.1, OWASP ZAP 2.17.0 |
| AI (optional) | Groq API — llama-3.3-70b-versatile |
| Launcher | PowerShell 7, uv, Docker Desktop |
| Tests | pytest, vitest |

---

## Safety and ethics

- Only assess code and websites **you own or are authorized to review**.
- Scan results are candidates for human review — absence of findings does not certify security.
- Exposed credentials must be **revoked/rotated** separately; changing code alone is insufficient.
- Read [SECURITY.md](SECURITY.md) before reporting a sensitive issue.

---

<div align="center">

**VibeGuard** · Evidence before confidence.

*CY-02 Hackathon 2026 · [HemantKumar822/vibeguard](https://github.com/HemantKumar822/vibeguard)*

</div>
