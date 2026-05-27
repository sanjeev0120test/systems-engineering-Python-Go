# Step 21 — Retry and Circuit Breaker

Exponential backoff retries and a three-state circuit breaker on a flaky mock service.

## Run

```bash
./run.sh 21
./check.sh 21
```

## Key concepts

- **Exponential backoff:** 1s, 2s, 4s… capped with optional jitter
- **Circuit breaker:** closed → open (fast fail) → half-open (probe) → closed
- **Retry storms:** unbounded retries amplify outages

## Next

Step 22 decouples work with a file-based job queue and dead-letter queue.
