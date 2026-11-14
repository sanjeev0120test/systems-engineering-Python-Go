# Windows check helper - Python steps 0-31 and Go steps 32-41.
param(
    [Parameter(Mandatory = $true)]
    [string]$Step
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
$env:PYTHONPATH = $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "Run setup.ps1 first" -ForegroundColor Red
    exit 1
}

function Pass($n) {
    Write-Host ""
    Write-Host "PASS: Step $n complete - see README.md step index for next step" -ForegroundColor Green
    exit 0
}

function Fail($n) {
    Write-Host ""
    Write-Host "FAIL: Step $n" -ForegroundColor Red
    exit 1
}

$testPaths = @{
    "1"  = "python/01_python_basics/step_01_variables/test_lesson.py"
    "2"  = "python/01_python_basics/step_02_control_flow/test_lesson.py"
    "3"  = "python/01_python_basics/step_03_functions/test_lesson.py"
    "4"  = "python/01_python_basics/step_04_classes/test_lesson.py"
    "5"  = "python/01_python_basics/step_05_exceptions/test_lesson.py"
    "6"  = "python/01_python_basics/step_06_typing/test_lesson.py"
    "7"  = "python/02_file_handling/test_lesson.py"
    "8"  = "python/03_json_yaml/test_lesson.py"
    "9"  = "python/04_logging/test_lesson.py"
    "10" = "python/05_subprocess_linux/test_lesson.py"
    "11" = "python/06_rest_api/client/test_lesson.py"
    "12" = "python/06_rest_api/server/test_lesson.py"
    "13" = "python/07_concurrency/test_lesson.py"
    "14" = "python/08_threading/test_lesson.py"
    "15" = "python/09_asyncio/test_lesson.py"
    "16" = "python/13_health_checker/test_lesson.py"
    "17" = "python/10_monitoring_agent/test_lesson.py"
    "18" = "python/11_log_parser/test_lesson.py"
    "19" = "python/12_alerting_engine/test_lesson.py"
    "20" = "python/16_rate_limiter/test_lesson.py"
    "21" = "python/23_retry_circuit_breaker/test_lesson.py"
    "22" = "python/24_queue_worker/test_lesson.py"
    "23" = "python/14_reverse_proxy_sim/test_lesson.py"
    "24" = "python/15_load_balancer_sim/test_lesson.py"
    "25" = "python/17_scheduler_cron/test_lesson.py"
    "26" = "python/18_config_management/test_lesson.py"
    "27" = "python/19_kubernetes_sim/test_lesson.py"
    "28" = "python/20_incident_simulator/test_lesson.py"
    "29" = "python/21_metrics_exporter/test_lesson.py"
    "30" = "python/22_distributed_system_basics/test_lesson.py"
    "31" = "python/25_mini_platform_engineering/test_lesson.py"
}

$goDirs = @{
    "32" = "go/01_go_basics"
    "33" = "go/02_concurrency"
    "34" = "go/03_http_server"
    "35" = "go/04_worker_pool"
    "36" = "go/05_log_processor"
    "37" = "go/06_api_gateway"
    "38" = "go/07_resilient_client"
    "39" = "go/08_job_queue"
    "40" = "go/09_canary_analysis"
    "41" = "go/10_consistent_hash_lb"
}

if ($Step -eq "0") {
    & $Python -c "import pytest, yaml, requests, fastapi; from python.common.logging_setup import new_trace_id; from python.common.paths import sample_data_path; assert sample_data_path('logs','access.log').exists(); print('Environment OK')"
    if ($LASTEXITCODE -ne 0) { Fail 0 }
    Pass 0
}

if ($Step -eq "all") {
    & $Python -m pytest python/ -q
    if ($LASTEXITCODE -ne 0) { Fail $Step }
    $goExe = Get-Command go -ErrorAction SilentlyContinue
    if (-not $goExe) {
        $goExe = Get-Command go -ErrorAction SilentlyContinue -Path @(
            "$env:ProgramFiles\Go\bin\go.exe",
            "${env:ProgramFiles(x86)}\Go\bin\go.exe"
        )
    }
    if ($goExe) {
        foreach ($dir in $goDirs.Values) {
            Push-Location (Join-Path $Root $dir)
            try {
                & $goExe.Source test ./...
                if ($LASTEXITCODE -ne 0) { Fail $Step }
            } finally {
                Pop-Location
            }
        }
        Write-Host "ALL PYTHON + GO TESTS PASS" -ForegroundColor Green
    } else {
        Write-Host "ALL PYTHON TESTS PASS (Go steps 32-41: install Go or use WSL ./check.sh N)" -ForegroundColor Green
    }
    exit 0
}

if ($goDirs.ContainsKey($Step)) {
    $goExe = Get-Command go -ErrorAction SilentlyContinue
    if (-not $goExe) {
        $goExe = Get-Command go -ErrorAction SilentlyContinue -Path @(
            "$env:ProgramFiles\Go\bin\go.exe",
            "${env:ProgramFiles(x86)}\Go\bin\go.exe"
        )
    }
    if (-not $goExe) {
        Write-Host "Go not found. Install Go 1.22+ or run: winget install GoLang.Go" -ForegroundColor Red
        exit 1
    }
    Push-Location (Join-Path $Root $goDirs[$Step])
    try {
        & $goExe.Source test ./...
        if ($LASTEXITCODE -ne 0) { Fail $Step }
    } finally {
        Pop-Location
    }
    Pass $Step
}

if (-not $testPaths.ContainsKey($Step)) {
    Write-Host "Unknown step: $Step"
    exit 1
}

& $Python -m pytest $testPaths[$Step] -q
if ($LASTEXITCODE -eq 0) { Pass $Step } else { Fail $Step }
