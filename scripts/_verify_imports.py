"""Smoke test for python.common imports — used by verify_setup.ps1."""
from python.common.logging_setup import new_trace_id
from python.common.paths import sample_data_path

assert len(new_trace_id()) == 16
assert sample_data_path("logs", "access.log").exists()
print("imports ok")
