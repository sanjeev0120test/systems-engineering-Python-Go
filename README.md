# systems-engineering-Python-Go

Local **SRE / DevOps / Platform Engineering** practice lab — Python-first (90%), Go basics (10%).

Everything runs **locally** in Cursor with **WSL2** — no cloud required.

## Quick start

**Open [START_HERE.md](START_HERE.md)** and follow Step 0.

```bash
chmod +x setup.sh run.sh check.sh
./setup.sh
./run.sh 1
./check.sh 1
```

## What's inside

| Path | Purpose |
|------|---------|
| [START_HERE.md](START_HERE.md) | Linear step-by-step guide |
| [ROADMAP.md](ROADMAP.md) | Checklist tracker |
| [python/](python/) | 31 Python steps (lesson + exercise + solution + tests) |
| [go/](go/) | 5 Go steps (Steps 32–36) |
| [sample_data/](sample_data/) | Logs, configs, metrics for local simulations |
| [docs/](docs/) | Java→Python cheat sheet, SLO glossary |

## Commands

| Command | Action |
|---------|--------|
| `./setup.sh` | Create venv, install all deps (once) |
| `./run.sh N` | Run step N lesson |
| `./run.sh N exercise` | Run your exercise |
| `./check.sh N` | Verify step N (pytest + PASS/FAIL) |
| `./check.sh all` | Run full test suite |
| `make test` | pytest all Python modules |

## Prerequisites

- WSL2 Ubuntu (primary)
- Python 3.11+
- Go 1.22+ (for Steps 32–36)

Windows-only: run [setup.ps1](setup.ps1) for venv, then use WSL for Linux modules.

## License

MIT — see [LICENSE](LICENSE).
