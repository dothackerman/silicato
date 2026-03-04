# Dialogos

Dialogos creates a local voice channel from Linux microphone input to a selected Codex tmux pane:
1. Push-to-talk capture
2. Local transcription with `faster-whisper`
3. Full confirm control before send
4. Send confirmed text to tmux
5. Persist target/config and JSONL turn logs

Milestone status: **Milestone 3 agent-first hardening in progress** (runtime behavior from Milestone 1 remains unchanged).

## Why the name "Dialogos"?

"Dialogos" comes from the Greek root associated with dialogue and exchange.
The project goal matches that meaning: a natural conversational channel between human speech and Codex.

## Alpha preview (recommended for now)

From a fresh clone:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
make install-dev
make alpha-preview
```

Useful alpha commands:

```bash
make alpha-preview-no-run
make alpha-reset
```

`make alpha-preview` now defaults to a higher-quality alpha profile (`small` + `cuda` + `float16`) with automatic CPU fallback if CUDA runtime is unavailable.
If model download warns about unauthenticated Hugging Face access, set `HF_TOKEN=hf_xxx` (see `docs/user/alpha-preview.md`).
Normal mode sends transcripts directly; add `--preview` to enable confirm/edit/retry/skip before sending.

## Known Issue: Codex TUI Submit Timing

### Status
- Mitigated in Dialogos sender logic by splitting text send and submit key send.
- Relevant to Codex CLI in tmux (observed with `codex-cli 0.107.0` on Linux).

### Symptom
- Transcript text appears in Codex input.
- Prompt is not submitted until user manually presses Enter.

### Expected behavior
- User should only press Enter to start/stop recording.
- Dialogos should submit the injected prompt automatically.

### Root-cause observations
- In generic tmux panes (bash/python/readline), a single call works:
  - `tmux send-keys -t <target> "<text>" C-m`
- In Codex TUI panes, single-call send was intermittently not submitted.
- Reliable pattern in Codex TUI:
  1. `tmux send-keys -t <target> "<text>"`
  2. short delay (about 50ms)
  3. `tmux send-keys -t <target> Enter`

### Reproduction notes for TUI maintainers
Use an isolated tmux session (do not use your working pane):

```bash
tmux new-session -d -s codex-diag "codex"
sleep 10

# often text-injected but not submitted in Codex TUI
tmux send-keys -t codex-diag:0.0 "diag-single-call" C-m

# reliably submitted in Codex TUI
tmux send-keys -t codex-diag:0.0 "diag-split-call"
sleep 0.05
tmux send-keys -t codex-diag:0.0 Enter
```

Optional verification: inspect `~/.codex/sessions` for presence of unique sent tokens.

### Dialogos mitigation
- Sender now performs split send with a short delay before submit key.
- If you still observe missed submits in your environment, report:
  - Codex CLI version
  - tmux version
  - terminal emulator
  - whether a larger delay (for example 100ms) resolves it

## Spec treatment

Specs under `specs/` are historical implementation plans.
Once implemented and merged, they remain immutable records.
Current behavior belongs in README and docs.

## Architecture snapshot

Target dependency direction is strict:
- `ui -> application -> domain`
- `application -> ports`
- `adapters -> ports`
- `ui` composes adapters and wires use-cases

Reference docs:
- [Architecture](docs/dev/architecture.md)
- [Patterns Quickstart](docs/dev/patterns-quickstart.md)
- [Dependency Rules](docs/dev/dependency-rules.md)
- [Business Rules](docs/dev/business-rules.md)
- [ADR Index](docs/dev/adr/README.md)

## Development commands

```bash
make install
make install-dev
make hooks
make alpha-preview
make alpha-reset
make test-arch
make check-rules
make test-rules-fast
make test-rules
make check
make test-fast
make test
make gate
```

## Documentation map

### User-facing
- [Quickstart](docs/user/quickstart.md)
- [Alpha Preview](docs/user/alpha-preview.md)
- [Feedback Template](docs/user/feedback-template.md)
- [Capabilities](docs/user/capabilities.md)
- [Dependencies](docs/user/dependencies.md)

### Agent-facing
- [Agent Roles](docs/agents/roles.md)
- [Agent Workflow](docs/agents/workflow.md)
- [New Session Handoff](docs/agents/new-session-handoff.md)

### Developer-only
- [Architecture](docs/dev/architecture.md)
- [Patterns Quickstart](docs/dev/patterns-quickstart.md)
- [Dependency Rules](docs/dev/dependency-rules.md)
- [Business Rules](docs/dev/business-rules.md)
- [Patterns Deep Dive](docs/dev/patterns-deep-dive.md)
- [ADR Index](docs/dev/adr/README.md)
- [Deferred Ideas](docs/dev/deferred-ideas.md)

## License

MIT. See [LICENSE](LICENSE).
