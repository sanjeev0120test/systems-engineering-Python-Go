"""Step 25 — Cron scheduling with APScheduler."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (SRE) ---
# Cron jobs drive backups, certificate rotation, cache warming, and synthetic probes.
# Missed or overlapping runs cause data gaps and thundering herds. Treat schedulers as
# production services: monitor last_success_timestamp, alert on missed schedules.

# --- Production patterns ---
# - Idempotent jobs — a retry after partial failure must not corrupt state
# - Distributed locks (etcd, DynamoDB) when multiple schedulers could fire the same job
# - Kubernetes CronJob adds backoffLimit and concurrencyPolicy — learn those fields

# --- Java developer note ---
# @Scheduled in Spring or Quartz Scheduler mirror APScheduler triggers. Cron syntax
# is the lingua franca across Linux crontab, K8s CronJob, and Java schedulers.

# --- How to run ---
# ./run.sh 25
# ./check.sh 25


def main() -> None:
    from solution import CronJobRunner, run_once

    record = run_once(lambda: "config_backup_complete", job_name="nightly_backup")
    logger.info("One-shot job %s ran %s time(s)", record.job_name, record.run_count)

    runner = CronJobRunner()
    runner.register_job("synthetic_probe", lambda: "probe_ok", minute="*/5")
    logger.info("Registered cron job 'synthetic_probe' — use APScheduler in long-running agents")
    logger.info("Always expose job last-run metrics for alerting.")


if __name__ == "__main__":
    main()
