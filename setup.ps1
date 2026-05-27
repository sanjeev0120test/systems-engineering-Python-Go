# Step 0 - Windows helper (creates venv; use WSL for Linux/automation modules).
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
Write-Host "Next: .\check.ps1 0   (must print PASS)" -ForegroundColor Cyan
Write-Host ""
Write-Host "For Linux subprocess and Go steps, use WSL:" -ForegroundColor Yellow
Write-Host "  wsl"
Write-Host "  cd /mnt/c/dev/systems-engineering-Python-Go"
Write-Host "  ./setup.sh && ./check.sh 0"
