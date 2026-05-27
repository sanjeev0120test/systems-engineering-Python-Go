# Step 22 — Queue Worker

File-based durable queue with workers and a dead-letter queue under `sample_data/output/`.

## Run

```bash
./run.sh 22
./check.sh 22
```

## Key concepts

- **Decoupling:** producers enqueue, workers consume at their pace
- **DLQ:** isolate poison pills without blocking the queue
- **Idempotency:** at-least-once delivery requires safe retries

## Next

Step 23 forwards HTTP through a reverse proxy simulator.
