# Step 14 — Threading

Parallel HTTP health checks with `ThreadPoolExecutor` — the I/O-bound pattern from Step 13 applied to real probes.

## Run

```bash
./run.sh 12    # optional live server
./run.sh 14
./check.sh 14
```

## Files

| File | Purpose |
|------|---------|
| `lesson.py` | Parallel probe demo |
| `exercise.py` | Your implementation |
| `solution.py` | Reference solution |
| `test_lesson.py` | pytest |

## Key concepts

- `ThreadPoolExecutor(max_workers=N)`
- `as_completed()` for result collection
- Sort results for deterministic output

## Next

Step 15 replaces threads with `asyncio` + `httpx` for the same I/O pattern.
