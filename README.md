# systems-engineering-Python-Go

**Local Python and Go practice lab for Java developers.**  
Python-first (Steps 1–31). Go basics last (Steps 32–36). Everything runs on your machine — no cloud.

## Start in 60 seconds

```bash
./setup.sh && ./check.sh 0    # once — must print PASS
./run.sh 1                    # learn
./check.sh 1                  # verify before next step
```

Windows: `.\setup.ps1` → `.\check.ps1 0` → `.\run.ps1 1` → `.\check.ps1 1`

**Every step is the same:** read `lesson.py` output → edit `exercise.py` → compare `solution.py` → `./check.sh N` must PASS.

## Critical concepts only (what this lab covers)

| Area | Steps | Production skill |
|------|-------|------------------|
| Python basics | 1–6 | types, functions, classes, errors (Java → Python) |
| Files & config | 7–9 | logs, YAML/JSON, structured logging with `trace_id` |
| Automation | 10 | subprocess with timeouts (replace brittle bash) |
| HTTP | 11–12 | health client + FastAPI server |
| Concurrency | 13–15 | when to use threads vs asyncio (GIL trap for Java devs) |
| Observability | 16–19 | health checks → metrics → log SLIs → alerts |
| Reliability | 20–22 | rate limit, circuit breaker, job queue |
| Platform sims | 23–31 | proxy, LB, scheduler, metrics, capstone pipeline |
| Go basics | 32–36 | syntax, goroutines, HTTP, workers, log parser |

You already know Java. Each `lesson.py` has Java comparisons in comments — this README is your map.

---

## Table of contents

1. [Quick start](#quick-start)
2. [How every step works](#how-every-step-works)
3. [Repository layout](#repository-layout)
4. [Shared code (`python/common/`)](#shared-code-pythoncommon)
5. [Prerequisites and setup (Step 0)](#prerequisites-and-setup-step-0)
6. [Commands reference](#commands-reference)
7. [Full step index (0–36)](#full-step-index-036)
8. [Step-by-step concepts (Java → Python → files)](#step-by-step-concepts-java--python--files)
9. [What each block teaches](#what-each-block-teaches)
10. [Java to Python cheat sheet](#java-to-python-cheat-sheet)
11. [Concurrency: threads vs asyncio vs Go](#concurrency-threads-vs-asyncio-vs-go)
12. [SLI, SLO, and error budgets](#sli-slo-and-error-budgets)
13. [Go steps (Java → Go → files)](#go-steps-java--go--files)
14. [Java → Python → Go comparison](#java--python--go-comparison)
15. [Real-world use cases](#real-world-use-cases)
16. [Repository conventions](#repository-conventions)
17. [Troubleshooting](#troubleshooting)
18. [Keep practicing](#keep-practicing)

---

## Quick start

### WSL Ubuntu (recommended — full path including Go)

```bash
cd /mnt/c/dev/systems-engineering-Python-Go
chmod +x setup.sh run.sh check.sh
./setup.sh
./check.sh 0          # must print PASS
./run.sh 1
./check.sh 1
```

Follow [Full step index](#full-step-index-036) in order. Do not skip steps.

### Windows PowerShell (Python Steps 1–31 only)

```powershell
cd C:\dev\systems-engineering-Python-Go
.\setup.ps1
.\check.ps1 0         # must print PASS
.\run.ps1 1
.\check.ps1 1
```

For Linux subprocess modules (Step 10+) and Go (Steps 32–36), switch to WSL and use `./setup.sh` / `./run.sh` / `./check.sh`.

---

## How every step works

Every Python step folder contains the same four files:

```text
lesson.py      # run first — commented walkthrough with Java notes
exercise.py    # your TODOs — edit and practice
solution.py    # reference answer (tests import this)
test_lesson.py # automated checks
```

**Workflow for each step N:**

1. Run `./run.sh N` (or `.\run.ps1 N`) — read the lesson output
2. Edit `exercise.py` → `./run.sh N exercise`
3. Compare with `solution.py`
4. Run `./check.sh N` (or `.\check.ps1 N`) — must show **PASS** before Step N+1

> **Important:** Step number ≠ folder name. Step 16 lives in `python/13_health_checker/` because folders group topics; steps follow learning order. See the [step index table](#full-step-index-036).

---

## Repository layout

```text
systems-engineering-Python-Go/
├── README.md                 # full guide (this file)
├── setup.sh / setup.ps1      # Step 0 — create .venv, install deps
├── run.sh / run.ps1          # run any step lesson/exercise/solution
├── check.sh / check.ps1      # verify step (pytest + PASS/FAIL)
├── requirements.txt          # Python dependencies
├── python/
│   ├── common/               # shared helpers (logging, config, paths)
│   ├── step_loader.py        # test helper — loads solution.py safely
│   ├── 01_python_basics/     # Steps 1–6 (micro-folders step_01_…)
│   ├── 02_file_handling/     # Step 7
│   ├── …                     # one folder per topic (see step index)
│   └── 25_mini_platform_engineering/  # Step 31 capstone
├── go/
│   ├── 01_go_basics/         # Step 32
│   └── 05_log_processor/     # Step 36
└── sample_data/              # logs, configs, metrics, alert rules (local inputs)
    └── output/               # runtime files (gitignored)
```

Every Python step folder has the **same four files**: `lesson.py`, `exercise.py`, `solution.py`, `test_lesson.py`.

---

## Shared code (`python/common/`)

Read these once — every later step imports them.

| File | What it does | Java equivalent | Used from |
|------|--------------|-----------------|-----------|
| `paths.py` | `sample_data_path()`, `output_path()` — stable file paths | `Paths.get("sample_data/...")` + project root discovery | Steps 7+ |
| `logging_setup.py` | `get_logger()`, `JsonFormatter`, `new_trace_id()` | SLF4J + Logback JSON + MDC trace ID | Step 9+ |
| `config_loader.py` | `load_yaml()`, `load_service_config()` with `LAB_*` env override | `@ConfigurationProperties` + env vars | Steps 8, 16, 17, 26 |

Example (paths — like a small utility class):

```python
from python.common.paths import sample_data_path, output_path

log_file = sample_data_path("logs", "access.log")   # input — in git
report = output_path("health_report.json")           # output — gitignored
```

Example (logging — like SLF4J with structured fields):

```python
from python.common.logging_setup import get_logger, new_trace_id

logger = get_logger("health_checker", json_logs=True)
trace_id = new_trace_id()
logger.info("probe ok", extra={"trace_id": trace_id, "service": "payment-api"})
```

Example (config — like Spring externalized config):

```python
from python.common.config_loader import load_service_config
from python.common.paths import sample_data_path

config = load_service_config(sample_data_path("configs", "service.yaml"))
# LAB_ENVIRONMENT=prod overrides YAML value when set
```

---

## Prerequisites and setup (Step 0)

| Tool | Required for | Install |
|------|--------------|---------|
| Python 3.11+ | All steps | [python.org](https://www.python.org/downloads/) or `sudo apt install python3 python3-venv python3-pip` |
| WSL2 Ubuntu | Steps 10, 32–36 | `wsl --install` then Ubuntu |
| Go 1.22+ | Steps 32–36 only | [go.dev/dl](https://go.dev/dl/) inside WSL |

**Step 0 — one-time setup:**

```bash
./setup.sh
./check.sh 0
```

**Expected output:** `PASS: Step 0 complete`

Dependencies install automatically from `requirements.txt` into a local `.venv`:

```text
pytest, fastapi, uvicorn, requests, httpx, pyyaml,
prometheus-client, apscheduler, psutil, black, ruff, mypy
```

Environment variables use the **`LAB_` prefix** (e.g. `LAB_ENVIRONMENT=prod`, `LAB_CHECK_INTERVAL_SECONDS=30`).

---

## Commands reference

| Command | Action |
|---------|--------|
| `./setup.sh` or `.\setup.ps1` | Create `.venv`, install deps (once) |
| `./run.sh N` or `.\run.ps1 N` | Run step N lesson |
| `./run.sh N exercise` | Run your practice file |
| `./run.sh N solution` | Run reference solution |
| `./run.sh 12 server` | Run FastAPI server (Step 12) |
| `./check.sh N` or `.\check.ps1 N` | Verify step N |
| `./check.sh all` or `.\check.ps1 all` | Full Python test suite |
| `python scripts/validate_all.py` | Maintainer cross-check |

---

## Full step index (0–36)

| Step | Topic | Folder path | Run | Check |
|------|-------|-------------|-----|-------|
| 0 | Setup | repo root | `./setup.sh` | `./check.sh 0` |
| 1 | Variables & f-strings | `python/01_python_basics/step_01_variables/` | `./run.sh 1` | `./check.sh 1` |
| 2 | Control flow | `python/01_python_basics/step_02_control_flow/` | `./run.sh 2` | `./check.sh 2` |
| 3 | Functions | `python/01_python_basics/step_03_functions/` | `./run.sh 3` | `./check.sh 3` |
| 4 | Classes & dataclasses | `python/01_python_basics/step_04_classes/` | `./run.sh 4` | `./check.sh 4` |
| 5 | Exceptions | `python/01_python_basics/step_05_exceptions/` | `./run.sh 5` | `./check.sh 5` |
| 6 | Typing | `python/01_python_basics/step_06_typing/` | `./run.sh 6` | `./check.sh 6` |
| 7 | File handling | `python/02_file_handling/` | `./run.sh 7` | `./check.sh 7` |
| 8 | JSON & YAML | `python/03_json_yaml/` | `./run.sh 8` | `./check.sh 8` |
| 9 | Structured logging | `python/04_logging/` | `./run.sh 9` | `./check.sh 9` |
| 10 | Subprocess / Linux | `python/05_subprocess_linux/` | `./run.sh 10` | `./check.sh 10` |
| 11 | REST client | `python/06_rest_api/client/` | `./run.sh 11` | `./check.sh 11` |
| 12 | FastAPI server | `python/06_rest_api/server/` | `./run.sh 12` | `./check.sh 12` |
| 13 | Concurrency overview | `python/07_concurrency/` | `./run.sh 13` | `./check.sh 13` |
| 14 | Threading | `python/08_threading/` | `./run.sh 14` | `./check.sh 14` |
| 15 | Asyncio | `python/09_asyncio/` | `./run.sh 15` | `./check.sh 15` |
| 16 | Health checker | `python/13_health_checker/` | `./run.sh 16` | `./check.sh 16` |
| 17 | Monitoring agent | `python/10_monitoring_agent/` | `./run.sh 17` | `./check.sh 17` |
| 18 | Log parser | `python/11_log_parser/` | `./run.sh 18` | `./check.sh 18` |
| 19 | Alerting engine | `python/12_alerting_engine/` | `./run.sh 19` | `./check.sh 19` |
| 20 | Rate limiter | `python/16_rate_limiter/` | `./run.sh 20` | `./check.sh 20` |
| 21 | Retry & circuit breaker | `python/23_retry_circuit_breaker/` | `./run.sh 21` | `./check.sh 21` |
| 22 | Queue worker | `python/24_queue_worker/` | `./run.sh 22` | `./check.sh 22` |
| 23 | Reverse proxy sim | `python/14_reverse_proxy_sim/` | `./run.sh 23` | `./check.sh 23` |
| 24 | Load balancer sim | `python/15_load_balancer_sim/` | `./run.sh 24` | `./check.sh 24` |
| 25 | Scheduler / cron | `python/17_scheduler_cron/` | `./run.sh 25` | `./check.sh 25` |
| 26 | Config drift detector | `python/18_config_management/` | `./run.sh 26` | `./check.sh 26` |
| 27 | Kubernetes scheduler sim | `python/19_kubernetes_sim/` | `./run.sh 27` | `./check.sh 27` |
| 28 | Incident simulator | `python/20_incident_simulator/` | `./run.sh 28` | `./check.sh 28` |
| 29 | Prometheus metrics | `python/21_metrics_exporter/` | `./run.sh 29` | `./check.sh 29` |
| 30 | Distributed systems | `python/22_distributed_system_basics/` | `./run.sh 30` | `./check.sh 30` |
| 31 | Platform capstone | `python/25_mini_platform_engineering/` | `./run.sh 31` | `./check.sh 31` |
| 32 | Go basics | `go/01_go_basics/` | `./run.sh 32` | `./check.sh 32` |
| 33 | Go concurrency | `go/02_concurrency/` | `./run.sh 33` | `./check.sh 33` |
| 34 | Go HTTP server | `go/03_http_server/` | `./run.sh 34` | `./check.sh 34` |
| 35 | Go worker pool | `go/04_worker_pool/` | `./run.sh 35` | `./check.sh 35` |
| 36 | Go log processor | `go/05_log_processor/` | `./run.sh 36` | `./check.sh 36` |

**Final verification:** `./check.sh all` (WSL, with Go installed for Steps 32–36)

---

## Step-by-step concepts (Java → Python → files)

How each step maps from Java thinking to Python code **in this repo**. Open `lesson.py` first, then `solution.py`.

### Steps 1–6 — Python foundations

| Step | Concept | Java way | Python in this repo | Key files |
|------|---------|----------|---------------------|-----------|
| 1 | Variables, f-strings, parsing | `String.format`, `URI.getHost()` | `hostname: str`, f-strings, `urlparse()` | `step_01_variables/solution.py` — `parse_hostname_from_url()` |
| 2 | if/for/while, truthiness | `if (x != null)` | `if x:` (empty string/list is falsy) | `step_02_control_flow/solution.py` — `classify_status_code()` |
| 3 | Functions, defaults | method overloads (not in Java cleanly) | default args, `*args`, return tuples | `step_03_functions/solution.py` — `build_probe_url()` |
| 4 | Classes, dataclasses | POJO / Lombok `@Data` | `@dataclass` — auto `__init__`, `__repr__` | `step_04_classes/solution.py` — `Server`, `build_inventory()` |
| 5 | Exceptions | `try/catch`, checked exceptions | `try/except`, no checked exceptions | `step_05_exceptions/solution.py` — `safe_divide()` |
| 6 | Type hints | compile-time types | `list[str]`, `dict[str, Any]`, `TypedDict` | `step_06_typing/solution.py` — `HostMetric` typed dict |

**Java → Python mindset:** Java enforces types at compile time. Python uses hints for readability; runtime stays flexible. Prefer explicit return types on public functions — same discipline as Java interfaces.

### Steps 7–9 — Files, config, logging

| Step | Concept | Java way | Python in this repo | Key files |
|------|---------|----------|---------------------|-----------|
| 7 | File I/O | try-with-resources `BufferedReader` | `with open(path) as f:` | `02_file_handling/solution.py` — `read_log_lines()` |
| 8 | JSON & YAML | Jackson / SnakeYAML | `json.load`, `yaml.safe_load` | `03_json_yaml/solution.py` — `load_service_config()` |
| 9 | Structured logging | SLF4J + JSON appender | `logging` + `JsonFormatter` + `trace_id` | `04_logging/lesson.py`, `common/logging_setup.py` |

**Production rule:** Never `print()` in tools — use `logger.info(..., extra={"trace_id": ...})` so log aggregators can search by correlation ID.

### Steps 10–12 — Automation and HTTP

| Step | Concept | Java way | Python in this repo | Key files |
|------|---------|----------|---------------------|-----------|
| 10 | Subprocess | `ProcessBuilder`, exit codes | `subprocess.run(..., timeout=30)` | `05_subprocess_linux/solution.py` — `run_command()` |
| 11 | HTTP client | RestTemplate / WebClient | `requests.Session` + retry loop | `06_rest_api/client/solution.py` — `poll_health()` |
| 12 | HTTP server | Spring `@RestController` | FastAPI `@app.get("/health")` | `06_rest_api/server/solution.py`, `server.py` |

**Step 12 tip:** `./run.sh 12` runs the lesson. `./run.sh 12 server` starts uvicorn. Use a second terminal for `./run.sh 11` to poll it.

### Steps 13–15 — Concurrency (critical for Java devs)

| Step | Concept | Java way | Python in this repo | Key files |
|------|---------|----------|---------------------|-----------|
| 13 | When to parallelize | `ExecutorService` | GIL explained — threads ≠ CPU parallelism | `07_concurrency/solution.py` |
| 14 | Threading for I/O | `ExecutorService.submit()` | `ThreadPoolExecutor` | `08_threading/solution.py` — `parallel_health_checks()` |
| 15 | Async I/O | CompletableFuture / reactive | `asyncio.gather()` | `09_asyncio/solution.py` — async health polls |

**Java trap:** In Java, more threads often means more CPU throughput. In Python, the GIL limits CPU work in threads — use threads/async for **I/O waits** (HTTP, disk), not heavy parsing.

### Steps 16–19 — Observability chain (production core)

These four steps connect like a real on-call pipeline:

```text
Step 16 health_checker  →  probe URLs/TCP, write health_report.json
Step 17 monitoring_agent →  collect host metrics to sample_data/metrics/
Step 18 log_parser       →  compute error_rate, latency_p95_ms from access.log
Step 19 alerting_engine  →  evaluate rules.yaml, dedupe alerts in SQLite
```

| Step | Concept | Java analogy | Python in this repo | Key files |
|------|---------|--------------|---------------------|-----------|
| 16 | Synthetic monitoring | Micrometer health indicators | `requests.get` + retries | `13_health_checker/solution.py` — `check_http()`, `run_health_checks()` |
| 17 | Metrics collection | JMX / agent polling | read CPU/mem, write JSON | `10_monitoring_agent/solution.py` — `collect_metrics()` |
| 18 | Log-based SLIs | log analysis job | regex parse access log | `11_log_parser/solution.py` — `analyze_access_log()` |
| 19 | Alerting + dedup | Alertmanager rules | YAML rules + SQLite `INSERT OR IGNORE` | `12_alerting_engine/solution.py` — `run_alerting()` |

### Steps 20–22 — Reliability patterns

| Step | Concept | Java / resilience libs | Python in this repo | Key files |
|------|---------|------------------------|---------------------|-----------|
| 20 | Rate limiting | Bucket4j, gateway filters | token bucket middleware | `16_rate_limiter/solution.py` — `TokenBucket` |
| 21 | Retry + circuit breaker | Resilience4j | exponential backoff + breaker state | `23_retry_circuit_breaker/solution.py` — `CircuitBreaker` |
| 22 | Background jobs | JMS / SQS worker | file queue + worker + DLQ | `24_queue_worker/solution.py` — `FileJobQueue`, `run_worker()` |

### Steps 23–31 — Platform simulations

| Step | Topic | What you learn | Key file |
|------|-------|----------------|----------|
| 23 | Reverse proxy | forward HTTP, strip hop-by-hop headers | `14_reverse_proxy_sim/solution.py` |
| 24 | Load balancer | round-robin across backends | `15_load_balancer_sim/solution.py` |
| 25 | Scheduler | cron-like job runner | `17_scheduler_cron/solution.py` |
| 26 | Config drift | compare YAML snapshots | `18_config_management/solution.py` |
| 27 | K8s scheduler sim | pod → node placement | `19_kubernetes_sim/solution.py` |
| 28 | Incident timeline | SQLite incident store | `20_incident_simulator/solution.py` |
| 29 | Prometheus metrics | `/metrics` endpoint | `21_metrics_exporter/solution.py` |
| 30 | Distributed basics | leader election sim | `22_distributed_system_basics/solution.py` |
| 31 | Capstone | lint → test → deploy pipeline | `25_mini_platform_engineering/solution.py` |

---

## What each block teaches

| Steps | You build | Python concepts | Java bridge |
|-------|-----------|-----------------|-------------|
| 1–6 | Host parsing, inventory | variables, loops, functions, classes, exceptions, typing | POJOs → `@dataclass`, `Optional` → `\| None` |
| 7–9 | Log and config files | `with open`, JSON/YAML, structured logging | try-with-resources → `with`, SLF4J → `logging` |
| 10 | Shell automation | `subprocess`, timeouts, exit codes | `ProcessBuilder` → `subprocess.run` |
| 11–12 | HTTP client and server | `requests`, FastAPI, uvicorn | RestTemplate → `requests`, Spring → FastAPI |
| 13–15 | Parallel checks | GIL, threads, asyncio | `ExecutorService` → thread pool / async |
| 16–19 | Health → metrics → logs → alerts | SQLite, retries, rule engine | mini observability pipeline |
| 20–22 | Rate limit, circuit breaker, queue | middleware, backoff, worker pool | resilience patterns |
| 23–31 | Proxy, LB, scheduler, K8s sim, capstone | platform simulations | how pieces fit together |
| 32–36 | Go tools | goroutines, channels, HTTP, workers | when Go beats Python for infra |

### Major Python concepts by the end

| Concept | Where you used it |
|---------|-------------------|
| Virtual env and imports | Step 0, every module |
| Type hints | Steps 1, 6, all solutions |
| Context managers | Step 7 file I/O |
| Config from env and YAML | Steps 8, 26 (`LAB_*` prefix) |
| Structured JSON logs | Step 9+ (`trace_id`) |
| Subprocess safety | Step 10 |
| HTTP client/server | Steps 11–12 |
| Concurrency choice | Steps 13–15 (CPU vs I/O) |
| Production mini-systems | Steps 16–31 |

---

## Java to Python cheat sheet

| Java | Python | Notes |
|------|--------|-------|
| `public static void main` | `if __name__ == "__main__":` | Script entry point |
| `String s = "x"` | `s: str = "x"` | Type hints optional at runtime |
| `null` | `None` | Use `Optional[T]` or `T \| None` |
| `try/catch` | `try/except` | Python prefers EAFP over LBYL |
| `try-with-resources` | `with open(...) as f:` | Context managers |
| `List<String>` | `list[str]` | Lowercase generics (3.9+) |
| `Map<K,V>` | `dict[K, V]` | |
| `interface` | duck typing / `Protocol` | No formal interface required |
| `ExecutorService` | `ThreadPoolExecutor`, `asyncio` | GIL limits CPU threading |
| Maven/Gradle deps | `venv` + `pip install -r requirements.txt` | One venv per project |
| SLF4J + Logback | `logging` + JSON formatter | Step 9 |
| Spring `@RestController` | FastAPI `@app.get` | Lighter, async-native |
| `String.format` | f-strings `f"{x}"` | Preferred in modern Python |
| checked exceptions | none | Document in docstrings instead |

### Production engineering mindset shift

- **Automation:** Python replaces bash for anything with logic branches or JSON output.
- **Observability:** Always log with `trace_id`; avoid bare `print()` in tools.
- **Reliability:** Timeouts on every network/subprocess call; retries with backoff.
- **Config:** 12-factor — env vars override YAML files.

---

## Concurrency: threads vs asyncio vs Go

```text
CPU-bound work (parse huge logs, crypto, compression)
  → multiprocessing (bypass GIL) OR external worker service

I/O-bound sync (requests, subprocess, file reads)
  → threading OR asyncio (asyncio scales better at high concurrency)

Simple parallel host checks (few targets)
  → ThreadPoolExecutor (Step 14) — easy to reason about

Many concurrent HTTP probes (100+ endpoints)
  → asyncio pattern (Step 15)

Go infrastructure tools (K8s, Docker, Prometheus)
  → native goroutines — Steps 32–36
```

**Java developer trap:** Java threads help CPU parallelism. Python threads **do not** for CPU-heavy work due to the GIL. Use processes or Go for CPU-heavy pipelines.

---

## SLI, SLO, and error budgets

| Term | Meaning | In this repo |
|------|---------|--------------|
| **SLI** | Service Level Indicator — a measurable signal | `error_rate`, `latency_p95_ms` from Step 18 |
| **SLO** | Service Level Objective — target for an SLI | Alert thresholds in `sample_data/alerts/rules.yaml` |
| **SLA** | Contract with customers (often 99.9% uptime) | Interview and work discussions |
| **Error budget** | Allowed unreliability before feature freeze | If error_rate > 0.05, budget burning (Step 19) |
| **Golden signals** | Latency, traffic, errors, saturation | Steps 17–19 simulate these |

**Production notes:**
- SLOs should be user-journey based (checkout success), not server CPU alone.
- Multi-window burn alerts catch fast and slow budget consumption.
- Error budgets align product and engineering: when budget is gone, stop risky releases.

---

## Go steps (Java → Go → files)

Run in **WSL**: `./run.sh 32` … `./run.sh 36`. Each folder has `main.go`, `main_test.go`, `go.mod`.

| Step | Concept | Java way | Go in this repo | Key files |
|------|---------|----------|-----------------|-------------|
| 32 | Syntax, structs, errors | classes + exceptions | struct + `(value, error)` return | `go/01_go_basics/main.go` — `User`, `Divide()` |
| 33 | Goroutines | `ExecutorService`, `synchronized` | goroutines + `sync.Mutex` / channels | `go/02_concurrency/main.go` — `SumConcurrent()`, `SquareAll()` |
| 34 | HTTP server | Spring Boot embedded Tomcat | `net/http` + `ServeMux` | `go/03_http_server/main.go` — `HealthHandler`, `GET /health` |
| 35 | Worker pool | fixed thread pool + queue | goroutines + buffered channels | `go/04_worker_pool/main.go` — `ParseLogLine()`, worker pool |
| 36 | Log processor CLI | batch log analysis tool | file scan + concurrent parse | `go/05_log_processor/main.go` — `ParseAccessLog()` |

### Go vs Java — error handling

```java
// Java
try {
    double r = divide(10, 0);
} catch (ArithmeticException e) { ... }
```

```go
// Go — errors are values, not exceptions
result, err := Divide(10, 4)
if err != nil {
    log.Fatal(err)
}
```

See `go/01_go_basics/main.go` — every function that can fail returns `(T, error)`.

### Go vs Java — HTTP handler

```java
// Spring
@GetMapping("/health")
public Map<String, String> health() { return Map.of("status", "ok"); }
```

```go
// Go — explicit handler function
func HealthHandler(w http.ResponseWriter, r *http.Request) {
    json.NewEncoder(w).Encode(HealthResponse{Status: "ok"})
}
```

See `go/03_http_server/main.go` — same JSON health endpoint as Python Step 12, minimal boilerplate.

### Go vs Python Step 22 — worker pool

Python Step 22 uses a **file-based queue** (`pending/` → `processing/` → `completed/`).  
Go Step 35 uses **in-memory channels** — same worker pattern, different storage. Both teach: bounded concurrency, handle failures, don't lose jobs.

### When to pick Go over Python

| Use Go | Use Python |
|--------|------------|
| Single binary CLI/agent | Quick scripts and glue |
| High goroutine concurrency | FastAPI prototypes |
| K8s/Docker-style tools | Log parsing, YAML glue |
| CPU-heavy concurrent pipelines | Rich ecosystem (pytest, FastAPI) |

---

## Java → Python → Go comparison

| Idea | Java | Python (this lab) | Go (Steps 32–36) |
|------|------|-------------------|------------------|
| Entry point | `main()` | `if __name__ == "__main__"` | `func main()` |
| Types | compile-time | hints + runtime | compile-time |
| Null | `null` | `None` | `nil` |
| Errors | exceptions | `try/except` | `(value, error)` |
| Modules | JAR/Maven | venv + pip | go.mod |
| Web API | Spring | FastAPI | net/http |
| Parallelism | threads | threads/async (GIL!) | goroutines |

---

## Real-world use cases

After completing the lab you can explain and build:

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

## Repository conventions

### Two numbering systems

1. **Step number (0–36)** — order you learn (`./run.sh N`, `./check.sh N`).
2. **Folder name** — topic group (`python/13_health_checker/`, `step_01_variables/`).

They differ on purpose: early steps use micro-folders under `01_python_basics/`; later steps use topic IDs.

### Path helpers (used in every step)

```python
from python.common.paths import sample_data_path, output_path

log = sample_data_path("logs", "access.log")   # version-controlled inputs
out = output_path("health_report.json")        # gitignored runtime output
```

Shared utilities live in `python/common/` — logging setup, config loader, path helpers.

### Sample data

| Path | Purpose |
|------|---------|
| `sample_data/logs/` | Access and app logs for parsing |
| `sample_data/configs/` | YAML service configs |
| `sample_data/metrics/` | Host metrics JSON |
| `sample_data/alerts/` | Alert rule definitions |
| `sample_data/output/` | Runtime output (gitignored) |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Run setup.ps1 first` | Run `.\setup.ps1` once |
| `python3 not found` (WSL) | `sudo apt update && sudo apt install -y python3 python3-venv python3-pip` |
| `No module named pytest` | Run `./setup.sh` again |
| Step 10 fails on Windows | Use WSL — subprocess/Linux modules need Linux |
| Step 12 blocks terminal | Normal — server runs until Ctrl+C; use 2nd terminal for `./run.sh 11` |
| Go step fails on Windows | Use WSL — `wsl ./run.sh 32` |
| Tests fail after edits | Run `./check.sh N` for that step only first |
| Unknown step number | See [step index table](#full-step-index-036) |

---

## Keep practicing

1. Re-do **exercise.py** files without looking at **solution.py**.
2. Change alert thresholds in `sample_data/alerts/rules.yaml` and re-run Step 19.
3. Add a new health endpoint in Step 12 and poll it from Step 11.
4. Complete Go Steps 32–36 in WSL after Python feels comfortable.

When `./check.sh all` passes in WSL, you have a complete local lab — zero to hero, on your machine, at your pace.

---

## License

MIT — see [LICENSE](LICENSE).
