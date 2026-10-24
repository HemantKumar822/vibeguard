#requires -Version 5.1
<#
.SYNOPSIS
    VibeGuard one-command dev launcher — for local demo and hackathon testing.
    Starts the API, coordinator worker, and Vite dev server in one terminal.

.DESCRIPTION
    Prerequisites:
      - Node 18+ (any LTS) and npm
      - uv   (https://docs.astral.sh/uv/)
      - Docker Desktop running its Linux engine  (for real scans)
        Without Docker: the API and frontend start, sessions and submissions
        work, but the coordinator cannot run scanners; scan stays "queued".

.EXAMPLE
    # From repo root in PowerShell 7:
    ./scripts/dev-start.ps1

.EXAMPLE
    # Skip Docker/scanner check (UI + API only, scans stay queued):
    ./scripts/dev-start.ps1 -NoDocker
#>
[CmdletBinding()]
param(
    [switch]$NoDocker   # Start API + frontend only; scans stay queued
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$procs = [System.Collections.Generic.List[System.Diagnostics.Process]]::new()

function Kill-All {
    foreach ($p in $procs) {
        if (-not $p.HasExited) {
            try { taskkill.exe /PID $p.Id /T /F *>$null } catch {}
        }
        $p.Dispose()
    }
}

trap { Kill-All; break }

Set-Location -LiteralPath $projectRoot

# ── tool checks ────────────────────────────────────────────────────────────────
$uvPath   = (Get-Command uv   -ErrorAction Stop).Source
$npmPath  = (Get-Command npm  -ErrorAction Stop).Source
Get-Command node -ErrorAction Stop | Out-Null

# ── .env ───────────────────────────────────────────────────────────────────────
if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
    Write-Host '✔ Created .env from .env.example. Add GROQ_API_KEY there to enable AI.' -ForegroundColor Yellow
}
Get-Content -LiteralPath '.env' | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith('#') -and $line.Contains('=')) {
        $parts = $line.Split('=', 2)
        [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process')
    }
}

# ── Python deps ────────────────────────────────────────────────────────────────
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    Write-Host '⟳ Installing Python dependencies (uv sync)…' -ForegroundColor Cyan
    & $uvPath sync --frozen
    if ($LASTEXITCODE -ne 0) { throw 'uv sync failed. Check .python-version and pyproject.toml.' }
}

# ── Frontend deps ──────────────────────────────────────────────────────────────
if (-not (Test-Path -LiteralPath 'frontend/node_modules/vite')) {
    Write-Host '⟳ Installing frontend dependencies (npm ci)…' -ForegroundColor Cyan
    & $npmPath --prefix frontend ci
    if ($LASTEXITCODE -ne 0) { throw 'npm ci failed.' }
}

# ── runtime dir ────────────────────────────────────────────────────────────────
if (-not $env:VIBEGUARD_RUNTIME_DIR) {
    $env:VIBEGUARD_RUNTIME_DIR = Join-Path $env:LOCALAPPDATA 'VibeGuard/demo-runtime'
}
Write-Host "Runtime dir: $env:VIBEGUARD_RUNTIME_DIR" -ForegroundColor DarkGray

# ── Docker / scanner check (optional) ─────────────────────────────────────────
if (-not $NoDocker) {
    $dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerCmd) {
        Write-Host '⚠  docker not found. Use -NoDocker to skip; scans will stay queued.' -ForegroundColor Yellow
        $NoDocker = $true
    } else {
        $dockerOs = & $dockerCmd.Source info --format '{{.OSType}}' 2>$null
        if ($LASTEXITCODE -ne 0 -or $dockerOs -ne 'linux') {
            Write-Host '⚠  Docker Desktop not running or not on Linux engine. Use -NoDocker to skip.' -ForegroundColor Yellow
            $NoDocker = $true
        }
    }
}

# ── port check ─────────────────────────────────────────────────────────────────
foreach ($port in @(8000, 5173)) {
    if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) {
        throw "Port $port is already in use. Stop the previous process then rerun."
    }
}

# ── log dir ────────────────────────────────────────────────────────────────────
$logRoot = Join-Path $env:LOCALAPPDATA ('VibeGuard/dev-logs/' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null

function Start-Proc([string]$Name, [string]$Exe, [string[]]$Args, [string]$Dir) {
    $p = Start-Process -FilePath $Exe -ArgumentList $Args `
            -WorkingDirectory $Dir -PassThru -WindowStyle Hidden `
            -RedirectStandardOutput (Join-Path $logRoot "$Name.log") `
            -RedirectStandardError  (Join-Path $logRoot "$Name.err.log")
    $procs.Add($p)
    Write-Host "  ▸ $Name (PID $($p.Id))" -ForegroundColor DarkGray
}

Write-Host "`nStarting VibeGuard dev stack…" -ForegroundColor Cyan

# 1. API
Start-Proc 'api' $uvPath `
    @('run', '--env-file', '.env', 'uvicorn', 'backend.api.main:app',
      '--host', '127.0.0.1', '--port', '8000', '--reload') `
    $projectRoot

# 2. Coordinator (only if Docker is available)
if (-not $NoDocker) {
    Start-Proc 'worker' $uvPath `
        @('run', '--env-file', '.env', 'python', '-m', 'workers.coordinator') `
        $projectRoot
} else {
    Write-Host '  ⚠  Coordinator skipped (-NoDocker). Scans will stay in "queued" state.' -ForegroundColor Yellow
}

# 3. Vite dev server (hot-reload, no build needed)
Start-Proc 'frontend' $npmPath `
    @('--prefix', 'frontend', 'run', 'dev') `
    $projectRoot

# ── wait for health ────────────────────────────────────────────────────────────
$deadline = (Get-Date).AddSeconds(30)
$healthy  = $false
Write-Host 'Waiting for API…' -ForegroundColor DarkGray
while ((Get-Date) -lt $deadline) {
    foreach ($p in $procs) {
        if ($p.HasExited) { throw "Process exited early. Inspect logs: $logRoot" }
    }
    try {
        $h = Invoke-RestMethod 'http://127.0.0.1:8000/api/v1/health' -TimeoutSec 1 -ErrorAction Stop
        if ($h.status -eq 'ok') { $healthy = $true; break }
    } catch { Start-Sleep -Milliseconds 400 }
}
if (-not $healthy) { throw "API did not become healthy. Logs: $logRoot" }

Write-Host @"

  ┌──────────────────────────────────────────────────────────┐
  │  VibeGuard is running                                    │
  │                                                          │
  │  Open:  http://127.0.0.1:5173                            │
  │  API:   http://127.0.0.1:8000/api/v1/health              │
  │  Logs:  $logRoot
  │                                                          │
  │  Press Ctrl+C to stop all processes.                     │
  └──────────────────────────────────────────────────────────┘
"@ -ForegroundColor Cyan

if (-not $NoDocker) {
    Write-Host '  Real scans: submit a codebase, repository URL, or website URL.' -ForegroundColor Green
} else {
    Write-Host '  UI demo only: start Docker Desktop then rerun without -NoDocker for real scans.' -ForegroundColor Yellow
}

# ── keep alive ─────────────────────────────────────────────────────────────────
try {
    while ($true) {
        Start-Sleep -Seconds 2
        foreach ($p in $procs) {
            if ($p.HasExited) { throw "A process exited. Logs: $logRoot" }
        }
    }
} finally {
    Write-Host "`nStopping…" -ForegroundColor DarkGray
    Kill-All
}
