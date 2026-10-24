#!/usr/bin/env python3
"""
Quick verification script -- run before the hackathon demo.
Checks: settings, Groq API key (live call), scanner readiness, API health.

Usage:
    uv run --env-file .env python scripts/verify_demo.py
    uv run --env-file .env python scripts/verify_demo.py --skip-groq
"""
import argparse
import http.client
import json
import os
import subprocess
import sys
from pathlib import Path

# Make sure the project root is on the path regardless of cwd
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)  # ensure relative paths work

# ASCII-safe symbols for Windows console compatibility
OK   = "[OK]  "
FAIL = "[FAIL]"
WARN = "[WARN]"
INFO = "[    ]"

passed = []
failed = []
warnings = []


def check(label, ok, message="", warn=False):
    sym = WARN if warn else (OK if ok else FAIL)
    print(f"  {sym}  {label}{': ' + message if message else ''}")
    if warn:
        warnings.append(label)
    elif ok:
        passed.append(label)
    else:
        failed.append(label)
    return ok


# -- 1. Python env -------------------------------------------------------------
print("\n[1/5] Python environment")
try:
    from backend.core.settings import Settings
    from backend.adapters.explanations import configuration, explain
    check("backend imports", True)
except ImportError as e:
    check("backend imports", False, str(e))
    sys.exit("Run: uv sync --frozen  then retry.")

# -- 2. Settings ---------------------------------------------------------------
print("\n[2/5] Runtime settings")
runtime_dir = os.environ.get("VIBEGUARD_RUNTIME_DIR", "")
if not runtime_dir:
    os.environ["VIBEGUARD_RUNTIME_DIR"] = str(
        Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share")) / "VibeGuard" / "demo-runtime"
    )
    runtime_dir = os.environ["VIBEGUARD_RUNTIME_DIR"]

settings = Settings.environment()
if settings:
    try:
        settings.validate()
        check("VIBEGUARD_RUNTIME_DIR", True, runtime_dir)
    except Exception as e:
        check("VIBEGUARD_RUNTIME_DIR", False, str(e))
else:
    check("Settings", False, "Settings.environment() returned None")

check("VIBEGUARD_ORIGIN", bool(os.environ.get("VIBEGUARD_ORIGIN")),
      os.environ.get("VIBEGUARD_ORIGIN", "NOT SET"))
check("VIBEGUARD_AI_ENABLED", os.environ.get("VIBEGUARD_AI_ENABLED") == "1",
      os.environ.get("VIBEGUARD_AI_ENABLED", "NOT SET"))

# -- 3. Groq AI (live API call) ------------------------------------------------
print("\n[3/5] Groq AI (live API call)")

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--skip-groq", action="store_true")
args, _ = parser.parse_known_args()

groq_key = os.environ.get("GROQ_API_KEY", "").strip()
cfg = configuration()

ai_enabled = os.environ.get("VIBEGUARD_AI_ENABLED") == "1"

if not ai_enabled:
    check("Groq AI", True, "disabled (VIBEGUARD_AI_ENABLED!=1) - deterministic guidance active")
elif args.skip_groq:
    check("Groq key check", True, "skipped (--skip-groq)", warn=True)
elif not groq_key:
    check("GROQ_API_KEY", False, "not set in .env")
elif not cfg:
    check("Groq configuration", False, "configuration() returned None - check VIBEGUARD_AI_ENABLED=1 and VIBEGUARD_AI_PROVIDER=groq")
else:
    check("Groq config", True, f"{cfg.hostname}{cfg.path}")
    # Live minimal call
    print(f"  {INFO}  Making live call to api.groq.com...")
    try:
        body = json.dumps({
            "model": os.environ.get("VIBEGUARD_AI_MODEL", "llama-3.3-70b-versatile"),
            "temperature": 0,
            "max_completion_tokens": 10,
            "messages": [{"role": "user", "content": "Reply: ok"}],
        }).encode()
        conn = http.client.HTTPSConnection("api.groq.com", 443, timeout=10)
        conn.request("POST", "/openai/v1/chat/completions", body=body, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + groq_key,
        })
        resp = conn.getresponse()
        data = resp.read()
        conn.close()
        if resp.status == 200:
            result = json.loads(data)
            model_used = result.get("model", "?")
            check("Groq live call", True, f"HTTP 200 - model={model_used}")
        elif resp.status == 401:
            check("Groq live call", False, "HTTP 401 Invalid API Key (check key at console.groq.com/keys)")
        elif resp.status == 429:
            check("Groq live call", True, "HTTP 429 rate-limited (key is valid, just slow down)", warn=True)
        else:
            detail = json.loads(data).get("error", {}).get("message", "")
            check("Groq live call", False, f"HTTP {resp.status}: {detail}")
    except Exception as e:
        check("Groq live call", False, f"{type(e).__name__}: {e}")

# -- 4. Scanner images (Docker) ------------------------------------------------
print("\n[4/5] Docker scanner images")
try:
    readiness = json.loads((ROOT / "contracts" / "scanner-readiness.json").read_text())
    if not readiness.get("ready"):
        check("scanner-readiness.json", False, "ready=false - run: uv run python scripts/scanner_readiness.py")
    else:
        check("scanner-readiness.json", True, f"ready=true, checked {readiness.get('checked_at', '?')[:10]}")

    docker_ok = subprocess.run(
        ["docker", "info", "--format", "{{.OSType}}"],
        capture_output=True, text=True, timeout=5
    )
    if docker_ok.returncode != 0 or docker_ok.stdout.strip() != "linux":
        check("Docker Desktop", False, "not running or not using Linux engine - start Docker Desktop", warn=True)
    else:
        check("Docker Desktop", True, "Linux engine running")
        for scanner in readiness.get("scanners", []):
            result = subprocess.run(
                ["docker", "image", "inspect", scanner["digest"]],
                capture_output=True, timeout=10
            )
            check(f"Image: {scanner['name']} {scanner['expected_version']}",
                  result.returncode == 0,
                  "cached" if result.returncode == 0 else f"MISSING - run: docker pull {scanner['digest']}")
except FileNotFoundError:
    check("docker command", False, "Docker not found in PATH", warn=True)
except Exception as e:
    check("Docker check", False, str(e), warn=True)

# -- 5. Frontend build ---------------------------------------------------------
print("\n[5/5] Frontend")
node_modules = ROOT / "frontend" / "node_modules" / "vite"
check("node_modules installed", node_modules.exists(),
      "present" if node_modules.exists() else "missing - run: npm --prefix frontend ci")

# -- Summary -------------------------------------------------------------------
print()
print("=" * 58)
print(f"  {OK} Passed:   {len(passed)}")
if warnings:
    print(f"  {WARN} Warnings: {len(warnings)}")
if failed:
    print(f"  {FAIL} Failed:   {len(failed)}")
    for f in failed:
        print(f"         - {f}")
print("=" * 58)

if failed:
    print("\nFix the failures above then rerun this script.")
    sys.exit(1)
else:
    print("\nAll checks passed! Run the launcher:")
    print("  PowerShell 7:  ./scripts/dev-start.ps1")
    print("  Git Bash:      bash ./scripts/start.sh")
    sys.exit(0)
