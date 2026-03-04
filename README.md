# Dialogos

Dialogos creates a local voice channel from Linux microphone input to a selected Codex tmux pane:
1. Push-to-talk capture
2. Local transcription with `faster-whisper`
3. Full confirm control before send
4. Send confirmed text to tmux
5. Persist target/config and JSONL turn logs

Milestone status: **Milestone 2 architecture migration target** (runtime behavior from Milestone 1 remains unchanged).

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
- [ADR Index](docs/dev/adr/README.md)

## Development commands

```bash
make install
make install-dev
make hooks
make alpha-preview
make alpha-reset
make test-arch
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
- [Patterns Deep Dive](docs/dev/patterns-deep-dive.md)
- [ADR Index](docs/dev/adr/README.md)
- [Deferred Ideas](docs/dev/deferred-ideas.md)

## License

MIT. See [LICENSE](LICENSE).
