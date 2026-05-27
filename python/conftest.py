"""Shared pytest setup for all step tests."""

from __future__ import annotations

import pytest

from python.common import paths as paths_module
from python.common.paths import _find_repo_root


@pytest.fixture(autouse=True)
def _reset_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep path helpers pointed at this repo during tests."""
    monkeypatch.setattr(paths_module, "REPO_ROOT", _find_repo_root(), raising=False)
