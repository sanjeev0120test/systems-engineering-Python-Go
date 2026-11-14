# Windows run helper - Python steps 1-31 and Go steps 32-41 (when Go is installed).
param(
    [Parameter(Mandatory = $true)]
    [string]$Step,
    [string]$Mode = "lesson"
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

if ($Mode -notin @("lesson", "exercise", "solution", "server")) {
    Write-Host "Invalid mode: $Mode" -ForegroundColor Red
    exit 1
}

$paths = @{
    "1"  = "python/01_python_basics/step_01_variables/$Mode.py"
    "2"  = "python/01_python_basics/step_02_control_flow/$Mode.py"
    "3"  = "python/01_python_basics/step_03_functions/$Mode.py"
    "4"  = "python/01_python_basics/step_04_classes/$Mode.py"
    "5"  = "python/01_python_basics/step_05_exceptions/$Mode.py"
    "6"  = "python/01_python_basics/step_06_typing/$Mode.py"
    "7"  = "python/02_file_handling/$Mode.py"
    "8"  = "python/03_json_yaml/$Mode.py"
    "9"  = "python/04_logging/$Mode.py"
    "10" = "python/05_subprocess_linux/$Mode.py"
    "11" = "python/06_rest_api/client/$Mode.py"
    "12" = if ($Mode -eq "server") { "python/06_rest_api/server/server.py" } else { "python/06_rest_api/server/$Mode.py" }
    "13" = "python/07_concurrency/$Mode.py"
    "14" = "python/08_threading/$Mode.py"
    "15" = "python/09_asyncio/$Mode.py"
    "16" = "python/13_health_checker/$Mode.py"
    "17" = "python/10_monitoring_agent/$Mode.py"
    "18" = "python/11_log_parser/$Mode.py"
    "19" = "python/12_alerting_engine/$Mode.py"
    "20" = "python/16_rate_limiter/$Mode.py"
    "21" = "python/23_retry_circuit_breaker/$Mode.py"
    "22" = "python/24_queue_worker/$Mode.py"
    "23" = "python/14_reverse_proxy_sim/$Mode.py"
    "24" = "python/15_load_balancer_sim/$Mode.py"
    "25" = "python/17_scheduler_cron/$Mode.py"
    "26" = "python/18_config_management/$Mode.py"
    "27" = "python/19_kubernetes_sim/$Mode.py"
    "28" = "python/20_incident_simulator/$Mode.py"
    "29" = "python/21_metrics_exporter/$Mode.py"
    "30" = "python/22_distributed_system_basics/$Mode.py"
    "31" = "python/25_mini_platform_engineering/$Mode.py"
}

if ($Step -eq "0") {
    Write-Host "Run setup.ps1 then check.ps1 0"
    exit 1
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
        Write-Host "Alternative: wsl ./run.sh $Step" -ForegroundColor Yellow
        exit 1
    }
    Push-Location (Join-Path $Root $goDirs[$Step])
    try {
        & $goExe.Source run .
    } finally {
        Pop-Location
    }
    exit $LASTEXITCODE
}

if (-not $paths.ContainsKey($Step)) {
    Write-Host "Unknown step: $Step"
    exit 1
}

& $Python $paths[$Step]
