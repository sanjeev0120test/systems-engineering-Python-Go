# Step 2 — Control flow

**Time:** ~20 minutes  
**Goal:** Use `if`, `for`, and `while` to filter unhealthy hosts and summarize fleet status.

## Run

```bash
./run.sh 2
./run.sh 2 exercise
./check.sh 2
```

## What you will learn

| Construct | Production use |
|-----------|---------|
| `if` / `elif` | Route alerts by severity |
| `for` | Iterate probe results |
| `while` | Scan until retry threshold exceeded |
| dict `.get()` | Safe access to optional host fields |

## Exercise checklist

1. `filter_unhealthy` — return hosts with `healthy is False`
2. `count_by_status` — tally by `status` field
3. `first_host_exceeding_retries` — while-loop scan
4. `summarize_fleet` — one-line dashboard string

Pass `./check.sh 2` before Step 3.
