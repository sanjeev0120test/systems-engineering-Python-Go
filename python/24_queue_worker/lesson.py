"""Step 22 — File-based job queue, workers, and dead-letter queue."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger
from python.common.paths import output_path

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (SRE) ---
# Synchronous request/response cannot absorb traffic spikes. Queues decouple producers
# from consumers: API returns 202 Accepted, workers drain backlog at sustainable rate.
# Dead-letter queues (DLQ) preserve poison messages for inspection instead of infinite
# retry loops that block healthy jobs (SQS DLQ, RabbitMQ dead-letter exchange).

# --- Production patterns ---
# - At-least-once delivery: workers must be idempotent (dedupe by job_id)
# - Visibility timeout: processing/ folder ≈ in-flight lease; stale jobs requeued
# - Monitor queue depth (pending_count) — sustained growth means under-provisioned workers
# - Alert on DLQ rate — often bad deploy, schema change, or upstream data corruption

# --- Java developer note ---
# JMS / Kafka consumers with retry topics mirror pending → DLQ. Celery/RQ are Python
# equivalents; this lesson uses files so you see the mechanics without Redis/RabbitMQ.

# --- How to run ---
# ./run.sh 22
# ./check.sh 22


def main() -> None:
    from solution import FileJobQueue, Job, run_worker

    queue = FileJobQueue(output_path("queue_worker"))
    queue.enqueue({"task": "send_alert", "severity": "warning"})
    queue.enqueue({"task": "rotate_logs", "host": "web-01"})

    def handler(job: Job) -> None:
        logger.info("Processing job %s payload=%s", job.job_id, job.payload)

    stats = run_worker(queue, handler, max_jobs=10)
    logger.info(
        "Worker stats: processed=%s succeeded=%s failed=%s",
        stats["processed"],
        stats["succeeded"],
        stats["failed"],
    )
    logger.info("Artifacts live under sample_data/output/queue_worker/")


if __name__ == "__main__":
    main()
