# Step 9 — Logging

Structured logging with the stdlib `logging` module and JSON lines for production observability stacks.

## Goals

- Configure text vs JSON loggers via `python.common.logging_setup.get_logger`
- Attach `trace_id` and `service` with the `extra=` dict (like Java MDC)
- Log health-check events and access-log summaries at appropriate levels
- Understand when to use DEBUG locally vs INFO/WARNING in prod

## Run

```bash
./run.sh 9
./run.sh 9 exercise
./run.sh 9 solution
./check.sh 9
```

## Exercise

Implement `exercise.py`:

1. `build_text_logger` / `build_json_logger`
2. `log_health_check` — endpoint, status, latency with correlation ID
3. `summarize_status_counts` — aggregate 5xx counts
4. `run_health_check_demo` — wire trace ID + logger together

## Java bridge

| Java | Python |
|------|--------|
| SLF4J | `logging.getLogger` |
| Logback JSON | `JsonFormatter` in `logging_setup.py` |
| MDC | `logger.info(..., extra={"trace_id": ...})` |
| `log.warn` | `logger.warning(...)` |

## SRE context

During incidents, grep-friendly text logs help on a laptop; JSON logs feed Loki, Elasticsearch, and Cloud Logging. Correlation IDs connect the health checker, alert, and remediation script in one trace.
