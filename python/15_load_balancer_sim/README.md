# Step 24 — Load Balancer Simulator

Round-robin HTTP load balancing across multiple local backend URLs.

## Run

```bash
./run.sh 24
./check.sh 24
```

## Key concepts

- **Round-robin:** fair rotation when backends are equivalent
- **Health checks:** never route to known-bad instances
- **X-Backend-Used:** trace which instance served a request

## Next

Step 25 schedules recurring jobs with APScheduler.
