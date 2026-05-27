# Step 35 — Go worker pool

Process log lines concurrently with a fixed worker pool — a common pattern for shippers, parsers, and queue consumers.

## Topics

- Job and result channels
- Worker goroutines with `sync.WaitGroup`
- Parsing nginx-style access log lines

## Commands

```bash
./run.sh 35
./check.sh 35
```
