# Silicato

Silicato is a Linux voice bridge from push-to-talk microphone input to a selected AI-agent tmux pane.

Current release candidate: `0.1.0rc3`.

## Supported Platforms

- Official support: TUXEDO OS 24.04 LTS (Ubuntu noble base)
- Best effort: Ubuntu 24.04-compatible Linux environments

Validated baseline for this RC:
- OS: TUXEDO OS 24.04.4 LTS
- Python: 3.12.3
- tmux: 3.4
- Agent CLIs: Codex CLI 0.107.0 and Claude Code (manual validation)

## Release Scope

`0.1.0rc3` is intentionally limited to the current feature set:
- Push-to-talk transcription flow
- Optional preview mode (`--preview`) for `send/edit/retry/skip/quit`
- Required tmux + terminal agent CLI workflow
- Existing target resolution, config persistence, JSONL logging, and doctor diagnostics

Out of scope for this RC:
- Always-on mode
- Spoken replies (TTS)
- Non-Linux platform support

## Capabilities

- Push-to-talk capture controls: press Enter to start recording, then Enter again to stop
- Local speech capture via `arecord`
- Local transcription via `faster-whisper`
- Language selection: `en`, `de`, `auto`
- tmux pane target selection via interactive picker by default (`--reuse-target` to opt into env/config fallback)
- Normal mode: direct send after transcription without local transcript echo
- Preview mode: review/edit/retry/skip/quit before send
- Runtime diagnostics via `silicato --doctor`
- Hardware-aware spawn profile via `silicato --spawn` for 3-4 parallel sessions
- Local JSONL turn logging

## Limitations

- Linux and tmux are mandatory
- A terminal agent CLI (for example Codex or Claude Code) must run in a tmux pane
- Explicit tmux targets must be pane-scoped (`session:window.pane` or `%pane_id`)
- No always-on listening mode
- No spoken output mode
- Turn logs may contain transcript text and stay local on disk

## Install

### Install from PyPI (`0.1.0rc3`)

```bash
pipx install silicato==0.1.0rc3
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
pipx install silicato
```

Maintainer-only TestPyPI validation steps live in `docs/dev/release-rc.md`.

## Quick Start

Install required system packages:

```bash
sudo apt update
sudo apt install -y alsa-utils ffmpeg python3-venv tmux
```

Run diagnostics:

```bash
silicato --doctor
```

Run normal mode:

```bash
silicato
```

Run spawn profile (recommended for 3-4 parallel instances on constrained GPUs):

```bash
silicato --spawn
# alias for: silicato --profile spawn
```

Interactive turn controls:
- Press Enter to start recording.
- Press Enter again to stop recording and transcribe.
- Type `q` then Enter at the turn prompt to quit.

Run preview mode:

```bash
silicato --preview
# short form:
silicato -p
```

Normal mode sends directly after transcription and does not print the transcript locally.
Preview mode requires explicit confirmation and shows transcript text for review.

## Known Issues

### Agent submit timing in tmux

Status:
- Silicato mitigates this by splitting text send and submit key send with a short delay.
- The issue has been observed with terminal agent UIs in tmux on Linux.

Symptom:
- Transcript text appears in the agent input but is not submitted until manual Enter.

Current mitigation in Silicato:
1. Send transcript text first.
2. Wait briefly.
3. Send Enter as a separate tmux operation.

If you still see this behavior, open a bug report and include:
- OS distribution and version
- terminal emulator
- tmux version
- Agent CLI + version (for example Codex CLI or Claude Code)
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
make test-e2e-tmux
make test
make gate
make release-test VERSION=<version>
make release-prod VERSION=<version>
```

Checks reference:
- `docs/dev/repo-checks.md`

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
- [Repository Checks](docs/dev/repo-checks.md)
- [RC Release Runbook](docs/dev/release-rc.md)

Project docs:
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## License

MIT. See [LICENSE](LICENSE).
