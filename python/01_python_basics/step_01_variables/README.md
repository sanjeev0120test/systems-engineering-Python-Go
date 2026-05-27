# Step 1 — Variables, types, f-strings

**Time:** ~15 minutes  
**Goal:** Parse hostnames from URLs and log lines; format on-call alerts with f-strings.

## Run

```bash
./run.sh 1              # lesson demo
./run.sh 1 exercise     # your TODOs
./check.sh 1            # pytest — must PASS before Step 2
```

From this folder or repo root:

```bash
python lesson.py
python exercise.py
```

## What you will learn

| Python | Java analogy | Production use |
|--------|--------------|---------|
| `hostname: str` | `String hostname` | Type hints for readability |
| f-strings | `String.format` | Alert and log messages |
| `urlparse` | `java.net.URI` | Extract host from health-check URL |
| `None` | `null` | Missing hostname in log line |

## Files

- `lesson.py` — commented walkthrough (run first)
- `exercise.py` — your implementation (TODOs)
- `solution.py` — reference answer
- `test_lesson.py` — automated checks

## Exercise checklist

1. Implement `parse_hostname_from_url` using `urllib.parse.urlparse`
2. Implement `parse_hostname_from_log_line` for `hostname=` tokens
3. Implement `format_host_alert` with CRITICAL vs WARNING severity
4. Run `./check.sh 1` until PASS

See [docs/JAVA_TO_PYTHON.md](../../../docs/JAVA_TO_PYTHON.md) for the full cheat sheet.
