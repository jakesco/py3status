prog = py3status.py

fix:
	black $(prog) && ruff --fix $(prog)

lint:
	ruff $(prog)

install:
	cp $(prog) ${HOME}/.local/bin/$(prog)

update-deps:
	python -m pip install --upgrade pip-tools pip setuptools wheel
	pip-compile --upgrade --resolver backtracking -o requirements.txt pyproject.toml
	pip-compile --extra dev --upgrade --resolver backtracking -o requirements-dev.txt pyproject.toml

.PHONY: fix lint install update-deps
