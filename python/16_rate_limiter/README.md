# Step 20 — Rate Limiter

Token bucket rate limiting with FastAPI middleware returning HTTP 429.

## Run

```bash
./run.sh 20
./check.sh 20
```

## Files

| File | Purpose |
|------|---------|
| `lesson.py` | Production context and demo |
| `exercise.py` | Your implementation |
| `solution.py` | Token bucket + middleware |
| `test_lesson.py` | pytest |

## Key concepts

- **Token bucket:** burst capacity + steady refill rate
- **429 Too Many Requests:** signal clients to slow down
- **Middleware:** cross-cutting limit before route handlers run

## Next

Step 21 adds retry with backoff when downstream services flake.
