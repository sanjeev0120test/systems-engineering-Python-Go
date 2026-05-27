# Start Here — Systems Engineering Python Practice Lab

**You know Java. You are learning Python for systems engineering. Go comes last (Steps 32–36).**

Open this repo in Cursor → terminal **WSL (Ubuntu)** → follow steps in order.

> **Step number ≠ folder name.** Step 16 is in `python/13_health_checker/`. See [docs/STEP_INDEX.md](docs/STEP_INDEX.md).  
> **When finished:** read [GUIDE.md](GUIDE.md) for concepts, Java comparison, and use cases.

---

## Before Step 0

- [ ] Cursor opened on this folder
- [ ] Terminal profile: **WSL Ubuntu**
- [ ] Example path: `cd /mnt/c/dev/systems-engineering-Python-Go`

---

## Step 0 — One-time setup (~5 min)

```bash
chmod +x setup.sh run.sh check.sh
./setup.sh
./check.sh 0
```

**Expected:** `PASS: Step 0 complete`

---

## How every step works

1. Read the step **README** (path in [STEP_INDEX](docs/STEP_INDEX.md))
2. Run: `./run.sh N`
3. Practice: edit `exercise.py` → `./run.sh N exercise`
4. Compare: `solution.py`
5. Verify: `./check.sh N` → **PASS** before next step

---

## Step index

| Step | Topic | Run | Check |
|------|-------|-----|-------|
| 0 | Setup | `./setup.sh` | `./check.sh 0` |
| 1 | Variables & f-strings | `./run.sh 1` | `./check.sh 1` |
| 2 | Control flow | `./run.sh 2` | `./check.sh 2` |
| 3 | Functions | `./run.sh 3` | `./check.sh 3` |
| 4 | Classes & dataclasses | `./run.sh 4` | `./check.sh 4` |
| 5 | Exceptions | `./run.sh 5` | `./check.sh 5` |
| 6 | Typing | `./run.sh 6` | `./check.sh 6` |
| 7 | File handling | `./run.sh 7` | `./check.sh 7` |
| 8 | JSON & YAML | `./run.sh 8` | `./check.sh 8` |
| 9 | Logging (structured JSON) | `./run.sh 9` | `./check.sh 9` |
| 10 | Subprocess / Linux | `./run.sh 10` | `./check.sh 10` |
| 11 | REST client | `./run.sh 11` | `./check.sh 11` |
| 12 | FastAPI server | `./run.sh 12` | `./check.sh 12` |
| 13 | Concurrency overview | `./run.sh 13` | `./check.sh 13` |
| 14 | Threading | `./run.sh 14` | `./check.sh 14` |
| 15 | Asyncio | `./run.sh 15` | `./check.sh 15` |
| 16 | Health checker | `./run.sh 16` | `./check.sh 16` |
| 17 | Monitoring agent | `./run.sh 17` | `./check.sh 17` |
| 18 | Log parser | `./run.sh 18` | `./check.sh 18` |
| 19 | Alerting engine | `./run.sh 19` | `./check.sh 19` |
| 20 | Rate limiter | `./run.sh 20` | `./check.sh 20` |
| 21 | Retry & circuit breaker | `./run.sh 21` | `./check.sh 21` |
| 22 | Queue worker | `./run.sh 22` | `./check.sh 22` |
| 23 | Reverse proxy sim | `./run.sh 23` | `./check.sh 23` |
| 24 | Load balancer sim | `./run.sh 24` | `./check.sh 24` |
| 25 | Scheduler / cron | `./run.sh 25` | `./check.sh 25` |
| 26 | Config drift detector | `./run.sh 26` | `./check.sh 26` |
| 27 | Kubernetes scheduler sim | `./run.sh 27` | `./check.sh 27` |
| 28 | Incident simulator | `./run.sh 28` | `./check.sh 28` |
| 29 | Prometheus metrics exporter | `./run.sh 29` | `./check.sh 29` |
| 30 | Distributed systems basics | `./run.sh 30` | `./check.sh 30` |
| 31 | Platform capstone | `./run.sh 31` | `./check.sh 31` |
| 32 | Go basics | `./run.sh 32` | `./check.sh 32` |
| 33 | Go concurrency | `./run.sh 33` | `./check.sh 33` |
| 34 | Go HTTP server | `./run.sh 34` | `./check.sh 34` |
| 35 | Go worker pool | `./run.sh 35` | `./check.sh 35` |
| 36 | Go log processor | `./run.sh 36` | `./check.sh 36` |

**Run everything:** `./check.sh all`

---

## Docs

| Doc | When to read |
|-----|--------------|
| [docs/JAVA_TO_PYTHON.md](docs/JAVA_TO_PYTHON.md) | Anytime — Java bridge |
| [docs/STEP_INDEX.md](docs/STEP_INDEX.md) | When folder path is unclear |
| [docs/CONCURRENCY_DECISION_TREE.md](docs/CONCURRENCY_DECISION_TREE.md) | Steps 13–15 |
| [docs/SLO_SLI_GLOSSARY.md](docs/SLO_SLI_GLOSSARY.md) | Steps 18–19 |
| [GUIDE.md](GUIDE.md) | **After Step 31** — final summary |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3: not found` | `sudo apt install python3 python3-venv python3-pip` |
| `No module named pytest` | `./setup.sh` again |
| Step 10 fails on Windows | Use WSL terminal |
| Step 12 blocks terminal | Normal — server runs until Ctrl+C; use 2nd terminal for `./run.sh 11` |
| Step 12 shortcut | `./run.sh 12 server` runs `server.py` directly |
