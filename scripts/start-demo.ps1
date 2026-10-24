#requires -Version 7.0
[CmdletBinding()]
param([switch]$SmokeCheck, [switch]$SkipBuild)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$demoProcesses = [System.Collections.Generic.List[System.Diagnostics.Process]]::new()
$previousLocation = Get-Location
$previousRuntime = $env:VIBEGUARD_RUNTIME_DIR
try {
    Set-Location -LiteralPath $projectRoot
    $uvPath = (Get-Command uv -ErrorAction Stop).Source
    $nodePath = (Get-Command node -ErrorAction Stop).Source
    Get-Command npm -ErrorAction Stop | Out-Null
    $dockerCommand = Get-Command docker -ErrorAction SilentlyContinue
    $dockerPath = if ($dockerCommand) { $dockerCommand.Source } else { Join-Path $env:ProgramFiles 'Docker/Docker/resources/bin/docker.exe' }
    if (-not (Test-Path -LiteralPath $dockerPath)) { throw 'Install Docker Desktop and start its Linux engine first.' }
    $nodeMajor = [int]((& $nodePath --version).TrimStart('v').Split('.')[0])
    if ($nodeMajor -ne 24) { throw 'Use Node 24 LTS for this locked frontend.' }
    $dockerOs = & $dockerPath info --format '{{.OSType}}' 2>$null
    if ($LASTEXITCODE -ne 0 -or $dockerOs -ne 'linux') { throw 'Start Docker Desktop with the Linux engine, then rerun this command.' }
    foreach ($port in @(8000, 5173)) {
        if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) {
            throw "Port $port is already in use. Stop your previous API/frontend before starting the demo."
        }
    }
    if (-not (Test-Path -LiteralPath '.env')) {
        Copy-Item -LiteralPath '.env.example' -Destination '.env'
        Write-Host 'Created private .env. Add GROQ_API_KEY there to enable optional AI.' -ForegroundColor Yellow
    }
    if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
        & $uvPath sync --frozen
        if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
    }
    if (-not (Test-Path -LiteralPath 'frontend/node_modules/vite/bin/vite.js')) {
        & npm --prefix frontend ci
        if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
    }
    $readiness = Get-Content -LiteralPath 'contracts/scanner-readiness.json' -Raw | ConvertFrom-Json
    foreach ($scanner in $readiness.scanners) {
        & $dockerPath image inspect $scanner.digest *> $null
        if ($LASTEXITCODE -ne 0) {
            throw "Missing pinned $($scanner.name) image. Run: docker pull $($scanner.digest)"
        }
    }
    if (-not $env:VIBEGUARD_RUNTIME_DIR) {
        $env:VIBEGUARD_RUNTIME_DIR = Join-Path $env:LOCALAPPDATA 'VibeGuard/demo-runtime'
    }
    & $uvPath run --env-file .env python -c "from backend.core.settings import Settings; Settings.environment().validate()"
    if ($LASTEXITCODE -ne 0) { throw 'Runtime directory must be absolute, private, and outside this checkout and OneDrive.' }
    & $uvPath run --env-file .env python -c "from backend.adapters.explanations import configuration; from backend.core.website_readiness import ready; print('AI: configured (per-scan opt-in required)' if configuration() else 'AI: unavailable; deterministic guidance remains available'); print('Website review: ready' if ready() else 'Website review: readiness proof missing/stale; see docs/DEVELOPMENT.md')"
    if ($LASTEXITCODE -ne 0) { throw 'Configuration check failed.' }
    if (-not $SkipBuild -or -not (Test-Path -LiteralPath 'frontend/dist/index.html')) {
        & npm --prefix frontend run build
        if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
    }
    $logRoot = Join-Path $env:LOCALAPPDATA ('VibeGuard/demo-logs/' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
    New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
    function Start-DemoProcess([string]$Name, [string]$Executable, [string[]]$Arguments, [string]$Directory) {
        $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $Directory -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logRoot "$Name.log") -RedirectStandardError (Join-Path $logRoot "$Name.error.log")
        $demoProcesses.Add($process)
    }
    Start-DemoProcess 'api' $uvPath @('run', '--env-file', '.env', 'uvicorn', 'backend.api.main:app', '--host', '127.0.0.1', '--port', '8000') $projectRoot
    Start-DemoProcess 'worker' $uvPath @('run', '--env-file', '.env', 'python', '-m', 'workers.coordinator') $projectRoot
    Start-DemoProcess 'frontend' $nodePath @('node_modules/vite/bin/vite.js', 'preview') (Join-Path $projectRoot 'frontend')
    $deadline = (Get-Date).AddSeconds(45)
    $healthy = $false
    while ((Get-Date) -lt $deadline) {
        foreach ($process in $demoProcesses) {
            if ($process.HasExited) { throw "A demo process exited. Inspect local logs: $logRoot" }
        }
        try {
            $health = Invoke-RestMethod 'http://127.0.0.1:5173/api/v1/health' -TimeoutSec 2
            $page = Invoke-WebRequest 'http://127.0.0.1:5173/' -TimeoutSec 2
            if ($health.status -eq 'ok' -and $health.contract_version -eq 'v1' -and $page.StatusCode -eq 200) { $healthy = $true; break }
        } catch { Start-Sleep -Milliseconds 500 }
    }
    if (-not $healthy) { throw "Startup timed out. Inspect local logs: $logRoot" }
    Write-Host "`nVibeGuard is ready: http://127.0.0.1:5173" -ForegroundColor Cyan
    Write-Host "Real API + coordinator + built frontend. Logs: $logRoot"
    Write-Host 'Scans run only when you submit an authorized input. Press Ctrl+C to stop these three processes.'
    if ($SmokeCheck) {
        Write-Host 'Startup smoke check passed. No scans or external AI requests were made.' -ForegroundColor Green
    } else {
        while ($true) {
            Start-Sleep -Seconds 2
            foreach ($process in $demoProcesses) {
                if ($process.HasExited) { throw "A demo process exited. Inspect local logs: $logRoot" }
            }
        }
    }
} finally {
    foreach ($process in $demoProcesses) {
        if (-not $process.HasExited) {
            # Only terminate process trees started by this invocation.
            & taskkill.exe /PID $process.Id /T /F *> $null
        }
        $process.Dispose()
    }
    $env:VIBEGUARD_RUNTIME_DIR = $previousRuntime
    Set-Location -LiteralPath $previousLocation
}
