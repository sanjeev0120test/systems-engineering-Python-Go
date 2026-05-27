# Step 17 — Monitoring Agent

Poll CPU and memory, write snapshots for downstream alerting.

## Goals

- Collect host metrics with `psutil` (works on Linux, macOS, and Windows)
- Write `sample_data/metrics/latest.json` on each poll cycle
- Run continuously via `agent.py` (`./run.sh 17`)
- Graceful shutdown on Ctrl+C (SIGINT)
- Single-cycle mode for tests: `SRE_AGENT_ONCE=1 ./run.sh 17`

## Run

```bash
./run.sh 17                  # continuous polling (Ctrl+C to stop)
SRE_AGENT_ONCE=1 ./run.sh 17 # one snapshot then exit
./run.sh 17 lesson
./check.sh 17
```

## Exercise

Implement `exercise.py` using `python.common` paths, config, and logging helpers.

## SRE context

Node exporters and Datadog agents follow the same pattern: poll → write → scrape. The monitoring agent feeds Step 19 alerting via `latest.json` and `host_metrics.json`.
