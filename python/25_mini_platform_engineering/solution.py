"""Step 31 solution — mini platform engineering capstone pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from python.common.paths import output_path


@dataclass(frozen=True)
class StageResult:
    name: str
    success: bool
    detail: str


@dataclass(frozen=True)
class PipelineReport:
    service: str
    stages: list[StageResult]
    deployed: bool

    @property
    def passed(self) -> bool:
        return all(stage.success for stage in self.stages)


def run_lint(service: str) -> StageResult:
    ok = bool(service) and service.replace("-", "").isalnum()
    return StageResult(
        name="lint",
        success=ok,
        detail="ruff check passed" if ok else "invalid service name",
    )


def run_tests(service: str) -> StageResult:
    return StageResult(
        name="test",
        success=True,
        detail=f"pytest smoke passed for {service}",
    )


def run_deploy(service: str, *, environment: str = "staging") -> StageResult:
    allowed = {"staging", "production"}
    success = environment in allowed
    return StageResult(
        name="deploy",
        success=success,
        detail=f"deployed {service} to {environment}" if success else "unknown environment",
    )


def run_pipeline(
    service: str,
    *,
    environment: str = "staging",
    report_path: Path | None = None,
) -> PipelineReport:
    """Simulate lint → test → deploy and write a report to sample_data/output/."""
    stages = [
        run_lint(service),
        run_tests(service) if service else StageResult("test", False, "skipped"),
        run_deploy(service, environment=environment),
    ]
    if not stages[0].success:
        stages[1] = StageResult("test", False, "skipped due to lint failure")
        stages[2] = StageResult("deploy", False, "skipped due to lint failure")

    deployed = stages[-1].success and all(stage.success for stage in stages)
    report = PipelineReport(service=service, stages=stages, deployed=deployed)
    write_pipeline_report(report, report_path=report_path)
    return report


def write_pipeline_report(report: PipelineReport, report_path: Path | None = None) -> Path:
    target = report_path or output_path("platform_pipeline_report.txt")
    timestamp = datetime.now(timezone.utc).isoformat()
    lines = [
        "Platform pipeline report",
        "========================",
        f"timestamp: {timestamp}",
        f"service: {report.service}",
        f"deployed: {report.deployed}",
        "",
    ]
    for stage in report.stages:
        status = "PASS" if stage.success else "FAIL"
        lines.append(f"[{status}] {stage.name}: {stage.detail}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target
