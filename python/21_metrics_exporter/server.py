"""Step 29 — Prometheus metrics server entrypoint (./run.sh 29)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prometheus_client import make_wsgi_app
from wsgiref.simple_server import make_server

from solution import simulate_traffic


def main() -> None:
    simulate_traffic()
    app = make_wsgi_app()
    host = "127.0.0.1"
    port = 9100
    print(f"Prometheus metrics on http://{host}:{port}/metrics")
    print("Press Ctrl+C to stop.")
    with make_server(host, port, app) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
