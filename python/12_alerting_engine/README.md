# Step 19 — Alerting Engine

Evaluate YAML alert rules against metrics and deduplicate in SQLite.

## Goals

- Load rules from `sample_data/alerts/rules.yaml`
- Merge `host_metrics.json` with Step 18 log-parser SLIs
- Fire alerts when thresholds are breached
- Persist to `sample_data/output/alerts.db` with deduplication

## Run

```bash
./run.sh 19
./run.sh 19 exercise
./run.sh 19 solution
./check.sh 19
```

## Bundled rules

| Rule | Metric | Threshold |
|------|--------|-----------|
| high_error_rate | error_rate | > 0.05 |
| high_latency_p95 | latency_p95_ms | > 200 |
| disk_usage_high | disk_percent | > 85 |

Sample data triggers **high_error_rate** (0.25) and **high_latency_p95** (250 ms).

## Production context

Dedup keys prevent paging on-call every 30 seconds for the same incident. Production systems use similar logic in Alertmanager, PagerDuty, or Opsgenie.
