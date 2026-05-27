"""Step 25 exercise — APScheduler cron-like jobs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable


@dataclass
class JobRunRecord:
    job_name: str
    run_count: int = 0
    last_run_at: datetime | None = None
    results: list[str] = field(default_factory=list)


class CronJobRunner:
    def __init__(self) -> None:
        raise NotImplementedError("Implement CronJobRunner")

    def register_job(
        self,
        name: str,
        func: Callable[[], str],
        *,
        minute: str = "*",
        second: str = "0",
    ) -> None:
        raise NotImplementedError("Implement register_job")

    def start(self) -> None:
        raise NotImplementedError("Implement start")

    def shutdown(self, wait: bool = False) -> None:
        raise NotImplementedError("Implement shutdown")

    def run_job_now(self, name: str) -> str:
        raise NotImplementedError("Implement run_job_now")


def run_once(func: Callable[[], str], *, job_name: str = "manual") -> JobRunRecord:
    raise NotImplementedError("Implement run_once")


def main() -> None:
    print("Implement scheduler, then run: ./check.sh 25")


if __name__ == "__main__":
    main()
