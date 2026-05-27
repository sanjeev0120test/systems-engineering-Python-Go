"""Step 13 — Concurrency: GIL, CPU-bound vs I/O-bound in CPython."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (SRE) ---
# Health checks and log shipping are I/O-bound (HTTP, disk, network).
# Log parsing at scale can be CPU-bound — threads won't help; use multiprocessing
# or push work to Go/Rust sidecars.

# --- Java developer note ---
# Java threads run bytecode in parallel on multiple cores. CPython's GIL allows
# only one thread to execute Python bytecode at a time — threads still help for I/O.

# --- How to run ---
# ./run.sh 13
# ./check.sh 13


def main() -> None:
    from solution import compare_concurrency_models

    results = compare_concurrency_models()
    cpu_seq = results["cpu_sequential"]["elapsed_s"]
    cpu_thr = results["cpu_threaded"]["elapsed_s"]
    io_thr = results["io_threaded"]["elapsed_s"]

    logger.info("CPU sequential: %.4fs", cpu_seq)
    logger.info("CPU threaded:   %.4fs (GIL — often similar to sequential)", cpu_thr)
    logger.info("I/O threaded:   %.4fs (parallel waits — faster than 4× delay)", io_thr)

    logger.info(
        "Rule of thumb: threads for I/O, ProcessPoolExecutor/multiprocessing for CPU."
    )


if __name__ == "__main__":
    main()
