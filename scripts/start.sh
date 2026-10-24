#!/usr/bin/env bash
# VibeGuard dev launcher — works from Git Bash, WSL, or any bash shell.
# Starts: FastAPI (port 8000) + coordinator worker + Vite dev server (port 5173)
#
# Usage:
#   ./scripts/start.sh             # full stack (needs Docker for real scans)
#   ./scripts/start.sh --no-docker # API + Vite only, scans stay queued

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
NO_DOCKER=false
PIDS=()

for arg in "$@"; do
  case $arg in
    --no-docker) NO_DOCKER=true ;;
    *) echo "Unknown flag: $arg"; exit 1 ;;
  esac
done

# ── cleanup on exit ──────────────────────────────────────────────────────────
cleanup() {
  echo ""
  echo "Stopping VibeGuard…"
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cd "$PROJECT_ROOT"

# ── check tools ───────────────────────────────────────────────────────────────
for tool in uv node npm; do
  if ! command -v "$tool" &>/dev/null; then
    echo "Error: '$tool' not found. Install it and retry." >&2
    exit 1
  fi
done

# ── .env ─────────────────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "✔ Created .env from .env.example — add GROQ_API_KEY there to enable AI."
fi

# ── Python deps ───────────────────────────────────────────────────────────────
if [ ! -f ".venv/Scripts/python.exe" ] && [ ! -f ".venv/bin/python" ]; then
  echo "⟳ Installing Python dependencies (uv sync)…"
  uv sync --frozen
fi

# ── Frontend deps ─────────────────────────────────────────────────────────────
if [ ! -d "frontend/node_modules/vite" ]; then
  echo "⟳ Installing frontend dependencies (npm ci)…"
  npm --prefix frontend ci
fi

# ── Runtime dir ───────────────────────────────────────────────────────────────
if [ -z "${VIBEGUARD_RUNTIME_DIR:-}" ]; then
  # Use LOCALAPPDATA on Windows/Git Bash, or $HOME/.local/share on Linux
  if [ -n "${LOCALAPPDATA:-}" ]; then
    export VIBEGUARD_RUNTIME_DIR="$(cygpath -u "$LOCALAPPDATA")/VibeGuard/demo-runtime"
  else
    export VIBEGUARD_RUNTIME_DIR="$HOME/.local/share/vibeguard/demo-runtime"
  fi
fi
echo "Runtime dir: $VIBEGUARD_RUNTIME_DIR"

# ── Docker check ──────────────────────────────────────────────────────────────
if [ "$NO_DOCKER" = false ]; then
  if ! command -v docker &>/dev/null; then
    echo "⚠  docker not found — use --no-docker to skip. Scans will stay queued."
    NO_DOCKER=true
  elif ! docker info --format '{{.OSType}}' 2>/dev/null | grep -q linux; then
    echo "⚠  Docker Desktop not running or not using Linux engine — use --no-docker to skip."
    NO_DOCKER=true
  fi
fi

# ── log dir ───────────────────────────────────────────────────────────────────
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
if [ -n "${LOCALAPPDATA:-}" ]; then
  LOG_ROOT="$(cygpath -u "$LOCALAPPDATA")/VibeGuard/dev-logs/$TIMESTAMP"
else
  LOG_ROOT="$HOME/.local/share/vibeguard/dev-logs/$TIMESTAMP"
fi
mkdir -p "$LOG_ROOT"

echo ""
echo "Starting VibeGuard dev stack…"

# ── start API ─────────────────────────────────────────────────────────────────
uv run --env-file .env \
  uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload \
  >"$LOG_ROOT/api.log" 2>"$LOG_ROOT/api.err.log" &
PIDS+=($!)
echo "  ▸ API (PID $!)"

# ── start coordinator ─────────────────────────────────────────────────────────
if [ "$NO_DOCKER" = false ]; then
  uv run --env-file .env python -m workers.coordinator \
    >"$LOG_ROOT/worker.log" 2>"$LOG_ROOT/worker.err.log" &
  PIDS+=($!)
  echo "  ▸ Coordinator worker (PID $!)"
else
  echo "  ⚠  Coordinator skipped (--no-docker). Scans will stay in 'queued' state."
fi

# ── start Vite dev server ─────────────────────────────────────────────────────
npm --prefix frontend run dev \
  >"$LOG_ROOT/frontend.log" 2>"$LOG_ROOT/frontend.err.log" &
PIDS+=($!)
echo "  ▸ Vite dev server (PID $!)"

# ── wait for API health ───────────────────────────────────────────────────────
echo "Waiting for API…"
DEADLINE=$((SECONDS + 30))
HEALTHY=false
while [ $SECONDS -lt $DEADLINE ]; do
  if curl -sf "http://127.0.0.1:8000/api/v1/health" 2>/dev/null | grep -q '"ok"'; then
    HEALTHY=true
    break
  fi
  sleep 0.5
done

if [ "$HEALTHY" = false ]; then
  echo "Error: API did not become healthy in 30s. Logs: $LOG_ROOT" >&2
  exit 1
fi

echo ""
echo "  ┌──────────────────────────────────────────────────────────┐"
echo "  │  VibeGuard is running                                    │"
echo "  │                                                          │"
echo "  │  Open:  http://127.0.0.1:5173                            │"
echo "  │  API:   http://127.0.0.1:8000/api/v1/health              │"
echo "  │  Logs:  $LOG_ROOT"
echo "  │                                                          │"
echo "  │  Press Ctrl+C to stop all processes.                     │"
echo "  └──────────────────────────────────────────────────────────┘"
echo ""
if [ "$NO_DOCKER" = false ]; then
  echo "  Real scans: submit a codebase, repository URL, or website URL."
else
  echo "  UI demo only — start Docker Desktop then rerun without --no-docker for real scans."
fi

# ── keep alive ────────────────────────────────────────────────────────────────
wait
