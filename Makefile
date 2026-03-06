.PHONY: install install-dev hooks format lint typecheck check check-rules test-arch test-rules test-rules-fast test test-fast gate alpha-preview alpha-preview-no-run alpha-reset release-test release-prod

VENV_PYTHON := .venv/bin/python3

ifeq ($(wildcard $(VENV_PYTHON)),)
PYTHON := python3
else
PYTHON := $(VENV_PYTHON)
endif

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e .[dev]

hooks:
	chmod +x .githooks/commit-msg .githooks/pre-push scripts/validate_branch_name.sh
	git config core.hooksPath .githooks

format:
	$(PYTHON) -m ruff format .

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy src tests talk_to_codex.py

check: format lint typecheck test-arch check-rules

check-rules:
	$(PYTHON) scripts/business_rules.py check

test-arch:
	$(PYTHON) scripts/check_architecture.py

test-rules:
	$(PYTHON) scripts/business_rules.py test

test-rules-fast:
	$(PYTHON) scripts/business_rules.py test --fast

test:
	$(PYTHON) -m pytest

test-fast:
	$(PYTHON) -m pytest -m "not hardware"

gate: check test-rules-fast test-fast test

alpha-preview:
	./scripts/alpha_preview.sh

alpha-preview-no-run:
	./scripts/alpha_preview.sh --no-run

alpha-reset:
	./scripts/reset_alpha_state.sh --yes

release-test:
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make release-test VERSION=0.1.0rc3 [REF=main] [SKIP_GATE=1]"; \
		exit 1; \
	fi
	$(PYTHON) scripts/release_cli.py --channel test --version "$(VERSION)" --ref "$(if $(REF),$(REF),main)" $(if $(SKIP_GATE),--skip-gate,)

release-prod:
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make release-prod VERSION=0.1.0rc3 [REF=main] [SKIP_GATE=1]"; \
		exit 1; \
	fi
	$(PYTHON) scripts/release_cli.py --channel prod --version "$(VERSION)" --ref "$(if $(REF),$(REF),main)" $(if $(SKIP_GATE),--skip-gate,)
