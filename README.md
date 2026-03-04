# Dialogos

Dialogos is a Linux voice bridge from push-to-talk microphone input to a selected Codex tmux pane.

Current release candidate: `0.1.0rc1`.

## Supported Platforms

- Official support: TUXEDO OS 24.04 LTS (Ubuntu noble base)
- Best effort: Ubuntu 24.04-compatible Linux environments

Validated baseline for this RC:
- OS: TUXEDO OS 24.04.4 LTS
- Python: 3.12.3
- tmux: 3.4
- Codex CLI: 0.107.0

## Release Scope

`0.1.0rc1` is intentionally limited to the current feature set:
- Push-to-talk transcription flow
- Optional preview mode (`--preview`) for `send/edit/retry/skip/quit`
- Required tmux + Codex CLI workflow
- Existing target resolution, config persistence, JSONL logging, and doctor diagnostics

Out of scope for this RC:
- Always-on mode
- Spoken replies (TTS)
- Non-Linux platform support

## Capabilities

- Local speech capture via `arecord`
- Local transcription via `faster-whisper`
- Language selection: `en`, `de`, `auto`
- tmux pane target selection with persisted default target
- Normal mode: direct send after transcription
- Preview mode: review/edit/retry/skip/quit before send
- Runtime diagnostics via `dialogos --doctor`
- Local JSONL turn logging

## Limitations

- Linux and tmux are mandatory
- Codex CLI must run in a tmux pane
- No always-on listening mode
- No spoken output mode
- Turn logs may contain transcript text and stay local on disk

## Install

### RC install from TestPyPI (recommended for `0.1.0rc1` validation)

```bash
pipx install --index-url https://test.pypi.org/simple --pip-args='--extra-index-url https://pypi.org/simple' dialogos==0.1.0rc1
```

### Source install

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
make install-dev
```

### Final release install (after `0.1.0` publish)

```bash
pipx install dialogos
```

## Quick Start

Install required system packages:

```bash
sudo apt update
sudo apt install -y alsa-utils ffmpeg python3-venv tmux
```

Run diagnostics:

```bash
dialogos --doctor
```

Run normal mode:

```bash
dialogos
```

Run preview mode:

```bash
dialogos --preview
```

Normal mode sends directly after transcription. Preview mode requires explicit confirmation.

## Known Issues

### Codex submit timing in tmux

Status:
- Dialogos mitigates this by splitting text send and submit key send with a short delay.
- The issue has been observed with Codex CLI in tmux on Linux.

Symptom:
- Transcript text appears in Codex input but is not submitted until manual Enter.

Current mitigation in Dialogos:
1. Send transcript text first.
2. Wait briefly.
3. Send Enter as a separate tmux operation.

If you still see this behavior, open a bug report and include:
- OS distribution and version
- terminal emulator
- tmux version
- Codex CLI version
- exact reproduction steps

## Commands

```bash
make install
make install-dev
make hooks
make test-arch
make check-rules
make test-rules-fast
make test-rules
make check
make test-fast
make test
make gate
```

## Documentation

User docs:
- [Quickstart](docs/user/quickstart.md)
- [Capabilities](docs/user/capabilities.md)
- [Dependencies](docs/user/dependencies.md)
- [Alpha Preview](docs/user/alpha-preview.md)
- [Feedback Template](docs/user/feedback-template.md)

Developer docs:
- [Architecture](docs/dev/architecture.md)
- [Patterns Quickstart](docs/dev/patterns-quickstart.md)
- [Dependency Rules](docs/dev/dependency-rules.md)
- [Business Rules](docs/dev/business-rules.md)
- [RC Release Runbook](docs/dev/release-rc.md)

Project docs:
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## License

MIT. See [LICENSE](LICENSE).
