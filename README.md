# systems-engineering-Python-Go

Local **Python and Go systems engineering** practice lab for Java developers.

- **Python:** Steps 1-31 (90% of the path)
- **Go:** Steps 32-36 (basics only)
- **Runs locally** in Cursor — no cloud required

## Start here (pick your terminal)

### WSL Ubuntu (recommended — full path including Go)

Use this for Steps 10+ (Linux subprocess), Steps 32-36 (Go), and `./check.sh all`.

```bash
cd /mnt/c/dev/systems-engineering-Python-Go
chmod +x setup.sh run.sh check.sh
./setup.sh
./check.sh 0          # must print PASS
./run.sh 1
./check.sh 1
```

Then open **[START_HERE.md](START_HERE.md)** and follow Steps 0-36 in order.  
When finished, read **[GUIDE.md](GUIDE.md)** (concepts, Java comparison, use cases).

### Windows PowerShell (Python Steps 1-31 only)

```powershell
cd C:\dev\systems-engineering-Python-Go
.\setup.ps1
.\check.ps1 0         # must print PASS
.\run.ps1 1
.\check.ps1 1
```

For Go steps and Linux-heavy modules, switch to WSL and use `./setup.sh` / `./run.sh` / `./check.sh`.

## What's inside

| Path | Purpose |
|------|---------|
| [START_HERE.md](START_HERE.md) | Step-by-step guide (Steps 0-36) |
| [GUIDE.md](GUIDE.md) | **Read last** — concepts, Java map, use cases |
| [ROADMAP.md](ROADMAP.md) | Checklist tracker |
| [docs/STEP_INDEX.md](docs/STEP_INDEX.md) | Step number to folder path |
| [python/](python/) | 31 Python steps (lesson + exercise + solution + tests) |
| [go/](go/) | 5 Go steps (32-36) |
| [sample_data/](sample_data/) | Logs, configs, metrics for local simulations |
| [docs/](docs/) | Java to Python, concurrency tree, SLO glossary |

> **Note:** Step number is not always the folder name. Example: Step 16 lives in `python/13_health_checker/`. See [docs/STEP_INDEX.md](docs/STEP_INDEX.md).

## Commands

| Command | Action |
|---------|--------|
| `./setup.sh` or `.\setup.ps1` | Create `.venv`, install deps (once) |
| `./run.sh N` or `.\run.ps1 N` | Run step N lesson |
| `./run.sh N exercise` | Run your practice file |
| `./check.sh N` or `.\check.ps1 N` | Verify step N |
| `./check.sh all` or `.\check.ps1 all` | Full Python test suite |
| `python scripts/validate_all.py` | Maintainer cross-check |

## Prerequisites

| Tool | Required for | Install |
|------|--------------|---------|
| Python 3.11+ | All steps | [python.org](https://www.python.org/downloads/) or `sudo apt install python3 python3-venv` |
| WSL2 Ubuntu | Steps 10, 32-36 | `wsl --install` then Ubuntu |
| Go 1.22+ | Steps 32-36 only | [go.dev/dl](https://go.dev/dl/) inside WSL |

Dependencies (pytest, FastAPI, etc.) install automatically from [requirements.txt](requirements.txt) when you run setup.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Run setup.ps1 first` | Run `.\setup.ps1` once |
| `python3 not found` (WSL) | `sudo apt update && sudo apt install -y python3 python3-venv python3-pip` |
| Step 10 fails on Windows | Use WSL — subprocess/Linux modules need Linux |
| Go step fails on Windows | Use WSL — `wsl ./run.sh 32` |
| Tests fail after edits | Run `./check.sh N` for that step only first |

## License

MIT — see [LICENSE](LICENSE).
