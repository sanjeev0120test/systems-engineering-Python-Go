"""Step 26 — Configuration management and drift detection."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (production) ---
# Config drift — when running systems diverge from declared intent — causes mysterious
# incidents: one pod still on old timeout values, a firewall rule edited by hand, a
# feature flag flipped in prod but not staging. GitOps + automated diff alerts catch
# drift before it burns error budget.

# --- Production patterns ---
# - Store desired state in Git; CI renders and applies (Argo CD, Flux)
# - Snapshot before/after deploys; fail pipeline on unexpected diffs
# - Separate secrets (Vault/SOPS) from non-secret config — never diff secrets to logs

# --- Java developer note ---
# Spring Cloud Config Server centralizes YAML like this lesson, but you still need drift
# detection when someone kubectl-edits a live ConfigMap.

# --- How to run ---
# ./run.sh 26
# ./check.sh 26


def main() -> None:
    from solution import (
        default_service_config_path,
        detect_drift,
        snapshot_config,
        write_drift_report,
    )

    baseline = snapshot_config(
        default_service_config_path(),
        Path(default_service_config_path().parent / "service_baseline.yaml"),
    )
    drift = detect_drift(baseline, default_service_config_path())
    report = write_drift_report(drift)
    logger.info("Baseline snapshot: %s", baseline)
    logger.info("Drift entries: %s", len(drift))
    logger.info("Report written: %s", report)


if __name__ == "__main__":
    main()
