#!/usr/bin/env python3
"""Cross-check repo structure and run random step validations."""

from __future__ import annotations

import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STEP_TESTS: dict[int, str] = {
    1: "python/01_python_basics/step_01_variables/test_lesson.py",
    2: "python/01_python_basics/step_02_control_flow/test_lesson.py",
    3: "python/01_python_basics/step_03_functions/test_lesson.py",
    4: "python/01_python_basics/step_04_classes/test_lesson.py",
    5: "python/01_python_basics/step_05_exceptions/test_lesson.py",
    6: "python/01_python_basics/step_06_typing/test_lesson.py",
    7: "python/02_file_handling/test_lesson.py",
    8: "python/03_json_yaml/test_lesson.py",
    9: "python/04_logging/test_lesson.py",
    10: "python/05_subprocess_linux/test_lesson.py",
    11: "python/06_rest_api/client/test_lesson.py",
    12: "python/06_rest_api/server/test_lesson.py",
    13: "python/07_concurrency/test_lesson.py",
    14: "python/08_threading/test_lesson.py",
    15: "python/09_asyncio/test_lesson.py",
    16: "python/13_health_checker/test_lesson.py",
    17: "python/10_monitoring_agent/test_lesson.py",
    18: "python/11_log_parser/test_lesson.py",
    19: "python/12_alerting_engine/test_lesson.py",
    20: "python/16_rate_limiter/test_lesson.py",
    21: "python/23_retry_circuit_breaker/test_lesson.py",
    22: "python/24_queue_worker/test_lesson.py",
    23: "python/14_reverse_proxy_sim/test_lesson.py",
    24: "python/15_load_balancer_sim/test_lesson.py",
    25: "python/17_scheduler_cron/test_lesson.py",
    26: "python/18_config_management/test_lesson.py",
    27: "python/19_kubernetes_sim/test_lesson.py",
    28: "python/20_incident_simulator/test_lesson.py",
    29: "python/21_metrics_exporter/test_lesson.py",
    30: "python/22_distributed_system_basics/test_lesson.py",
    31: "python/25_mini_platform_engineering/test_lesson.py",
}

LESSON_RUNS: dict[int, list[str]] = {
    1: ["python/01_python_basics/step_01_variables/lesson.py"],
    9: ["python/04_logging/lesson.py"],
    18: ["python/11_log_parser/lesson.py"],
    19: ["python/12_alerting_engine/lesson.py"],
    31: ["python/25_mini_platform_engineering/lesson.py"],
}

REQUIRED_ROOT = [
    "README.md",
    "setup.sh",
    "setup.ps1",
    "run.sh",
    "run.ps1",
    "check.sh",
    "check.ps1",
    "requirements.txt",
    "pyproject.toml",
    "Makefile",
]

REQUIRED_SAMPLE = [
    "sample_data/logs/access.log",
    "sample_data/configs/service.yaml",
    "sample_data/metrics/host_metrics.json",
    "sample_data/alerts/rules.yaml",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"OK: {msg}")


def main() -> None:
    print("=== Structure checks ===")
    for name in REQUIRED_ROOT:
        path = ROOT / name
        if not path.exists():
            fail(f"Missing {name}")
        ok(name)

    for name in REQUIRED_SAMPLE:
        path = ROOT / name
        if not path.exists():
            fail(f"Missing {name}")
        ok(name)

    if not (ROOT / "python/common/logging_setup.py").exists():
        fail("Missing python/common/logging_setup.py")
    ok("python/common/logging_setup.py")

    for step, test_path in STEP_TESTS.items():
        tp = ROOT / test_path
        if not tp.exists():
            fail(f"Step {step} missing test: {test_path}")
        step_dir = tp.parent
        for fname in ("lesson.py", "exercise.py", "solution.py"):
            if not (step_dir / fname).exists():
                fail(f"Step {step} missing {fname} in {step_dir.relative_to(ROOT)}")
    ok(f"All {len(STEP_TESTS)} Python steps have lesson/exercise/solution/tests")

    for go_dir in [
        "go/01_go_basics",
        "go/02_concurrency",
        "go/03_http_server",
        "go/04_worker_pool",
        "go/05_log_processor",
    ]:
        gd = ROOT / go_dir
        if not (gd / "main.go").exists():
            fail(f"Missing {go_dir}/main.go")
        if not (gd / "go.mod").exists():
            fail(f"Missing {go_dir}/go.mod")
    ok("All 5 Go modules present")

    python_exe = ROOT / ".venv/Scripts/python.exe"
    if not python_exe.exists():
        python_exe = ROOT / ".venv/bin/python"
    if not python_exe.exists():
        fail("No .venv — run setup first")

    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)}

    print("\n=== Full pytest ===")
    r = subprocess.run(
        [str(python_exe), "-m", "pytest", "python/", "-q", "--tb=short"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
        fail("Full pytest failed")
    ok("Full pytest passed")

    print("\n=== Random step spot checks ===")
    sample_steps = sorted(random.sample(list(STEP_TESTS.keys()), 8))
    for step in sample_steps:
        test_path = STEP_TESTS[step]
        r = subprocess.run(
            [str(python_exe), "-m", "pytest", test_path, "-q"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            print(r.stdout)
            print(r.stderr)
            fail(f"Step {step} pytest failed")
        ok(f"Step {step} tests")

    print("\n=== Random lesson runs ===")
    for step, scripts in LESSON_RUNS.items():
        for script in scripts:
            r = subprocess.run(
                [str(python_exe), script],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if r.returncode != 0:
                print(r.stdout)
                print(r.stderr)
                fail(f"Step {step} lesson run failed: {script}")
            ok(f"Step {step} lesson: {script}")

    print("\n=== Import smoke ===")
    r = subprocess.run(
        [
            str(python_exe),
            "-c",
            "from python.common.logging_setup import get_logger, new_trace_id; "
            "from python.common.paths import sample_data_path; "
            "assert sample_data_path('logs','access.log').exists(); "
            "print('imports ok')",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        fail(f"Import smoke failed: {r.stderr}")
    ok("Common imports")

    print("\n=== ALL VALIDATION PASSED ===")


if __name__ == "__main__":
    main()
