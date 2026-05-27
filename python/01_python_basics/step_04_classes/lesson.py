"""Step 4 — Classes and @dataclass for server inventory.

Run from repo root:
    ./run.sh 4
    python python/01_python_basics/step_04_classes/lesson.py

Run from this folder:
    python lesson.py

Java developer notes
--------------------
- `@dataclass` auto-generates `__init__`, `__repr__`, `__eq__` — like Java `record`.
- `field(default_factory=list)` avoids mutable default argument bug (never use `tags=[]`).
- Instance methods take `self` as first param (like implicit `this` in Java instance methods).
- No `public`/`private` keywords — convention: prefix `_name` for internal use.

SRE context
-----------
CMDB entries, Kubernetes node lists, and YAML host blocks all map to inventory objects.
Model them once with dataclasses instead of passing raw dicts through every script.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from solution import Server, build_inventory, find_by_role, unhealthy_hostnames  # noqa: E402

RAW_HOSTS: list[dict[str, object]] = [
    {"hostname": "web-01", "role": "frontend", "ip": "10.0.0.1", "healthy": True, "tags": ["prod"]},
    {"hostname": "api-01", "role": "backend", "ip": "10.0.0.2", "healthy": False},
    {"hostname": "db-01", "role": "database", "ip": "10.0.0.10", "healthy": True, "tags": ["prod", "pci"]},
]


def main() -> None:
    print("=" * 60)
    print("Step 4: Classes — Server inventory with @dataclass")
    print("=" * 60)

    inventory = build_inventory(RAW_HOSTS)
    print(f"\n1) Built inventory: {len(inventory)} servers")
    for server in inventory:
        print(f"   {server.display_name()} ip={server.ip} healthy={server.healthy}")

    backends = find_by_role(inventory, "backend")
    print(f"\n2) Backend role count: {len(backends)}")
    for server in backends:
        print(f"   {server.hostname}")

    bad = unhealthy_hostnames(inventory)
    print(f"\n3) Unhealthy hostnames: {bad}")

    # Mutating state after probe failure
    web = inventory[0]
    print(f"\n4) Before probe failure: {web.hostname} healthy={web.healthy}")
    web.mark_unhealthy()
    print(f"   After probe failure:  {web.hostname} healthy={web.healthy}")

    print("\nNext: implement exercise.py, then ./check.sh 4")


if __name__ == "__main__":
    main()
