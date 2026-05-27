# Step 10 — Subprocess on Linux/WSL

Replace shell runbook commands with Python: run `ps aux` and `df -h` with timeouts and parse the output.

## Run

```bash
./run.sh 10
./run.sh 10 exercise
./check.sh 10
```

Use **WSL or Linux** for live `ps`/`df` demos. Parser unit tests run on any platform.

## Files

| File | Purpose |
|------|---------|
| `lesson.py` | Demo subprocess calls |
| `exercise.py` | Your implementation |
| `solution.py` | Reference solution |
| `test_lesson.py` | pytest |

## Key concepts

- `subprocess.run(..., capture_output=True, text=True, timeout=N)`
- Exit codes and stderr — fail gracefully in automation
- Parsing CLI output for structured health data

## Troubleshooting

- **Windows native:** `ps`/`df` not found — open WSL terminal in Cursor.
- **TimeoutExpired:** increase timeout or check hung process.
