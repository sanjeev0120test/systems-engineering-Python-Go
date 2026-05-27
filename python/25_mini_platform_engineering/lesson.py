"""Step 31 — Mini platform engineering capstone."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (SRE) ---
# Platform engineering ships paved roads: standardized lint/test/deploy pipelines so
# product teams don't reinvent CI/CD. A single report artifact (like this lesson writes
# to sample_data/output/) mirrors build logs, deployment records, and change tickets.

# --- Production patterns ---
# - Fail fast at lint — cheapest feedback loop
# - Immutable artifacts promoted staging → prod (same SHA)
# - Deployment metrics: lead time, change failure rate, MTTR (DORA)

# --- Java developer note ---
# Jenkins/GitHub Actions/GitLab CI orchestrate the same stages. This capstone keeps
# them in Python so you see gating logic without YAML indirection.

# --- How to run ---
# ./run.sh 31
# ./check.sh 31


def main() -> None:
    from solution import run_pipeline

    report = run_pipeline("payment-api", environment="staging")
    for stage in report.stages:
        logger.info("[%s] %s — %s", "PASS" if stage.success else "FAIL", stage.name, stage.detail)
    logger.info("Deployed: %s", report.deployed)
    logger.info("Report under sample_data/output/platform_pipeline_report.txt")


if __name__ == "__main__":
    main()
