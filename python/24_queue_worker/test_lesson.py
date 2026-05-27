"""Tests for Step 22 — file-based queue worker."""

from __future__ import annotations

from pathlib import Path

import pytest
from python.common import paths as paths_module
from python.common.paths import output_path, sample_data_path

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

@pytest.fixture
def queue(tmp_path: Path) -> FileJobQueue:
    base = tmp_path / "queue"
    return FileJobQueue(base)


def test_enqueue_dequeue_round_trip(queue: FileJobQueue) -> None:
    job = queue.enqueue({"task": "reindex"})
    assert queue.pending_count() == 1
    dequeued = queue.dequeue()
    assert dequeued is not None
    assert dequeued.job_id == job.job_id
    assert queue.pending_count() == 0


def test_worker_processes_successful_jobs(queue: FileJobQueue) -> None:
    queue.enqueue({"task": "ok"})
    queue.enqueue({"task": "ok2"})

    def handler(job: Job) -> None:
        assert "task" in job.payload

    stats = run_worker(queue, handler, max_jobs=5)
    assert stats["succeeded"] == 2
    assert queue.completed_count() == 2


def test_failed_jobs_land_in_dlq(queue: FileJobQueue) -> None:
    queue.enqueue({"task": "fail"})

    def handler(_job: Job) -> None:
        raise RuntimeError("boom")

    stats = run_worker(queue, handler, max_jobs=5, max_attempts=1)
    assert stats["failed"] == 1
    assert queue.dlq_count() == 1


def test_output_directory_under_sample_data(tmp_path: Path) -> None:
    from python.common.paths import output_path

    q = FileJobQueue(output_path("queue_worker_test"))
    q.enqueue({"task": "cleanup"})
    assert q.pending_count() == 1
    shutil.rmtree(q.pending_dir.parent, ignore_errors=True)

