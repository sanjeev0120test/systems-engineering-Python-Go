"""One-time script to normalize all test_lesson.py imports."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "python"


def patch_test_file(test_file: Path) -> None:
    text = test_file.read_text(encoding="utf-8")
    if "from python.step_loader import load_solution" in text:
        return

    m = re.match(r'(""".*?""")\n', text, re.DOTALL)
    doc = m.group(1) if m else '"""Step tests."""'

    body_start = re.search(r"^(@pytest|def test_)", text, re.MULTILINE)
    if not body_start:
        print(f"SKIP {test_file}")
        return
    body = text[body_start.start() :]

    extra: list[str] = []
    if "paths_module" in body or "sample_data_path" in body or "output_path" in body:
        extra.append("from python.common import paths as paths_module")
        extra.append("from python.common.paths import output_path, sample_data_path")
    if "json." in body or "json.loads" in body:
        extra.append("import json")
    if "sqlite3" in body:
        extra.append("import sqlite3")
    if "HTTPServer" in body or "BaseHTTPRequestHandler" in body:
        extra.extend(
            [
                "import sys",
                "from http.server import BaseHTTPRequestHandler, HTTPServer",
                "from threading import Thread",
                "from typing import Any",
            ]
        )
    if "patch" in body:
        extra.append("from unittest.mock import patch")
    if "requests" in body:
        extra.append("import requests")
    if "asyncio" in body:
        extra.append("import asyncio")
    if "uuid" in body:
        extra.append("import uuid")
    if "logging" in body:
        extra.append("import logging")

    extra_block = "\n".join(extra)
    if extra_block:
        extra_block = extra_block + "\n"

    new_text = (
        f"{doc}\n\n"
        "from __future__ import annotations\n\n"
        "from pathlib import Path\n\n"
        "import pytest\n"
        f"{extra_block}\n"
        "from python.step_loader import load_solution\n\n"
        "STEP_DIR = Path(__file__).resolve().parent\n"
        "mod = load_solution(STEP_DIR)\n"
        "solution = mod\n\n"
        f"{body}\n"
    )
    test_file.write_text(new_text, encoding="utf-8")
    print(f"Updated {test_file}")


for test_file in ROOT.rglob("test_lesson.py"):
    patch_test_file(test_file)
