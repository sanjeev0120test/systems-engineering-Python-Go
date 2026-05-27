# Step 36 — Go log processor

Concurrently parse `sample_data/logs/access.log` and aggregate status and method counts.

## Topics

- Streaming file reads with `bufio.Scanner`
- Worker pool over real log data
- production-style error-rate summary (4xx/5xx lines)

## Commands

```bash
./run.sh 36
./check.sh 36
```

The program reads `../../sample_data/logs/access.log` relative to this directory.
