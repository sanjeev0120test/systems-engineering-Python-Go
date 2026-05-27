# Step 7 — File handling

Read and write log files the way production production tooling does: context managers, explicit UTF-8, and repo-root paths that work everywhere.

## Goals

- Use `with open(...)` so files always close (Java: try-with-resources)
- Build paths with `pathlib.Path` instead of string concatenation
- Read `sample_data/logs/access.log` via `sample_data_path()`
- Write summaries to `sample_data/output/` via `output_path()`

## Run

```bash
./run.sh 7              # lesson demo
./run.sh 7 exercise     # your implementation
./run.sh 7 solution     # reference solution
./check.sh 7            # pytest (must PASS)
```

## Exercise

Implement the functions in `exercise.py`:

1. `read_log_lines` — read file, skip blanks
2. `parse_status_code` — pull HTTP status from combined log line
3. `count_http_statuses` — aggregate counts
4. `write_status_report` — TSV under any output path
5. `process_access_log` — wire paths + read + write

## Java bridge

| Java | Python |
|------|--------|
| `Files.readAllLines` | `path.read_text().splitlines()` or `with open` |
| `try-with-resources` | `with path.open(...) as f:` |
| `Paths.get(a, b)` | `Path(a) / b` or `sample_data_path("a", "b")` |

## Production context

Access logs drive error-rate SLIs, latency dashboards, and incident timelines. The same file patterns apply to config snapshots, health reports, and alert exports in later steps.
