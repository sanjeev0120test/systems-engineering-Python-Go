# Step 25 — Scheduler / Cron

APScheduler cron-like recurring jobs with synchronous test hooks.

## Run

```bash
./run.sh 25
./check.sh 25
```

## Key concepts

- **Cron triggers:** minute/hour/day scheduling
- **run_job_now:** test without waiting for wall clock
- **Missed runs:** alert when last_success is stale

## Next

Step 26 detects configuration drift via YAML snapshot diffs.
