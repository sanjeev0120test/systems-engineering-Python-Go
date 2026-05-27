#!/usr/bin/env bash
# Step 0 — one-time environment setup (WSL/Linux/macOS primary).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "=== Step 0: SRE Python Practice Lab Setup ==="

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found."
  echo "Install: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
  exit 1
fi

PY_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
echo "Python version: $PY_VERSION"
python3 -c 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ required"'

if ! command -v go >/dev/null 2>&1; then
  echo "WARN: go not found (needed for Steps 32-36). Install Go 1.22+ when ready."
else
  echo "Go version: $(go version)"
fi

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment .venv ..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo ""
echo "Setup complete. Verify with: ./check.sh 0"
echo "Start learning: open START_HERE.md → Step 1 → ./run.sh 1"
