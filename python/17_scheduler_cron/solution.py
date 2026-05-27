"""Step 25 solution — APScheduler cron-like recurring jobs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


@dataclass
class JobRunRecord:
    job_name: str
    run_count: int = 0
    last_run_at: datetime | None = None
    results: list[str] = field(default_factory=list)


class CronJobRunner:
    """Wrap APScheduler for testable cron-style jobs."""

    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()
        self.records: dict[str, JobRunRecord] = {}
        self._lock = Lock()

    def register_job(
        self,
        name: str,
        func: Callable[[], str],
        *,
        minute: str = "*",
        second: str = "0",
    ) -> None:
        record = JobRunRecord(job_name=name)
        self.records[name] = record

        def wrapped() -> None:
            result = func()
            with self._lock:
                record.run_count += 1
                record.last_run_at = datetime.now(timezone.utc)
                record.results.append(result)

        trigger = CronTrigger(minute=minute, second=second)
        self.scheduler.add_job(wrapped, trigger, id=name, replace_existing=True)

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self, wait: bool = False) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)

    def run_job_now(self, name: str) -> str:
        """Execute a registered job immediately (used in tests)."""
        job = self.scheduler.get_job(name)
        if job is None:
            raise KeyError(f"unknown job: {name}")
        job.func()
        record = self.records[name]
        return record.results[-1]


def run_once(func: Callable[[], str], *, job_name: str = "manual") -> JobRunRecord:
    """Run a single job synchronously without starting the scheduler."""
    record = JobRunRecord(job_name=job_name)
    result = func()
    record.run_count = 1
    record.last_run_at = datetime.now(timezone.utc)
    record.results.append(result)
    return record
