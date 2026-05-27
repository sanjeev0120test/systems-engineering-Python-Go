# Step 13 — Concurrency Overview

Understand CPython's GIL and when threads help (I/O) vs when they don't (CPU).

## Run

```bash
./run.sh 13
./check.sh 13
```

## Files

| File | Purpose |
|------|---------|
| `lesson.py` | Timing comparison demo |
| `exercise.py` | Your implementation |
| `solution.py` | Reference solution |
| `test_lesson.py` | pytest |

## Key concepts

- **GIL:** one thread executes Python bytecode at a time
- **CPU-bound:** use `multiprocessing` or native extensions
- **I/O-bound:** threads, asyncio, or async HTTP clients

## Java bridge

| Java | Python |
|------|--------|
| `ExecutorService` for I/O | `ThreadPoolExecutor` |
| Parallel streams / fork-join for CPU | `ProcessPoolExecutor` |
| CompletableFuture | `asyncio` (Step 15) |

## Next

Step 14 applies `ThreadPoolExecutor` to parallel health checks.
