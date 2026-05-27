# Repository Conventions

## Step folder layout

```text
python/XX_module/
├── README.md
├── lesson.py      # Run with ./run.sh N
├── exercise.py    # Your TODOs
├── solution.py    # Reference + tests target
└── test_lesson.py # pytest
```

## Path helpers

Always use `python.common.paths`:

```python
from python.common.paths import sample_data_path, output_path

log = sample_data_path("logs", "access.log")   # version-controlled inputs
out = output_path("health_report.json")        # gitignored runtime output
```

## Comment blocks in lesson.py

Each section may include: Java note, Python concept, SRE use case, run command, expected output, interview tip, production tradeoff.

## Verification

Never skip `./check.sh N` before advancing to Step N+1.
