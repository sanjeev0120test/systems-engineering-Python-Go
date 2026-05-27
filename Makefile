.PHONY: setup lint test test-all run-step check-step

PYTHON := .venv/bin/python
PIP := .venv/bin/pip

setup:
	bash setup.sh

lint:
	$(PYTHON) -m ruff check python/
	$(PYTHON) -m black --check python/
	$(PYTHON) -m mypy python/common python/01_python_basics python/02_file_handling python/03_json_yaml python/04_logging || true

test:
	$(PYTHON) -m pytest python/ -q

test-all:
	bash check.sh all

run-step:
	@test -n "$(STEP)" || (echo "Usage: make run-step STEP=1" && exit 1)
	bash run.sh $(STEP)

check-step:
	@test -n "$(STEP)" || (echo "Usage: make check-step STEP=1" && exit 1)
	bash check.sh $(STEP)
