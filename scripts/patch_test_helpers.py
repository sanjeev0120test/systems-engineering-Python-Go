"""Restore test constants and helpers stripped by fix_tests.py."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PATCHES: dict[str, str] = {
    "python/01_python_basics/step_02_control_flow/test_lesson.py": '''
HOSTS = [
    {"hostname": "web-01", "healthy": True, "status": "healthy", "retry_count": 1},
    {"hostname": "web-02", "healthy": False, "status": "down", "retry_count": 5},
    {"hostname": "api-01", "healthy": False, "status": "degraded", "retry_count": 2},
    {"hostname": "db-01", "healthy": True, "status": "down", "retry_count": 0},
]
''',
    "python/01_python_basics/step_03_functions/test_lesson.py": '''
HOSTS = [
    {"hostname": "web-01", "disk_percent": 55.0, "mount": "/"},
    {"hostname": "db-01", "disk_percent": 93.5, "mount": "/var/lib/mysql"},
]
''',
    "python/01_python_basics/step_04_classes/test_lesson.py": '''
RAW = [
    {"hostname": "web-01", "role": "frontend", "ip": "10.0.0.1", "healthy": True, "tags": ["prod"]},
    {"hostname": "api-01", "role": "backend", "ip": "10.0.0.2", "healthy": False, "tags": []},
    {"hostname": "db-01", "role": "backend", "ip": "10.0.0.3", "healthy": True, "tags": ["prod", "pci"]},
]
''',
    "python/04_logging/test_lesson.py": '''
import uuid


def _unique_name(prefix: str) -> str:
    return f"{prefix}.{uuid.uuid4().hex[:8]}"
''',
    "python/05_subprocess_linux/test_lesson.py": '''
SAMPLE_PS = """\\
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1  16896  1088 ?        Ss   Jan01   0:05 /sbin/init
ubuntu    1234  2.5  1.2 123456 7890 ?        Sl   10:00   0:01 python app.py
"""

SAMPLE_DF = """\\
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   20G   28G  42% /
tmpfs           3.9G     0  3.9G   0% /dev/shm
"""
''',
    "python/06_rest_api/server/test_lesson.py": '''
from fastapi.testclient import TestClient

from server import app
''',
    "python/06_rest_api/client/test_lesson.py": '''
import json


class _FlakyHandler(BaseHTTPRequestHandler):
    call_count = 0

    def do_GET(self) -> None:  # noqa: N802
        type(self).call_count += 1
        if type(self).call_count < 2:
            self.send_response(503)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return
''',
    "python/08_threading/test_lesson.py": '''
import json


class _OkHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def _start_server() -> tuple[HTTPServer, str]:
    server = HTTPServer(("127.0.0.1", 0), _OkHandler)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{port}/health"
''',
    "python/09_asyncio/test_lesson.py": '''
import httpx
import json


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return
''',
    "python/14_reverse_proxy_sim/test_lesson.py": '''
import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient


def _backend_app() -> FastAPI:
    backend = FastAPI()

    @backend.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "backend-a"}

    @backend.get("/api/items")
    def items() -> dict[str, list[str]]:
        return {"items": ["cpu", "memory"]}

    return backend
''',
    "python/15_load_balancer_sim/test_lesson.py": '''
import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
''',
    "python/16_rate_limiter/test_lesson.py": '''
from fastapi.testclient import TestClient
''',
}

DISTRIBUTED_FIX = '''def test_stale_heartbeat_triggers_re_election() -> None:
    cluster = LeaderElectionCluster(heartbeat_timeout=2.0)
    t0 = 5000.0
    cluster.register("node-a", priority=2)
    cluster.register("node-b", priority=1)
    cluster.heartbeat("node-a", now=t0)
    cluster.heartbeat("node-b", now=t0)
    assert cluster.elect_leader(now=t0) == "node-a"
    cluster.heartbeat("node-b", now=t0 + 2.9)
    assert cluster.elect_leader(now=t0 + 3.0) == "node-b"
'''


def main() -> None:
    marker = "globals()[_name] = getattr(mod, _name)\n"
    for rel_path, insert in PATCHES.items():
        path = ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        if insert.strip() in text:
            print("skip", rel_path)
            continue
        if marker not in text:
            print("no marker", rel_path)
            continue
        text = text.replace(marker, marker + insert + "\n", 1)
        path.write_text(text, encoding="utf-8")
        print("patched", rel_path)

    dist_path = ROOT / "python/22_distributed_system_basics/test_lesson.py"
    dist_text = dist_path.read_text(encoding="utf-8")
    old = dist_text.split("def test_stale_heartbeat_triggers_re_election")[1]
    old_fn = "def test_stale_heartbeat_triggers_re_election" + old.split("\n\n", 1)[0]
    if "cluster.heartbeat(\"node-b\", now=t0 + 2.9)" not in dist_text:
        dist_text = dist_text.replace(old_fn, DISTRIBUTED_FIX.strip())
        dist_path.write_text(dist_text, encoding="utf-8")
        print("patched distributed test")


if __name__ == "__main__":
    main()
