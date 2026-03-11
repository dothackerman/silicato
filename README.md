# Silicato

Silicato is a Linux voice bridge from push-to-talk microphone input to a selected AI-agent tmux pane.

Current release candidate: `0.1.0rc5`.

## At A Glance

Silicato captures one push-to-talk turn, transcribes locally, and sends text
to a chosen tmux pane where your agent CLI is running.

Best fit:
- Linux terminal workflow
- tmux-based agent usage (Codex CLI, Claude Code, similar)
- local speech-to-text with `faster-whisper`

Not in scope:
- always-on listening
- spoken replies (TTS)
- non-Linux support

## Quick Links

- User quickstart: [docs/user/quickstart.md](docs/user/quickstart.md)
- Capabilities: [docs/user/capabilities.md](docs/user/capabilities.md)
- Dependencies: [docs/user/dependencies.md](docs/user/dependencies.md)
- RC release runbook (maintainers): [docs/dev/release-rc.md](docs/dev/release-rc.md)
- Full checks matrix: [docs/dev/repo-checks.md](docs/dev/repo-checks.md)

## Choose Your Path

### I want to use stable (`pipx`)

```bash
pipx install silicato
```

### I want to use the current RC (`pipx`)

```bash
pipx install silicato==0.1.0rc5
```

### I want to clone and run from source

```bash
git clone https://github.com/dothackerman/silicato.git
cd silicato
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
make install-dev
```

### I am a maintainer and want to publish (GitHub Actions)

```bash
make release-test VERSION=<version>
make release-prod VERSION=<version>
```

These commands dispatch `.github/workflows/release.yml`:
- `make release-test`: TestPyPI publish + GitHub prerelease
- `make release-prod`: PyPI publish + GitHub release

Trusted Publishing setup, environments, and release flow:
- [docs/dev/release-rc.md](docs/dev/release-rc.md)

## Supported Platforms

- Official support: TUXEDO OS 24.04 LTS (Ubuntu noble base)
- Best effort: Ubuntu 24.04-compatible Linux environments

Validated baseline for this RC:
- OS: TUXEDO OS 24.04.4 LTS
- Python: 3.12.3
- tmux: 3.4
- Agent CLIs: Codex CLI 0.107.0 and Claude Code (manual validation)

## First Run (60 seconds)

Install system dependencies:

```bash
sudo apt update
sudo apt install -y alsa-utils ffmpeg python3-venv tmux
```

Start your agent CLI in tmux, then verify runtime:

```bash
silicato --doctor
silicato
```

Turn controls:
- Enter starts recording
- long pause stops recording
- Enter during recording stops manually
- `q` then Enter at start prompt exits

## Common Commands

Run with spawn runtime profile (recommended for 3-4 parallel sessions on
constrained GPUs):

```bash
silicato --spawn
# alias for: silicato --profile spawn
```

Run with an external runtime plugin:

```bash
silicato --profile my-custom-plugin
```

Preview mode:

```bash
silicato --preview
# short form:
silicato -p
```

Route management:

```bash
silicato route add gaia codex:0.1
silicato route list
silicato route check gaia
silicato inject --to gaia --text "status check"
```

Useful tuning:
- `--silence-stop-seconds <seconds>` (default `1.4`)
- `--silence-rms-threshold <value>` (default `80`)
- `--max-recording-seconds <seconds>` enables hard-stop only when `> 0`
  (default `0`, disabled)

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

## Developer Command Reference

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

Checks matrix:
- [docs/dev/repo-checks.md](docs/dev/repo-checks.md)

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
