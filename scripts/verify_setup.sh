#!/usr/bin/env bash
# Full environment verification — run after setup.sh (WSL/Linux/macOS).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PASSES="${1:-5}"

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

echo "=== Lab Setup Verification ($PASSES passes) ==="
echo "Root: $ROOT"
echo ""

failures=0

for i in $(seq 1 "$PASSES"); do
  echo "--- Pass $i of $PASSES ---"
  pass_ok=1

  if [ ! -x ".venv/bin/python" ]; then
    echo "  [FAIL] .venv missing — run ./setup.sh"
    pass_ok=0
  else
    echo "  [OK] Python venv: $(.venv/bin/python --version)"
  fi

  if ! .venv/bin/python -c "import pytest, yaml, requests, fastapi, uvicorn, httpx, psutil" 2>/dev/null; then
    echo "  [FAIL] Missing Python dependencies"
    pass_ok=0
  else
    echo "  [OK] All Python dependencies importable"
  fi

  for s in sample_data/logs/access.log sample_data/configs/service.yaml \
           sample_data/metrics/host_metrics.json sample_data/alerts/rules.yaml; do
    if [ ! -f "$s" ]; then
      echo "  [FAIL] Missing sample data: $s"
      pass_ok=0
    fi
  done
  [ "$pass_ok" -eq 1 ] && echo "  [OK] Sample data present"

  if ! .venv/bin/python -c "from python.common.logging_setup import new_trace_id; from python.common.paths import sample_data_path; assert len(new_trace_id())==16" 2>/dev/null; then
    echo "  [FAIL] python.common imports"
    pass_ok=0
  else
    echo "  [OK] python.common imports"
  fi

  if command -v go >/dev/null 2>&1; then
    echo "  [OK] Go: $(go version)"
    for dir in go/01_go_basics go/02_concurrency go/03_http_server go/04_worker_pool go/05_log_processor go/06_api_gateway go/07_resilient_client go/08_job_queue go/09_canary_analysis go/10_consistent_hash_lb; do
      if ! (cd "$dir" && go test ./...); then
        echo "  [FAIL] Go tests: $dir"
        pass_ok=0
      fi
    done
    [ "$pass_ok" -eq 1 ] && echo "  [OK] All Go module tests pass"
  else
    echo "  [WARN] Go not installed — Steps 32-41 need Go 1.22+"
  fi

  if ! ./check.sh 0 >/dev/null 2>&1; then
    echo "  [FAIL] ./check.sh 0"
    pass_ok=0
  else
    echo "  [OK] ./check.sh 0"
  fi

  [ "$pass_ok" -eq 0 ] && failures=$((failures + 1))
  echo ""
done

echo "=== Summary ==="
if [ "$failures" -eq 0 ]; then
  echo "ALL $PASSES PASSES OK — environment ready."
  echo "Start: ./run.sh 1  then  ./check.sh 1"
  exit 0
fi

echo "$failures pass(es) had failures. Run ./setup.sh and re-verify."
exit 1
