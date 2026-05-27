"""Load step-local solution.py without cross-step import collisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def load_solution(step_dir: Path) -> ModuleType:
    """Import solution.py from *step_dir* under a unique module name."""
    step_dir = step_dir.resolve()
    unique_name = "solution_" + step_dir.as_posix().replace("/", "_").replace(":", "")
    spec = importlib.util.spec_from_file_location(unique_name, step_dir / "solution.py")
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load solution from {step_dir}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[unique_name] = module
    spec.loader.exec_module(module)
    return module
