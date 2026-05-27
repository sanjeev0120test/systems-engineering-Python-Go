# systems-engineering-Python-Go

Local **Python and Go systems engineering** practice lab — Python-first (90%), Go basics (10%).

Everything runs **locally** in Cursor with **WSL2** — no cloud required.

## Quick start

1. Open **[START_HERE.md](START_HERE.md)** and follow Step 0 → Step 1.
2. When you finish the path, read **[GUIDE.md](GUIDE.md)** (summary, Java comparison, use cases).

```bash
chmod +x setup.sh run.sh check.sh
./setup.sh
./run.sh 1
./check.sh 1
```

Windows: `.\setup.ps1` · `.\run.ps1 1` · `.\check.ps1 1`

## What's inside

| Path | Purpose |
|------|---------|
| [START_HERE.md](START_HERE.md) | Linear step-by-step guide (Steps 0–36) |
| [GUIDE.md](GUIDE.md) | **Read last** — concepts, Java map, use cases |
| [ROADMAP.md](ROADMAP.md) | Checklist tracker |
| [docs/STEP_INDEX.md](docs/STEP_INDEX.md) | Step number → folder path |
| [python/](python/) | 31 Python steps (lesson + exercise + solution + tests) |
| [go/](go/) | 5 Go steps (32–36) |
| [sample_data/](sample_data/) | Logs, configs, metrics for local simulations |
| [docs/](docs/) | Java→Python, concurrency tree, SLO glossary |

## Commands

| Command | Action |
|---------|--------|
| `./setup.sh` | Create venv, install deps (once) |
| `./run.sh N` | Run step N lesson |
| `./run.sh N exercise` | Run your practice file |
| `./check.sh N` | Verify step N (pytest + PASS/FAIL) |
| `./check.sh all` | Full suite (Python + Go in WSL) |
| `python scripts/validate_all.py` | Maintainer cross-check |

## Prerequisites

- WSL2 Ubuntu (primary for Steps 10, 32–36)
- Python 3.11+
- Go 1.22+ (Steps 32–36 only)

## License

MIT — see [LICENSE](LICENSE).
