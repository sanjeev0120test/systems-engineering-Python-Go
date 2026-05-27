#!/usr/bin/env bash
# Verify a step: ./check.sh <N> — human PASS/FAIL + pytest
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

STEP="${1:-}"
if [ -z "$STEP" ]; then
  echo "Usage: ./check.sh <step-number>"
  exit 1
fi

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

pass() {
  echo ""
  echo "PASS: Step $STEP complete — see README.md step index for Step $((STEP + 1))"
  exit 0
}

fail() {
  echo ""
  echo "FAIL: Step $STEP — fix errors above, then re-run ./check.sh $STEP"
  exit 1
}

pytest_step() {
  local test_path="$1"
  if [ ! -f "$test_path" ]; then
    echo "Missing test file: $test_path"
    return 1
  fi
  python -m pytest "$test_path" -q
}

go_test_step() {
  local dir="$1"
  (cd "$dir" && go test ./...)
}

case "$STEP" in
  0)
    echo "Checking environment ..."
    [ -f README.md ] || { echo "Missing README.md"; fail; }
    python -c "import pytest, yaml, requests, fastapi" || { echo "Run ./setup.sh first"; fail; }
    python -c "from python.common.logging_setup import new_trace_id; assert len(new_trace_id())==16"
    python -c "from python.common.paths import sample_data_path; assert sample_data_path('logs','access.log').exists()"
    echo "Environment OK."
    pass
    ;;
  1) pytest_step python/01_python_basics/step_01_variables/test_lesson.py && pass ;;
  2) pytest_step python/01_python_basics/step_02_control_flow/test_lesson.py && pass ;;
  3) pytest_step python/01_python_basics/step_03_functions/test_lesson.py && pass ;;
  4) pytest_step python/01_python_basics/step_04_classes/test_lesson.py && pass ;;
  5) pytest_step python/01_python_basics/step_05_exceptions/test_lesson.py && pass ;;
  6) pytest_step python/01_python_basics/step_06_typing/test_lesson.py && pass ;;
  7) pytest_step python/02_file_handling/test_lesson.py && pass ;;
  8) pytest_step python/03_json_yaml/test_lesson.py && pass ;;
  9) pytest_step python/04_logging/test_lesson.py && pass ;;
  10) pytest_step python/05_subprocess_linux/test_lesson.py && pass ;;
  11) pytest_step python/06_rest_api/client/test_lesson.py && pass ;;
  12) pytest_step python/06_rest_api/server/test_lesson.py && pass ;;
  13) pytest_step python/07_concurrency/test_lesson.py && pass ;;
  14) pytest_step python/08_threading/test_lesson.py && pass ;;
  15) pytest_step python/09_asyncio/test_lesson.py && pass ;;
  16) pytest_step python/13_health_checker/test_lesson.py && pass ;;
  17) pytest_step python/10_monitoring_agent/test_lesson.py && pass ;;
  18) pytest_step python/11_log_parser/test_lesson.py && pass ;;
  19) pytest_step python/12_alerting_engine/test_lesson.py && pass ;;
  20) pytest_step python/16_rate_limiter/test_lesson.py && pass ;;
  21) pytest_step python/23_retry_circuit_breaker/test_lesson.py && pass ;;
  22) pytest_step python/24_queue_worker/test_lesson.py && pass ;;
  23) pytest_step python/14_reverse_proxy_sim/test_lesson.py && pass ;;
  24) pytest_step python/15_load_balancer_sim/test_lesson.py && pass ;;
  25) pytest_step python/17_scheduler_cron/test_lesson.py && pass ;;
  26) pytest_step python/18_config_management/test_lesson.py && pass ;;
  27) pytest_step python/19_kubernetes_sim/test_lesson.py && pass ;;
  28) pytest_step python/20_incident_simulator/test_lesson.py && pass ;;
  29) pytest_step python/21_metrics_exporter/test_lesson.py && pass ;;
  30) pytest_step python/22_distributed_system_basics/test_lesson.py && pass ;;
  31) pytest_step python/25_mini_platform_engineering/test_lesson.py && pass ;;
  32) go_test_step go/01_go_basics && pass ;;
  33) go_test_step go/02_concurrency && pass ;;
  34) go_test_step go/03_http_server && pass ;;
  35) go_test_step go/04_worker_pool && pass ;;
  36) go_test_step go/05_log_processor && pass ;;
  all)
    echo "Running all step checks (0-36) ..."
    failed=0
    for step in $(seq 0 36); do
      echo "--- Step $step ---"
      if ! "$0" "$step"; then
        failed=1
      fi
    done
    if [ "$failed" -eq 0 ]; then
      echo "ALL STEPS PASS"
      exit 0
    fi
    fail
    ;;
  *)
    echo "Unknown step: $STEP"
    exit 1
    ;;
esac

fail
