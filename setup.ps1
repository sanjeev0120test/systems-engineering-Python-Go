# Step 0 - Windows helper (creates venv; Go steps 32-41 run natively when Go is installed).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "=== Step 0: Windows venv setup ===" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: python not found. Install Python 3.11+ from python.org" -ForegroundColor Red
    exit 1
}

Write-Host "Python: $(python --version)"

if (-not (Test-Path ".venv")) {
    Write-Host "Creating .venv ..."
    python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host ""
Write-Host "Windows venv ready." -ForegroundColor Green

$goPath = Get-Command go -ErrorAction SilentlyContinue
if (-not $goPath) {
    $goBin = "$env:ProgramFiles\Go\bin\go.exe"
    if (Test-Path $goBin) { $goPath = Get-Item $goBin }
}
if ($goPath) {
    Write-Host "Go: $(& $goPath.Source version 2>&1)" -ForegroundColor Green
    Write-Host "Go steps 32-41: .\run.ps1 32  and  .\check.ps1 32" -ForegroundColor Cyan
} else {
    Write-Host "Go not found. Install for Steps 32-41:" -ForegroundColor Yellow
    Write-Host "  winget install GoLang.Go" -ForegroundColor Yellow
    Write-Host "  Or use WSL: wsl ./setup.sh && wsl ./check.sh 32" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Verify: .\check.ps1 0   (must print PASS)" -ForegroundColor Cyan
Write-Host "Full audit: .\scripts\verify_setup.ps1" -ForegroundColor Cyan
Write-Host "Start learning: .\run.ps1 1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Step 10 (Linux subprocess) needs WSL if tests fail on Windows." -ForegroundColor Yellow
