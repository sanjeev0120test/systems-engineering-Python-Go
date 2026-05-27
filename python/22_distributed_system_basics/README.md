# Step 30 — Distributed System Basics

Heartbeat-based leader election with priority and failover simulation.

## Run

```bash
./run.sh 30
./check.sh 30
```

## Key concepts

- **Leader election:** exactly one active coordinator
- **Heartbeats:** detect crashed nodes via timeout
- **Failover:** re-elect when leader is dead or stale

## Next

Step 31 capstone simulates lint → test → deploy and writes a report.
