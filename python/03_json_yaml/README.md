# Step 8 — JSON & YAML

Load service configuration and metrics snapshots — the two formats SRE teams touch daily.

## Goals

- Parse `sample_data/configs/service.yaml` with `python.common.config_loader`
- Parse `sample_data/metrics/host_metrics.json` with `json.load`
- Apply `SRE_*` environment variable overrides (12-factor config)
- Extract endpoints and capacity signals for monitoring logic

## Run

```bash
./run.sh 8
./run.sh 8 exercise
./run.sh 8 solution
./check.sh 8
```

## Exercise

Implement `exercise.py` using:

- `load_service_config` / `load_yaml` from `python.common.config_loader`
- `sample_data_path` from `python.common.paths`
- `json.load` with `encoding="utf-8"`

## Java bridge

| Java | Python |
|------|--------|
| Jackson `readValue` | `json.load(handle)` |
| SnakeYAML | `yaml.safe_load` via `load_yaml()` |
| `@ConfigurationProperties` | YAML + `load_service_config()` env merge |
| `System.getenv` | `env("KEY", default)` |

## SRE context

Health checkers, alert engines, and deploy pipelines all start by reading YAML/JSON config. Environment overrides let the same file run locally and in Kubernetes without edits.
