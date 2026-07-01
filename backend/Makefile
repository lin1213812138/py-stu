.PHONY: dev test lint typecheck build shell

PYTHON = .venv\Scripts\python

dev:
	$(PYTHON) -m uvicorn app.main:app --reload

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy .

build:
	$(PYTHON) -m hatch build

shell:
	$(PYTHON)
