"""Replace systems engineering wording with neutral terms across the repo."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}

EXTENSIONS = {".py", ".md", ".sh", ".ps1", ".toml", ".yaml", ".yml", ".go", ".txt"}

# Order matters: longer / more specific patterns first.
REPLACEMENTS: list[tuple[str, str]] = [
    ("Python and Go systems engineering", "Python and Go systems engineering"),
    ("systems engineering", "systems engineering"),
    ("systems engineering", "systems engineering"),
    ("systems engineering", "systems engineering"),
    ("LAB_CHECK_INTERVAL_SECONDS", "LAB_CHECK_INTERVAL_SECONDS"),
    ("LAB_AGENT_ONCE", "LAB_AGENT_ONCE"),
    ("LAB_ENVIRONMENT", "LAB_ENVIRONMENT"),
    ("LAB_HTTP_TIMEOUT", "LAB_HTTP_TIMEOUT"),
    ("LAB_*", "LAB_*"),
    ("LAB_", "LAB_"),
    ("lab_http_requests_total", "lab_http_requests_total"),
    ("lab_in_flight_requests", "lab_in_flight_requests"),
    ("lab_request_latency_seconds", "lab_request_latency_seconds"),
    ("practice-lab", "practice-lab"),
    ("Practice Lab Service", "Practice Lab Service"),
    ("Practice Lab API", "Practice Lab API"),
    ("# --- Why this matters (production) ---", "# --- Why this matters (production) ---"),
    ("## Production context", "## Production context"),
    ("Production context", "Production context"),
    ("# PRODUCTION USE CASES", "# PRODUCTION USE CASES"),
    ("PRODUCTION USE CASES", "PRODUCTION USE CASES"),
    ("Production use case", "Production use case"),
    ("Production use", "Production use"),
    ("platform teams", "platform teams"),
    ("production tooling", "production tooling"),
    ("automation workflows", "automation workflows"),
    ("systems string parsing", "systems string parsing"),
    ("service configuration", "service configuration"),
    ("service configuration", "service configuration"),
    ("health smoke tests", "health smoke tests"),
    ("service config", "service config"),
    ("core production mini-systems", "core production mini-systems"),
    ("Python Practice Lab", "Python Practice Lab"),
    ("Python Practice Lab Setup", "Python Practice Lab Setup"),
    ("Python systems", "Python systems"),
    ("CLI automation tools", "CLI automation tools"),
    ("practice lab steps", "practice lab steps"),
    ("Production rule:", "Production rule:"),
    ("production-style", "production-style"),
    ("Python track", "Python track"),
    ("Production context and demo", "Production context and demo"),
    ("Production engineering mindset shift", "Production engineering mindset shift"),
    ("for systems engineering", "for systems engineering"),
    ("align product and engineering teams:", "align product and engineering teams:"),
    ("Linux/automation modules", "Linux/automation modules"),
    ("Practice Lab", "Practice Lab"),
    ('name: str = "lab.text"', 'name: str = "lab.text"'),
    ('name: str = "lab.json"', 'name: str = "lab.json"'),
    ('_unique_name("lab.text")', '_unique_name("lab.text")'),
    ('_unique_name("lab.json")', '_unique_name("lab.json")'),
    ("test_run_agent_respects_lab_agent_once_env", "test_run_agent_respects_lab_agent_once_env"),
    ('User{Name: "alex", Role: "oncall"}', 'User{Name: "alex", Role: "oncall"}'),
    ('User{Name: "alex", Role: "engineer"}', 'User{Name: "alex", Role: "engineer"}'),
    ('want := "Hello, alex (engineer)"', 'want := "Hello, alex (engineer)"'),
    ("Local systems engineering practice lab", "Local systems engineering practice lab"),
]


def should_process(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    return path.suffix.lower() in EXTENSIONS


def main() -> None:
    changed: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or not should_process(path):
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(path)
            print(f"updated {path.relative_to(ROOT)}")
    print(f"\nDone. {len(changed)} files updated.")


if __name__ == "__main__":
    main()
