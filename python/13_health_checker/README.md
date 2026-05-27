# Step 16 — Health Checker

Synthetic HTTP and TCP probes with retries — the foundation of uptime monitoring.

## Goals

- HTTP GET checks via `requests` with configurable retries
- TCP connect checks via `socket.create_connection`
- Load targets from `sample_data/configs/service.yaml`
- Write `sample_data/output/health_report.json`

## Run

```bash
./run.sh 16
./run.sh 16 exercise
./run.sh 16 solution
./check.sh 16
```

## Exercise

Implement `exercise.py` using:

- `load_service_config` from `python.common.config_loader`
- `sample_data_path` / `output_path` from `python.common.paths`
- `get_logger` / `new_trace_id` from `python.common.logging_setup`

## SRE context

Health checkers run on a schedule (cron, Kubernetes liveness probes, or agents). Retries distinguish transient network blips from real outages. JSON reports feed alerting (Step 19) and incident dashboards.
