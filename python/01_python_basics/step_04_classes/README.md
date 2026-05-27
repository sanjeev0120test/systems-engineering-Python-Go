# Step 4 — Classes and dataclasses

**Time:** ~25 minutes  
**Goal:** Model server inventory with `@dataclass` instead of raw dicts.

## Run

```bash
./run.sh 4
./run.sh 4 exercise
./check.sh 4
```

## Concepts

| Python | Java |
|--------|------|
| `@dataclass` | `record` / Lombok `@Data` |
| `field(default_factory=list)` | mutable list in constructor |
| `self` | implicit `this` |

## Sample inventory source

See `sample_data/configs/service.yaml` — hosts block mirrors real service config.

Pass `./check.sh 4` before Step 5.
