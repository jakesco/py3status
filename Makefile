fix:
	black py3status && ruff --fix py3status

lint:
	ruff py3status

test:
	python -m pytest tests/

update-deps:
	python -m pip install --upgrade pip-tools pip setuptools wheel
	pip-compile --extra dev --upgrade --resolver backtracking -o requirements-dev.txt pyproject.toml

.PHONY: fix lint test update-deps
