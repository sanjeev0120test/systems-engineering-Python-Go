# Learning Guide — Read This Last

You finished (or skimmed) the lab. This page is the **short map**: why this repo exists, what you practiced, and how Python/Go relate to Java.

---

## Why this repo exists

You already know **Java**. This lab teaches **Python first** (90%), then **Go basics** (10%), using **real production-style problems** — health checks, logs, metrics, alerts, queues — that run **entirely on your machine** (no cloud account required).

Goal: go from **zero Python** to **confident automation and small services**, the way platform and backend teams actually work.

---

## How to use the repo (3 commands)

```bash
./setup.sh          # once
./run.sh N          # learn step N
./check.sh N        # verify before step N+1
```

Full step list: [START_HERE.md](START_HERE.md). Checklist: [ROADMAP.md](ROADMAP.md).

**Step number ≠ folder number.** Step 16 lives in `python/13_health_checker/` because folders follow *topic groups*, steps follow *learning order*. See [docs/STEP_INDEX.md](docs/STEP_INDEX.md).

---

## What each block teaches

| Steps | You build | Python concepts | Java bridge |
|-------|-----------|-----------------|-------------|
| 1–6 | Host parsing, inventory | variables, loops, functions, classes, exceptions, typing | like POJOs → `@dataclass`, `Optional` → `\| None` |
| 7–9 | Log + config files | `with open`, JSON/YAML, structured logging | try-with-resources → `with`, SLF4J → `logging` |
| 10 | Shell automation | `subprocess`, timeouts, exit codes | `ProcessBuilder` → `subprocess.run` |
| 11–12 | HTTP client + server | `requests`, FastAPI, uvicorn | RestTemplate → `requests`, Spring → FastAPI |
| 13–15 | Parallel checks | GIL, threads, asyncio | `ExecutorService` → thread pool / async |
| 16–19 | Health → metrics → logs → alerts | SQLite, retries, rule engine | mini observability pipeline |
| 20–22 | Rate limit, circuit breaker, queue | middleware, backoff, worker pool | resilience patterns |
| 23–31 | Proxy, LB, scheduler, K8s sim, capstone | platform simulations | how pieces fit together |
| 32–36 | Go tools | goroutines, channels, HTTP, workers | when Go beats Python for infra |

---

## Major Python concepts (by the end)

| Concept | Where you used it |
|---------|-------------------|
| Virtual env + imports | Step 0, every module |
| Type hints | Steps 1, 6, all solutions |
| Context managers | Step 7 file I/O |
| Config from env + YAML | Steps 8, 26 (`LAB_*` prefix) |
| Structured JSON logs | Step 9+ (`trace_id`) |
| Subprocess safety | Step 10 |
| HTTP client/server | Steps 11–12 |
| Concurrency choice | Steps 13–15 (CPU vs I/O) |
| Production mini-systems | Steps 16–31 |

---

## Go concepts (Steps 32–36)

| Concept | Why it matters |
|---------|----------------|
| Structs + errors | Explicit types; no exceptions |
| Goroutines + channels | Cheap parallelism (K8s/Docker tooling uses Go) |
| `net/http` | Small binary HTTP services |
| Worker pools | Same pattern as Python Step 22, faster for CPU |

**When to pick Go over Python:** long-running agents, high concurrency, single binary deploy. **When to pick Python:** glue scripts, APIs, data parsing, fast iteration.

---

## Java → Python → Go (cheat sheet)

| Idea | Java | Python (this lab) | Go (Steps 32–36) |
|------|------|-------------------|------------------|
| Entry point | `main()` | `if __name__ == "__main__"` | `func main()` |
| Types | compile-time | hints + runtime | compile-time |
| Null | `null` | `None` | `nil` |
| Errors | exceptions | `try/except` | `(value, error)` |
| Modules | JAR/Maven | venv + pip | go.mod |
| Web API | Spring | FastAPI | net/http |
| Parallelism | threads | threads/async (GIL!) | goroutines |

More detail: [docs/JAVA_TO_PYTHON.md](docs/JAVA_TO_PYTHON.md)

---

## Use cases you can now explain (interviews & work)

1. **Synthetic health checks** — HTTP/TCP probes, retries, JSON reports (Step 16)
2. **Structured logging** — JSON lines with correlation IDs for search (Step 9)
3. **Log SLIs** — error rate and p95 latency from access logs (Step 18)
4. **Alert deduplication** — rules + SQLite so pages do not storm (Step 19)
5. **Rate limiting** — token bucket protecting APIs (Step 20)
6. **Circuit breaker** — stop calling a failing dependency (Step 21)
7. **Background jobs** — file queue + workers + dead-letter queue (Step 22)
8. **Metrics endpoint** — Prometheus-style `/metrics` on localhost (Step 29)
9. **Config drift** — compare YAML snapshots over time (Step 26)
10. **Mini deploy pipeline** — lint → test → deploy simulation (Step 31)

---

## Files worth bookmarking

| File | Purpose |
|------|---------|
| [START_HERE.md](START_HERE.md) | Day-one walkthrough |
| [docs/STEP_INDEX.md](docs/STEP_INDEX.md) | Step number → folder path |
| [docs/CONCURRENCY_DECISION_TREE.md](docs/CONCURRENCY_DECISION_TREE.md) | threads vs asyncio vs processes |
| [docs/SLO_SLI_GLOSSARY.md](docs/SLO_SLI_GLOSSARY.md) | error budgets, SLIs |
| [python/common/](python/common/) | logging, config, paths reused everywhere |

---

## Keep practicing

1. Re-do **exercise.py** files without looking at **solution.py**.
2. Change alert thresholds in `sample_data/alerts/rules.yaml` and re-run Step 19.
3. Add a new health endpoint in Step 12 and poll it from Step 11.
4. Complete Go Steps 32–36 in WSL after Python feels comfortable.

When `./check.sh all` passes in WSL, you have a complete local lab — **zero to hero**, on your machine, at your pace.
