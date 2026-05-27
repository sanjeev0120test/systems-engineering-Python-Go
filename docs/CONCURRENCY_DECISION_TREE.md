# When to use threading vs multiprocessing vs asyncio

```text
CPU-bound work (parse huge logs, crypto, compression)
  → multiprocessing (bypass GIL) OR external worker service

I/O-bound sync (requests, subprocess, file reads)
  → threading OR asyncio (asyncio scales better at high concurrency)

Simple parallel host checks (few targets)
  → ThreadPoolExecutor (Step 14) — easy to reason about

Many concurrent HTTP probes (100+ endpoints)
  → asyncio + aiohttp pattern (Step 15)

Go infrastructure tools (K8s, Docker, Prometheus)
  → native goroutines — see Steps 32–36
```

## Java developer trap

Java threads help CPU parallelism. Python threads **do not** for CPU-heavy work due to the GIL. Use processes or Go/Rust for CPU-heavy pipelines.
