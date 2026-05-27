# Step 34 — Go HTTP server

A minimal `net/http` server with a `/health` endpoint — the same pattern used by Kubernetes probes and load balancers.

## Topics

- `http.ServeMux` routing
- JSON responses with `encoding/json`
- Listening on `:8081`

## Commands

```bash
./run.sh 34
./check.sh 34
```

Manual check:

```bash
curl -s http://localhost:8081/health
```
