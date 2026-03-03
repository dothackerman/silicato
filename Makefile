.PHONY: install install-dev format lint check

install:
	python3 -m pip install -r requirements.txt

install-dev:
	python3 -m pip install -r requirements.txt -r requirements-dev.txt

format:
	ruff format .

lint:
	ruff check .

check: format lint
