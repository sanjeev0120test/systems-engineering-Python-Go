# Step 29 — Metrics Exporter

Prometheus metrics with `prometheus_client`; `./run.sh 29` serves `/metrics` on port 9100.

## Run

```bash
./run.sh 29
curl http://127.0.0.1:9100/metrics
./check.sh 29
```

## Key concepts

- **Counter / Gauge / Histogram:** core Prometheus types
- **RED metrics:** rate, errors, duration per endpoint
- **Cardinality:** keep label sets bounded

## Next

Step 30 simulates heartbeat-based leader election.
