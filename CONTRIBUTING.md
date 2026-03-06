# Contributing

Thanks for contributing to Silicato.

## Scope and support policy

Please keep contributions aligned with current release scope:
- push-to-talk transcription flow
- optional preview mode (`--preview`)
- tmux + terminal agent CLI transport model

Support policy:
- Official: TUXEDO OS 24.04 LTS
- Best effort: Ubuntu 24.04-compatible environments

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
make install-dev
make hooks
```

Install system packages if needed:

```bash
sudo apt update
sudo apt install -y alsa-utils ffmpeg python3-venv tmux
```

## Branch and commit rules

Branch names:
- `feat/<slug>`
- `fix/<slug>`
- `docs/<slug>`
- `refactor/<slug>`
- `test/<slug>`
- `chore/<slug>`

Commit messages must follow Conventional Commits:
- `feat(scope): ...`
- `fix(scope): ...`
- `docs(scope): ...`
- `refactor(scope): ...`
- `test(scope): ...`
- `chore(scope): ...`

## Required quality checks

Run during development:

```bash
make test-arch
make test-rules-fast
```

Blocking checks before merge:

```bash
make check
make test-rules-fast
make gate
make test-rules
```

## RC release workflow (maintainers)

Use the dedicated runbook:
- [RC Release Runbook](docs/dev/release-rc.md)

Primary commands:
- `make release-test VERSION=<version>`
- `make release-prod VERSION=<version>`

The runbook covers:
- Trusted Publishing setup values for PyPI and TestPyPI
- GitHub environment requirements
- local preflight + gate behavior

## Architecture boundaries

Keep dependency direction strict:
- `ui -> application -> domain`
- `application -> ports`
- `adapters -> ports`
- `ui -> adapters` for composition only

Do not import adapters from application/domain.

## Reporting bugs and proposing features

- Use GitHub issue templates.
- For bug reports, include:
  - OS and version
  - terminal emulator
  - tmux version
  - agent CLI + version
  - exact reproduction steps

## Security issues

For security disclosures, follow the process in [SECURITY.md](SECURITY.md).
