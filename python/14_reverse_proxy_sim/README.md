# Step 23 — Reverse Proxy Simulator

Forward HTTP requests to a local backend through a FastAPI reverse proxy.

## Run

```bash
./run.sh 23
./check.sh 23
```

## Key concepts

- **Reverse proxy:** clients see one front door; backends can change
- **Hop-by-hop headers:** stripped before forwarding
- **Observability:** normalize upstream health for dashboards

## Next

Step 24 load-balances across multiple backend ports with round-robin.
