# Architecture

## Product name
Silicato.

Intent: enable a local-first communication channel between human speech and terminal AI-agent text workflows.

## Runtime posture
- Local-first and offline-capable after model download
- No telemetry
- Local JSONL turn logs only
- Milestone 3 hardening is behavior-preserving for Milestone 1 user flow

## Layered architecture target

### `src/silicato/domain/`
- Pure business state and transitions (no side effects)
- Owns turn state machine and confirm action semantics
- No filesystem/subprocess/env/terminal/network imports

### `src/silicato/application/`
- Use-case orchestration for turn flow
- Coordinates domain decisions and port calls
- May import `domain` and `ports`, never adapters

### `src/silicato/ports/`
- Typed interfaces for external capabilities
- Examples: audio capture, STT, sender, target resolver, config store, turn logger

### `src/silicato/adapters/`
- Concrete side-effect implementations (tmux, ALSA, whisper, storage)
- Implements `ports` contracts

### `src/silicato/ui/`
- CLI argument parsing, prompts, output rendering, and dependency wiring
- Entry points stay `silicato` and `python3 -m silicato`
- May compose adapters and call application use-cases

## Dependency direction (strict)

Allowed:
- `ui -> application`
- `application -> domain`
- `application -> ports`
- `adapters -> ports`
- `ui -> adapters` for composition only

Forbidden:
- `domain -> application|ui|adapters|ports`
- `application -> adapters|ui`
- `adapters -> application|domain|ui`
- `ui -> domain`

## Turn behavior
1. Resolve tmux target (`--tmux-target` -> picker by default, or `--reuse-target` mode: env -> remembered -> picker; invalid env fails fast, invalid remembered falls back to picker)
2. Validate target
3. Capture push-to-talk audio
4. Transcribe locally
5. Confirm action (`send/edit/retry/skip/quit`)
6. Send to tmux when confirmed
7. Append JSONL turn log event

## Quality and enforcement
- Use `make test-arch` for architecture boundary checks
- Use `make check-rules` to validate business-rule to regression-test mappings
- Use `make test-rules-fast` for non-hardware business-rule regressions
- Use `make test-rules` for full business-rule regressions (includes hardware)
- `make gate` remains the blocking local gate
- Architecture and rule checks are expected to run inside `make check`/`make gate`
- Checks matrix reference: `docs/dev/repo-checks.md`

## Testing taxonomy target
- `tests/unit`: pure logic and helpers
- `tests/contracts`: adapter compliance with port contracts
- `tests/integration`: multi-component behavior with fakes/stubs where possible
- `tests/hardware`: local runtime checks (tmux/ALSA)

## Knowledge gradient entrypoints
- Bootstrap: `docs/dev/patterns-quickstart.md`, `docs/dev/dependency-rules.md`
- Deep dive: `docs/dev/patterns-deep-dive.md`, `docs/dev/adr/*`
