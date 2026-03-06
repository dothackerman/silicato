# RC Release Runbook

This runbook documents the manual-but-automated release flow for release candidates.

## Scope guardrails

Do not add product features during RC release work. Keep scope locked to:
- push-to-talk flow
- optional `--preview` flow
- existing tmux target/config/logging/doctor behavior

## Release model

Default release path:
- local preflight and gate via `make release-test` / `make release-prod`
- publish from GitHub Actions via Trusted Publishing (OIDC)
- no local PyPI/TestPyPI token usage in normal flow

Workflow file:
- `.github/workflows/release.yml`

## One-time setup outside this repository

### 1) GitHub environments

Create both environments in repository settings:
- `testpypi`
- `pypi-prod`

Recommended:
- add required reviewers to `pypi-prod`
- keep `testpypi` unblocked for faster RC loops

### 2) Trusted Publishers (PyPI + TestPyPI)

In the publisher form, use these values.

TestPyPI publisher:
- Owner: `dothackerman`
- Repository name: `silicato`
- Workflow name: `release.yml`
- Environment name: `testpypi`

PyPI publisher:
- Owner: `dothackerman`
- Repository name: `silicato`
- Workflow name: `release.yml`
- Environment name: `pypi-prod`

### 3) GitHub CLI auth

Ensure `gh` is authenticated locally:

```bash
gh auth status
```

## Local release commands

Test lane (publishes to TestPyPI + GitHub prerelease):

```bash
make release-test VERSION=0.1.0rc3
```

Prod lane (publishes to PyPI + GitHub release):

```bash
make release-prod VERSION=0.1.0rc3
```

Optional overrides:
- `REF=<git-ref>` to release from a ref other than `main`
- `SKIP_GATE=1` to skip local `make gate` (not recommended)

What the command does:
1. require clean git tree
2. verify `pyproject.toml` version matches `VERSION`
3. run local `make gate` (unless skipped)
4. dispatch `release.yml` with `workflow_dispatch`
5. watch workflow completion and return non-zero on failure

## Manual UX acceptance

Run both:
1. one normal-mode turn end-to-end
2. one preview-mode turn end-to-end

Verify transcript send does not require extra manual Enter.

## Break-glass fallback (not default)

If GitHub Actions publishing is unavailable, local Twine upload can still be used with local tokens.
Treat this as exception-only flow and rotate tokens after any accidental exposure.
