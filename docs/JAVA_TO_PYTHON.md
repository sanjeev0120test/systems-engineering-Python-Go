# Java → Python Cheat Sheet (for systems engineering)

| Java | Python | Notes |
|------|--------|-------|
| `public static void main` | `if __name__ == "__main__":` | Script entry point |
| `String s = "x"` | `s: str = "x"` | Type hints optional at runtime |
| `null` | `None` | Use `Optional[T]` or `T \| None` |
| `try/catch` | `try/except` | Python prefers EAFP over LBYL |
| `try-with-resources` | `with open(...) as f:` | Context managers |
| `List<String>` | `list[str]` | Lowercase generics (3.9+) |
| `Map<K,V>` | `dict[K, V]` | |
| `interface` | duck typing / `Protocol` | No formal interface required |
| `ExecutorService` | `ThreadPoolExecutor`, `asyncio` | GIL limits CPU threading |
| Maven/Gradle deps | `venv` + `pip install -r requirements.txt` | One venv per project |
| SLF4J + Logback | `logging` + `JsonFormatter` | See Step 9 |
| Spring `@RestController` | FastAPI `@app.get` | Lighter, async-native |
| `String.format` | f-strings `f"{x}"` | Preferred in modern Python |
| checked exceptions | none | Document in docstrings instead |

## Production engineering mindset shift

- **Automation:** Python replaces bash for anything with logic branches or JSON output.
- **Observability:** Always log with `trace_id`; never bare `print()` in tools.
- **Reliability:** Timeouts on every network/subprocess call; retries with backoff.
- **Config:** 12-factor — env vars override YAML files.
