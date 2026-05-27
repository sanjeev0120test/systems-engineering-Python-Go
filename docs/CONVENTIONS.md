# Repository Conventions

## Two numbering systems

1. **Step number (0–36)** — order you learn (`./run.sh N`, `./check.sh N`).
2. **Folder name** — topic group (`python/13_health_checker/`, `step_01_variables/`).

They differ on purpose: early steps use micro-folders under `01_python_basics/`; later steps use topic IDs. Full map: [STEP_INDEX.md](STEP_INDEX.md).

## Step folder layout

```text
python/<topic_folder>/
├── README.md
├── lesson.py      # ./run.sh N
├── exercise.py    # your TODOs
├── solution.py    # reference + tests
└── test_lesson.py # pytest
```

Basics use nested paths: `python/01_python_basics/step_01_variables/`.

## Path helpers

```python
from python.common.paths import sample_data_path, output_path

log = sample_data_path("logs", "access.log")   # version-controlled inputs
out = output_path("health_report.json")        # gitignored runtime output
```

Environment overrides use **`LAB_` prefix** (e.g. `LAB_ENVIRONMENT=prod`).

## Comment blocks in lesson.py

Sections may include: Java note, Python concept, production use case, how to run, expected output, production tradeoff.

## Verification

Never skip `./check.sh N` before Step N+1. Final summary: [GUIDE.md](../GUIDE.md).
