#!/usr/bin/env bash
# Run any practice step: ./run.sh <N> [lesson|exercise|solution|server]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

STEP="${1:-}"
MODE="${2:-lesson}"

if [ -z "$STEP" ]; then
  echo "Usage: ./run.sh <step-number> [lesson|exercise|solution|server]"
  echo "Example: ./run.sh 1"
  exit 1
fi

case "$MODE" in
  lesson|exercise|solution|server) ;;
  *)
    echo "Invalid mode: $MODE (use lesson, exercise, solution, or server for step 12)"
    exit 1
    ;;
esac

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

run_python() {
  python "$1"
}

case "$STEP" in
  0)
    echo "Step 0 is setup only. Run: ./setup.sh && ./check.sh 0"
    exit 1
    ;;
  1) run_python python/01_python_basics/step_01_variables/${MODE}.py ;;
  2) run_python python/01_python_basics/step_02_control_flow/${MODE}.py ;;
  3) run_python python/01_python_basics/step_03_functions/${MODE}.py ;;
  4) run_python python/01_python_basics/step_04_classes/${MODE}.py ;;
  5) run_python python/01_python_basics/step_05_exceptions/${MODE}.py ;;
  6) run_python python/01_python_basics/step_06_typing/${MODE}.py ;;
  7) run_python python/02_file_handling/${MODE}.py ;;
  8) run_python python/03_json_yaml/${MODE}.py ;;
  9) run_python python/04_logging/${MODE}.py ;;
  10) run_python python/05_subprocess_linux/${MODE}.py ;;
  11) run_python python/06_rest_api/client/${MODE}.py ;;
  12)
    if [ "$MODE" = "server" ]; then
      run_python python/06_rest_api/server/server.py
    else
      run_python python/06_rest_api/server/${MODE}.py
    fi
    ;;
  13) run_python python/07_concurrency/${MODE}.py ;;
  14) run_python python/08_threading/${MODE}.py ;;
  15) run_python python/09_asyncio/${MODE}.py ;;
  16) run_python python/13_health_checker/${MODE}.py ;;
  17) run_python python/10_monitoring_agent/${MODE}.py ;;
  18) run_python python/11_log_parser/${MODE}.py ;;
  19) run_python python/12_alerting_engine/${MODE}.py ;;
  20) run_python python/16_rate_limiter/${MODE}.py ;;
  21) run_python python/23_retry_circuit_breaker/${MODE}.py ;;
  22) run_python python/24_queue_worker/${MODE}.py ;;
  23) run_python python/14_reverse_proxy_sim/${MODE}.py ;;
  24) run_python python/15_load_balancer_sim/${MODE}.py ;;
  25) run_python python/17_scheduler_cron/${MODE}.py ;;
  26) run_python python/18_config_management/${MODE}.py ;;
  27) run_python python/19_kubernetes_sim/${MODE}.py ;;
  28) run_python python/20_incident_simulator/${MODE}.py ;;
  29) run_python python/21_metrics_exporter/${MODE}.py ;;
  30) run_python python/22_distributed_system_basics/${MODE}.py ;;
  31) run_python python/25_mini_platform_engineering/${MODE}.py ;;
  32) (cd go/01_go_basics && go run .) ;;
  33) (cd go/02_concurrency && go run .) ;;
  34) (cd go/03_http_server && go run .) ;;
  35) (cd go/04_worker_pool && go run .) ;;
  36) (cd go/05_log_processor && go run .) ;;
  *)
    echo "Unknown step: $STEP (see START_HERE.md or docs/STEP_INDEX.md)"
    exit 1
    ;;
esac
