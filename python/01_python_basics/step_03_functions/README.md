# Step 3 — Functions

**Time:** ~20 minutes  
**Goal:** Write reusable functions with default arguments for disk threshold alerting.

## Run

```bash
./run.sh 3
./run.sh 3 exercise
./check.sh 3
```

## Key functions

| Function | Purpose |
|----------|---------|
| `is_disk_critical` | Boolean threshold check |
| `summarize_disk_alert` | Human-readable alert or `None` |
| `evaluate_hosts_disk` | Batch evaluation across fleet |
| `disk_status_label` | Dashboard label: ok / warn / critical |

## Java note

Python default args (`threshold: float = 90.0`) replace many overload variants.
Keep thresholds as parameters — hard-coding 90 in five scripts causes on-call pain.

Pass `./check.sh 3` before Step 4.
