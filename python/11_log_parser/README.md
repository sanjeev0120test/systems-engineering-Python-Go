# Step 18 — Log Parser

Parse nginx-style access logs and compute SLI metrics.

## Goals

- Parse `sample_data/logs/access.log` (combined log format)
- Compute **error rate** (fraction of HTTP 5xx responses)
- Compute **p95 latency** in milliseconds
- Feed metrics into Step 19 alerting

## Run

```bash
./run.sh 18
./run.sh 18 exercise
./run.sh 18 solution
./check.sh 18
```

## Sample data expectations

The bundled `access.log` has 8 requests, 2 errors (500 + 503), error rate **0.25**, p95 latency **250 ms**.

## SRE context

Error rate and latency p95 are classic SLIs. Alert rules in Step 19 reference these metric names directly.
