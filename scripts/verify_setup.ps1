# Full environment verification - run after setup.ps1.
# Cross-checks Python, Go, sample data, and step 0 readiness (5 passes).
param(
    [int]$Passes = 5
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$env:PYTHONPATH = $Root

function Resolve-Go {
    $go = Get-Command go -ErrorAction SilentlyContinue
    if ($go) { return $go.Source }
    foreach ($p in @("$env:ProgramFiles\Go\bin\go.exe", "${env:ProgramFiles(x86)}\Go\bin\go.exe")) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

$Python = Join-Path $Root ".venv\Scripts\python.exe"
$failures = @()

Write-Host "=== Lab Setup Verification ($Passes passes) ===" -ForegroundColor Cyan
Write-Host "Root: $Root"
Write-Host ""

for ($i = 1; $i -le $Passes; $i++) {
    Write-Host "--- Pass $i of $Passes ---" -ForegroundColor Yellow
    $passOk = $true

    if (-not (Test-Path $Python)) {
        Write-Host "  [FAIL] .venv missing - run .\setup.ps1" -ForegroundColor Red
        $passOk = $false
    } else {
        $ver = & $Python --version 2>&1
        Write-Host "  [OK] Python venv: $ver"
    }

    $deps = @("pytest", "yaml", "requests", "fastapi", "uvicorn", "httpx", "psutil")
    foreach ($dep in $deps) {
        & $Python -c "import $dep" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [FAIL] Missing Python package: $dep" -ForegroundColor Red
            $passOk = $false
        }
    }
    if ($passOk) { Write-Host "  [OK] All Python dependencies importable" }

    $samples = @(
        "sample_data/logs/access.log",
        "sample_data/configs/service.yaml",
        "sample_data/metrics/host_metrics.json",
        "sample_data/alerts/rules.yaml"
    )
    foreach ($s in $samples) {
        if (-not (Test-Path (Join-Path $Root $s))) {
            Write-Host "  [FAIL] Missing sample data: $s" -ForegroundColor Red
            $passOk = $false
        }
    }
    if ($passOk) { Write-Host "  [OK] Sample data present" }

    & $Python (Join-Path $Root "scripts\_verify_imports.py") 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [FAIL] python.common imports" -ForegroundColor Red
        $passOk = $false
    } else {
        Write-Host "  [OK] python.common imports"
    }

    $goPath = Resolve-Go
    if ($goPath) {
        $goVer = & $goPath version 2>&1
        Write-Host "  [OK] Go: $goVer"
        foreach ($dir in @("go/01_go_basics", "go/02_concurrency", "go/03_http_server", "go/04_worker_pool", "go/05_log_processor", "go/06_api_gateway", "go/07_resilient_client", "go/08_job_queue", "go/09_canary_analysis", "go/10_consistent_hash_lb")) {
            Push-Location (Join-Path $Root $dir)
            try {
                & $goPath test ./... 2>$null
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "  [FAIL] Go tests: $dir" -ForegroundColor Red
                    $passOk = $false
                }
            } finally {
                Pop-Location
            }
        }
        if ($passOk) { Write-Host "  [OK] All Go module tests pass" }
    } else {
        Write-Host "  [WARN] Go not installed - Steps 32-41 need Go (winget install GoLang.Go)" -ForegroundColor Yellow
    }

    $wslOk = $false
    $wslJob = Start-Job { wsl echo ok 2>$null }
    if (Wait-Job $wslJob -Timeout 5) {
        $wslOut = Receive-Job $wslJob
        if ($wslOut -match "ok") { $wslOk = $true }
    }
    Remove-Job $wslJob -Force -ErrorAction SilentlyContinue
    if ($wslOk) {
        Write-Host "  [OK] WSL available (Step 10 Linux subprocess)"
    } else {
        Write-Host "  [WARN] WSL not responding - Step 10 may need WSL" -ForegroundColor Yellow
    }

    if (-not $passOk) { $failures += "Pass $i failed" }
    Write-Host ""
}

Write-Host "=== Summary ===" -ForegroundColor Cyan
if ($failures.Count -eq 0) {
    Write-Host "ALL $Passes PASSES OK - environment ready." -ForegroundColor Green
    Write-Host "Start: .\run.ps1 1  then  .\check.ps1 1" -ForegroundColor Cyan
    exit 0
}

Write-Host "Some checks failed:" -ForegroundColor Red
$failures | ForEach-Object { Write-Host "  - $_" }
Write-Host "Run .\setup.ps1 and install missing tools, then re-run this script." -ForegroundColor Yellow
exit 1
