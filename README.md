# Silicato

Silicato is a Linux voice bridge from push-to-talk microphone input to a selected AI-agent tmux pane.

Current release candidate: `0.1.0rc5`.

## Supported Platforms

- Official support: TUXEDO OS 24.04 LTS (Ubuntu noble base)
- Best effort: Ubuntu 24.04-compatible Linux environments

Validated baseline for this RC:
- OS: TUXEDO OS 24.04.4 LTS
- Python: 3.12.3
- tmux: 3.4
- Agent CLIs: Codex CLI 0.107.0 and Claude Code (manual validation)

## Release Scope

`0.1.0rc5` is intentionally limited to the current feature set:
- Push-to-talk transcription flow
- Optional preview mode (`--preview`) for `send/edit/retry/skip/quit`
- Named tmux pane routing plus prompt injection by route identifier
- Runtime profile plugins (built-in `spawn`, external plugin discovery via entry points)
- Required tmux + terminal agent CLI workflow
- Existing target resolution, config persistence, JSONL logging, and doctor diagnostics

Out of scope for this RC:
- Always-on mode
- Spoken replies (TTS)
- Non-Linux platform support

## Capabilities

- Push-to-talk capture controls: press Enter to start recording, then auto-stop after a long pause (Enter still stops manually)
- Deterministic max-duration fallback so capture does not hang indefinitely
- Local speech capture via `arecord`
- Local transcription via `faster-whisper`
- Language selection: `en`, `de`, `auto`
- tmux pane target selection via interactive picker by default (`--reuse-target` to opt into env/config fallback)
- Named tmux pane routing via `silicato route ...`
- Prompt injection to a named route via `silicato inject --to <id> ...`
- Normal mode: direct send after transcription without local transcript echo
- Preview mode: review/edit/retry/skip/quit before send
- Runtime diagnostics via `silicato --doctor`
- Runtime plugin support via `--profile` (built-in `spawn`, plus external plugins)
- Hardware-aware spawn runtime plugin via `silicato --spawn` for 3-4 parallel sessions
- Local JSONL turn logging

## Limitations

- Linux and tmux are mandatory
- A terminal agent CLI (for example Codex or Claude Code) must run in a tmux pane
- Explicit tmux targets must be pane-scoped (`session:window.pane` or `%pane_id`)
- No always-on listening mode
- No spoken output mode
- Turn logs may contain transcript text and stay local on disk

## Install

### Install from PyPI (`0.1.0rc5`)

```bash
pipx install silicato==0.1.0rc5
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

Run spawn runtime plugin (recommended for 3-4 parallel instances on constrained GPUs):

```bash
silicato --spawn
# alias for: silicato --profile spawn
```

Run a custom runtime plugin (after installing a plugin package):

```bash
silicato --profile my-custom-plugin
```

Interactive turn controls:
- Press Enter to start recording.
- Recording stops automatically after a long pause in speech.
- Press Enter during recording to stop manually.
- Type `q` then Enter at the turn prompt to quit.

Optional tuning:
- `--silence-stop-seconds <seconds>` adjusts pause length before auto-stop (default `1.4`).
- `--silence-rms-threshold <value>` adjusts speech sensitivity for auto-stop (default `80`).
- Set `--silence-stop-seconds 0` to disable silence-based stop; manual Enter remains primary stop and the fixed max-duration fallback still prevents hangs.

Hot tip:
- If Silicato cuts you off too early, first try `--silence-rms-threshold 60` or `--silence-rms-threshold 40`.
- If Silicato waits too long to stop, first try `--silence-rms-threshold 120` or reduce `--silence-stop-seconds` to `1.2`.
- Use the guided local tuning workflow to collect and evaluate your own recordings:

```bash
.venv/bin/python3 scripts/auto_stop_record.py --plan tests/fixtures/auto_stop/plans/de-en-core.toml --takes 2
.venv/bin/python3 scripts/auto_stop_eval.py
```

Run preview mode:

```bash
silicato --preview
# short form:
silicato -p
```

Normal mode sends directly after transcription and does not print the transcript locally.
Preview mode requires explicit confirmation and shows transcript text for review.

Manage named routes:

```bash
silicato route add gaia codex:0.1
silicato route list
silicato route check gaia
```

Inject directly to a named route:

```bash
silicato inject --to gaia --text "status check"
silicato inject --to gaia --from-file ./prompt.txt
```

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
