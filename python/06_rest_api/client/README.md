# Step 11 — REST API Client

Poll a `/health` endpoint with `requests`, retries, and timeouts — the pattern used in health smoke tests and deploy verification.

## Run

```bash
# Terminal 1 — start server (Step 12)
./run.sh 12

# Terminal 2 — poll health
./run.sh 11
./check.sh 11
```

## Files

| File | Purpose |
|------|---------|
| `lesson.py` | Live poll against localhost:8080 |
| `exercise.py` | Your implementation |
| `solution.py` | Reference solution |
| `test_lesson.py` | pytest with local HTTP server |

## Key concepts

- `requests.Session` + `HTTPAdapter` + `urllib3.Retry`
- Per-request `timeout=` (connect + read)
- Backoff between attempts during deploys

## Troubleshooting

- **Connection refused:** start Step 12 server first (`./run.sh 12`).
- **All retries fail:** check firewall and that server binds `127.0.0.1:8080`.
