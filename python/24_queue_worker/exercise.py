"""Step 22 exercise — file-based queue, worker, and dead-letter queue."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class Job:
    job_id: str
    payload: dict[str, str]
    attempts: int = 0


class FileJobQueue:
    def __init__(self, base_dir: Path | None = None) -> None:
        raise NotImplementedError("Implement FileJobQueue")

    def enqueue(self, payload: dict[str, str]) -> Job:
        raise NotImplementedError("Implement enqueue")

    def dequeue(self) -> Job | None:
        raise NotImplementedError("Implement dequeue")

    def mark_completed(self, job: Job) -> None:
        raise NotImplementedError("Implement mark_completed")

    def move_to_dlq(self, job: Job, reason: str) -> None:
        raise NotImplementedError("Implement move_to_dlq")

    def pending_count(self) -> int:
        raise NotImplementedError("Implement pending_count")

    def dlq_count(self) -> int:
        raise NotImplementedError("Implement dlq_count")

    def completed_count(self) -> int:
        raise NotImplementedError("Implement completed_count")


def process_job(job: Job, handler: Callable[[Job], None]) -> bool:
    raise NotImplementedError("Implement process_job")


def run_worker(
    queue: FileJobQueue,
    handler: Callable[[Job], None],
    *,
    max_jobs: int = 10,
    max_attempts: int = 2,
) -> dict[str, int]:
    raise NotImplementedError("Implement run_worker")


def main() -> None:
    print("Implement queue worker, then run: ./check.sh 22")


if __name__ == "__main__":
    main()
