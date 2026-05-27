"""Step 22 solution — file-based job queue with workers and dead-letter queue."""

from __future__ import annotations

import json
import shutil
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from python.common.paths import output_path


@dataclass
class Job:
    job_id: str
    payload: dict[str, str]
    attempts: int = 0


class FileJobQueue:
    """Simple durable queue using directories: pending/, processing/, completed/, dlq/."""

    def __init__(self, base_dir: Path | None = None) -> None:
        root = base_dir or output_path("queue_worker")
        self.pending_dir = root / "pending"
        self.processing_dir = root / "processing"
        self.completed_dir = root / "completed"
        self.dlq_dir = root / "dlq"
        for directory in (
            self.pending_dir,
            self.processing_dir,
            self.completed_dir,
            self.dlq_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def _job_path(self, directory: Path, job_id: str) -> Path:
        return directory / f"{job_id}.json"

    def enqueue(self, payload: dict[str, str]) -> Job:
        job = Job(job_id=str(uuid.uuid4()), payload=payload)
        target = self._job_path(self.pending_dir, job.job_id)
        target.write_text(json.dumps(asdict(job)), encoding="utf-8")
        return job

    def dequeue(self) -> Job | None:
        pending_files = sorted(self.pending_dir.glob("*.json"))
        if not pending_files:
            return None
        source = pending_files[0]
        job = Job(**json.loads(source.read_text(encoding="utf-8")))
        destination = self._job_path(self.processing_dir, job.job_id)
        shutil.move(str(source), str(destination))
        return job

    def mark_completed(self, job: Job) -> None:
        source = self._job_path(self.processing_dir, job.job_id)
        destination = self._job_path(self.completed_dir, job.job_id)
        if source.exists():
            shutil.move(str(source), str(destination))

    def move_to_dlq(self, job: Job, reason: str) -> None:
        job.payload["dlq_reason"] = reason
        source = self._job_path(self.processing_dir, job.job_id)
        if not source.exists():
            source = self._job_path(self.pending_dir, job.job_id)
        destination = self._job_path(self.dlq_dir, job.job_id)
        destination.write_text(json.dumps(asdict(job)), encoding="utf-8")
        if source.exists():
            source.unlink()

    def pending_count(self) -> int:
        return len(list(self.pending_dir.glob("*.json")))

    def dlq_count(self) -> int:
        return len(list(self.dlq_dir.glob("*.json")))

    def completed_count(self) -> int:
        return len(list(self.completed_dir.glob("*.json")))


def process_job(job: Job, handler: Callable[[Job], None]) -> bool:
    """Run handler; return True on success, False on failure."""
    try:
        handler(job)
        return True
    except Exception:  # noqa: BLE001 — worker boundary catches all job failures
        return False


def run_worker(
    queue: FileJobQueue,
    handler: Callable[[Job], None],
    *,
    max_jobs: int = 10,
    max_attempts: int = 2,
) -> dict[str, int]:
    """Drain up to max_jobs from the queue, routing failures to DLQ."""
    processed = succeeded = failed = 0
    while processed < max_jobs:
        job = queue.dequeue()
        if job is None:
            break
        processed += 1
        job.attempts += 1
        if process_job(job, handler):
            queue.mark_completed(job)
            succeeded += 1
        elif job.attempts >= max_attempts:
            queue.move_to_dlq(job, reason="max_attempts_exceeded")
            failed += 1
        else:
            requeue = queue.enqueue(job.payload)
            requeue.attempts = job.attempts
            queue._job_path(queue.pending_dir, requeue.job_id).write_text(
                json.dumps(asdict(requeue)), encoding="utf-8"
            )
            queue._job_path(queue.processing_dir, job.job_id).unlink(missing_ok=True)
    return {"processed": processed, "succeeded": succeeded, "failed": failed}
