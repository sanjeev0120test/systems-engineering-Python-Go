"""Resolve repo paths reliably from WSL, Linux, macOS, or Windows."""

from __future__ import annotations

from pathlib import Path


def _find_repo_root(start: Path | None = None) -> Path:
    """Walk up from cwd until we find START_HERE.md (repo marker)."""
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "START_HERE.md").exists():
            return candidate
    here = Path(__file__).resolve()
    return here.parents[2]


REPO_ROOT: Path = _find_repo_root()


def sample_data_path(*parts: str) -> Path:
    """Build path under sample_data/ (inputs are version-controlled)."""
    return REPO_ROOT / "sample_data" / Path(*parts)


def output_path(*parts: str) -> Path:
    """Build path under sample_data/output/ (runtime artifacts)."""
    target = REPO_ROOT / "sample_data" / "output" / Path(*parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    return target
