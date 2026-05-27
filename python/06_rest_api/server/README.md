# Step 12 — REST API Server

Minimal FastAPI microservice on `127.0.0.1:8080` with `/health` (liveness) and `/ready` (readiness).

## Run

```bash
./run.sh 12          # runs server.py — keeps running until Ctrl+C
./check.sh 12        # pytest with TestClient (no server needed)
```

Verify manually:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
```

Then run Step 11 client in another terminal: `./run.sh 11`

## Files

| File | Purpose |
|------|---------|
| `server.py` | **Run target** for `./run.sh 12` |
| `lesson.py` | Same server + teaching notes |
| `exercise.py` | Your FastAPI endpoints |
| `solution.py` | Reference app |
| `test_lesson.py` | TestClient tests |

## Key concepts

- Liveness vs readiness probes
- FastAPI + uvicorn ASGI stack
- OpenAPI at `/docs` and `/openapi.json`

## Troubleshooting

- **Address already in use:** another process on 8080 — `lsof -i :8080` (Linux/WSL).
- **Module not found:** run from repo root; `./run.sh` sets `PYTHONPATH`.
