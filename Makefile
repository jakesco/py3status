fix:
	black py3status.py && ruff --fix py3status.py

lint:
	ruff py3status.py

update-deps:
	python -m pip install --upgrade pip-tools pip setuptools wheel
	pip-compile --extra dev --upgrade --resolver backtracking -o requirements-dev.txt pyproject.toml

.PHONY: fix lint test update-deps
