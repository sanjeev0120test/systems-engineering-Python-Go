# Step 26 — Config Management

YAML snapshot diffing to detect configuration drift.

## Run

```bash
./run.sh 26
./check.sh 26
```

## Key concepts

- **Desired state:** Git-backed YAML snapshots
- **Drift:** runtime config differs from baseline
- **Reports:** write findings to `sample_data/output/`

## Next

Step 27 simulates Kubernetes pod scheduling without a real cluster.
