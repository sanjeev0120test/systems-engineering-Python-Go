# Step 5 — Exceptions

**Time:** ~20 minutes  
**Goal:** Parse messy service config safely using EAFP and LBYL patterns.

## Run

```bash
./run.sh 5
./run.sh 5 exercise
./check.sh 5
```

## EAFP vs LBYL

| Style | Python idiom | When |
|-------|--------------|------|
| EAFP | `try/except` | Expected failures (bad env vars) |
| LBYL | `if` guards | Cheap checks before expensive work |

## Real config reference

`sample_data/configs/service.yaml` — your parsers should tolerate partial/overridden values.

Pass `./check.sh 5` before Step 6.
