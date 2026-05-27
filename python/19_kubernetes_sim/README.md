# Step 27 — Kubernetes Simulator

Pod scheduling simulator with resource requests and node selectors (no real cluster).

## Run

```bash
./run.sh 27
./check.sh 27
```

## Key concepts

- **Requests:** CPU/memory the scheduler reserves
- **Pending pods:** no node satisfies constraints
- **Node selector:** pin workloads to labeled nodes

## Next

Step 28 records incident timelines in SQLite.
