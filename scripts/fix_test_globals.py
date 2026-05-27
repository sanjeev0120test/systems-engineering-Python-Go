"""Add solution re-exports and fix common test issues after batch rewrite."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "python"

EXPORT_BLOCK = """
for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)
"""

for test_file in ROOT.rglob("test_lesson.py"):
    text = test_file.read_text(encoding="utf-8")
    if "globals()[_name]" in text:
        continue
    needle = "solution = mod\n\n"
    if needle not in text:
        print("SKIP", test_file)
        continue
    text = text.replace(needle, needle + EXPORT_BLOCK + "\n")
    text = text.replace("def test_stale_heartbeat_triggers_re election", "def test_stale_heartbeat_triggers_re_election")
    if "sys.platform" in text and "import sys" not in text:
        text = text.replace("import pytest\n", "import sys\n\nimport pytest\n", 1)
    test_file.write_text(text, encoding="utf-8")
    print("Fixed", test_file)
