# Step 6 — Typing

**Time:** ~25 minutes  
**Goal:** Use `TypedDict`, `Optional` (`T | None`), and `python.common.paths` for typed metrics.

## Run

```bash
./run.sh 6
./run.sh 6 exercise
./check.sh 6
```

## New imports (shared repo utilities)

```python
from python.common.paths import sample_data_path, REPO_ROOT
```

Step 6+ steps use `python.common` for paths, logging, and config — same layout as production services.

## Types covered

| Type | Purpose |
|------|---------|
| `HostMetric` (TypedDict) | JSON metric shape |
| `HostMetric \| None` | Optional parse result |
| `NotRequired[str]` | Optional timestamp field |

## Sample data

`sample_data/metrics/host_metrics.json` — loaded via `load_sample_host_metric()`.

Pass `./check.sh 6` before Step 7 (file handling).
