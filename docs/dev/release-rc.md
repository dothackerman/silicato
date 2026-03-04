# RC Release Runbook

This runbook covers `0.1.0rc1`-style release candidate publication and validation.

## Scope guardrails

Do not add product features during RC release work. Keep scope locked to:
- push-to-talk flow
- optional `--preview` flow
- existing tmux target/config/logging/doctor behavior

## Prerequisites

- Python 3.12+
- `.venv` with dev dependencies (`make install-dev`)
- TestPyPI account
- TestPyPI API token in `.env` as `TEST_PYPI_TOKEN`
- `pipx` installed and available in `PATH`

## Create TestPyPI token

1. Sign in at `https://test.pypi.org/`.
2. Open Account Settings -> API tokens.
3. Create a new token (project-scoped token preferred).
4. Copy token once and store locally in `.env`:

```bash
TEST_PYPI_TOKEN=pypi-<token-value>
```

Do not commit `.env` and do not print token values in terminal logs.

Legacy local setups may still use `TEST_PYPI_API_TOKEN`. If present, either rename it to
`TEST_PYPI_TOKEN` or export a compatibility alias before upload:

```bash
export TEST_PYPI_TOKEN="${TEST_PYPI_TOKEN:-${TEST_PYPI_API_TOKEN:-}}"
```

## Load local env vars

```bash
set -a
source .env
set +a
```

Sanity check without printing secrets:

```bash
[ -n "${TEST_PYPI_TOKEN:-${TEST_PYPI_API_TOKEN:-}}" ] && echo "token present" || echo "token missing"
```

## Build and metadata check

```bash
rm -rf dist build *.egg-info src/*.egg-info
python3 -m build
python3 -m twine check dist/*
```

## Required quality gates

```bash
make check
make test-rules-fast
make gate
make test-rules
```

## Upload to TestPyPI

```bash
TWINE_USERNAME=__token__ \
TWINE_PASSWORD="${TEST_PYPI_TOKEN:-${TEST_PYPI_API_TOKEN:-}}" \
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

## pipx validation from TestPyPI

```bash
pipx install --index-url https://test.pypi.org/simple --pip-args='--extra-index-url https://pypi.org/simple' dialogos==0.1.0rc1

dialogos --doctor
dialogos --help
```

## Manual UX acceptance

Run both:
1. one normal-mode turn end-to-end
2. one preview-mode turn end-to-end

Verify transcript send does not require extra manual Enter.

## Stop point before real PyPI

Do not upload to real PyPI until explicit user go/no-go is given after manual UX signoff.
