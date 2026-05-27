# SLI / SLO / Error Budget Glossary

| Term | Meaning | In this repo |
|------|---------|--------------|
| **SLI** | Service Level Indicator — a measurable signal | `error_rate`, `latency_p95_ms` from Step 18 |
| **SLO** | Service Level Objective — target for an SLI | Alert thresholds in `sample_data/alerts/rules.yaml` |
| **SLA** | Contract with customers (often 99.9% uptime) | Discussed in README interview sections |
| **Error budget** | Allowed unreliability before feature freeze | If error_rate > 0.05, budget burning (Step 19) |
| **Golden signals** | Latency, traffic, errors, saturation | Steps 17–19 simulate these |

## Production notes

- SLOs should be user-journey based (checkout success), not server CPU alone.
- Multi-window burn alerts catch fast and slow budget consumption.
- Error budgets align product and engineering teams: when budget is gone, stop risky releases.
