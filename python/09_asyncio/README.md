# Step 15 — Asyncio

Async HTTP health polling with `asyncio` and `httpx.AsyncClient` — same I/O fan-out as Step 14, single-threaded event loop.

## Run

```bash
./run.sh 12    # optional
./run.sh 15
./check.sh 15
```

## Files

| File | Purpose |
|------|---------|
| `lesson.py` | Async poll demo |
| `exercise.py` | Your implementation |
| `solution.py` | Reference solution |
| `test_lesson.py` | pytest (includes async tests) |

## Key concepts

- `async def` / `await` coroutines
- `asyncio.gather()` for concurrent I/O
- `httpx.AsyncClient` for non-blocking HTTP
- `asyncio.run()` entry point from sync scripts

## Java bridge

| Java | Python |
|------|--------|
| CompletableFuture.allOf | asyncio.gather |
| Virtual threads (Project Loom) | asyncio (different model) |
| WebClient (Spring) | httpx.AsyncClient |

## Next

Step 16 builds a full health checker using these patterns.
