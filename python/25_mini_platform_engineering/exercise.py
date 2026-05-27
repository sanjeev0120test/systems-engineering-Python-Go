"""Step 31 exercise — platform engineering capstone pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
        raise NotImplementedError("Implement passed")


def run_lint(service: str) -> StageResult:
    raise NotImplementedError("Implement run_lint")


def run_tests(service: str) -> StageResult:
    raise NotImplementedError("Implement run_tests")


def run_deploy(service: str, *, environment: str = "staging") -> StageResult:
    raise NotImplementedError("Implement run_deploy")


def run_pipeline(
    service: str,
    *,
    environment: str = "staging",
    report_path: Path | None = None,
) -> PipelineReport:
    raise NotImplementedError("Implement run_pipeline")


def write_pipeline_report(report: PipelineReport, report_path: Path | None = None) -> Path:
    raise NotImplementedError("Implement write_pipeline_report")


def main() -> None:
    print("Implement platform capstone, then run: ./check.sh 31")


if __name__ == "__main__":
    main()
