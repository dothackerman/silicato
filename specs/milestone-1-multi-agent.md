# Dialogos Milestone 1 - Multi-Agent Execution Plan

## Summary
Build milestone 1 as a production-ready, local-first voice input channel to Codex on Linux:
1. Push-to-talk capture.
2. Local transcription (`faster-whisper`).
3. Full confirm control before send.
4. Send confirmed text to a selected tmux pane.
5. Persist target/config and JSONL logs.
6. Enforce local quality gates with hardware tests blocking.

This plan is optimized for parallel subagent work with strict file ownership and deterministic handoffs.

## Scope
1. In scope:
- tmux mandatory transport.
- Interactive tmux pane picker.
- Remember selected pane by default.
- Guided setup message when no tmux session exists.
- Confirm menu with full control.
- Optional preview mode.
- `pyproject`-only dependency management.
- User/agent/dev docs updates.

2. Out of scope:
- Always-on voice mode (silence segmentation).
- TTS reply audio.
- Telemetry/usage metrics.
- Cloud CI.

## Locked Product Decisions
1. Dependencies: use only `pyproject.toml` (`requirements*.txt` removed).
2. Confirm flow:
- Normal mode: `Enter=send`, `e=edit`, `r=retry`, `s=skip`, `q=quit`.
- Preview mode (`--preview`): explicit send only.
3. tmux selection:
- Startup picker by index (no tmux syntax needed for user).
- Remember pane by default.
- Optional explicit target via CLI/env.
4. If no tmux session: print guided setup and exit.
5. Logs: JSONL local file.
6. Languages: `de`, `en`, `auto`.

## Public Interfaces (Decision Complete)
1. Command:
- `dialogos` (also `python3 -m dialogos`)

2. New CLI options:
- `--tmux-target <target>`
- `--pick-target`
- `--no-remember-target`
- `--preview`
- `--log-file <path>`

3. Environment variable:
- `DIALOGOS_TMUX_TARGET` as fallback target source.

4. Config file:
- `$XDG_CONFIG_HOME/dialogos/config.toml` fallback `~/.config/dialogos/config.toml`
- Key: `tmux_target`

5. Log file default:
- `$XDG_STATE_HOME/dialogos/turns.jsonl` fallback `~/.local/state/dialogos/turns.jsonl`

## tmux UX and Behavior
1. Target resolution order:
- `--tmux-target` -> `DIALOGOS_TMUX_TARGET` -> remembered config target -> picker.
2. Picker source:
- `tmux list-panes -a -F "#{session_name}:#{window_index}.#{pane_index}\t#{pane_current_command}\t#{pane_title}"`
3. Validation:
- `tmux list-panes -t <target>` before first send.
4. Send operation:
- `tmux send-keys -t <target> "<text>" C-m`
5. No tmux running:
- Show:
  - `tmux new -s codex`
  - start Codex in that session
  - rerun Dialogos
- Exit non-zero.

## Agent Work Partition (No Overlap)
1. Builder A - tmux Targeting
- Owns: `src/dialogos/tmux_picker.py`, `src/dialogos/adapters/tmux_sender.py`, related tests.
- Delivers: pane listing, interactive picker, validation, send wrapper.

2. Builder B - Turn Interaction
- Owns: `src/dialogos/cli.py`, `src/dialogos/orchestrator.py`, related tests.
- Delivers: confirm menu, preview behavior, edit/retry/skip/quit flow, action outcomes.

3. Builder C - Config and Logging
- Owns: `src/dialogos/config.py`, `src/dialogos/logging_jsonl.py`, related tests.
- Delivers: config persistence, remembered target handling, structured JSONL logging.

4. Quality Agent
- Owns: gate and policy verification only.
- Files: `Makefile`, `.githooks/*`, `pyproject.toml` checks only if needed.
- Delivers: maintainability review, legibility review, test rigor review, final gate evidence.

5. Docs Agent
- Owns: `README.md`, `docs/user/*`, `docs/agents/*`, `docs/dev/*`, `specs/mvp-push-to-talk.md`.
- Delivers: complete docs alignment with final behavior.

6. Integrator (lead session)
- Owns merge sequencing, conflict resolution, final acceptance verification.

## Parallelization and Merge Order
1. Batch 1 (parallel):
- Builder A, Builder B, Builder C start concurrently.
2. Batch 2:
- Integrator rebases and resolves integration points.
3. Batch 3:
- Quality Agent review + fixes.
4. Batch 4:
- Docs Agent final sync.
5. Batch 5:
- Final `make gate` on host hardware, then push.

## Subagent Handoff Contract (Mandatory)
Each subagent must return exactly:
1. `changed_files`: explicit file list.
2. `behavior_summary`: what changed functionally.
3. `tests_run`: command + result.
4. `assumptions`: explicit assumptions made.
5. `risks`: known residual risks.
6. `out_of_scope`: items intentionally not handled.

## Testing Plan
1. Unit tests:
- confirm menu action transitions.
- preview mode explicit-send behavior.
- tmux target parse/validate and picker selection.
- config load/save fallback paths.
- JSONL log schema and append behavior.

2. Integration tests (fake adapters):
- end-to-end turn with send/edit/retry/skip paths.
- remembered target reuse and override behavior.

3. Hardware tests (blocking):
- tmux available.
- tmux send smoke test to temporary pane.
- ALSA capture device present.

4. Gate:
- `make check`
- `make test-fast`
- `make gate` (must pass on real host before merge)

## Dependency Migration Plan (pyproject-only)
1. Update `pyproject.toml`:
- runtime in `[project.dependencies]`
- dev extras in `[project.optional-dependencies].dev`
2. Remove:
- `requirements.txt`
- `requirements-dev.txt`
3. Update `Makefile` install targets:
- `make install` => `python -m pip install -e .`
- `make install-dev` => `python -m pip install -e .[dev]`
4. Update docs commands accordingly.

## Acceptance Criteria
1. User can complete: speak -> transcript -> confirm -> send to Codex pane.
2. Picker works for first-time tmux users.
3. Remembered pane works and can be overridden.
4. No tmux gives clear guided setup instructions.
5. Preview mode enforces explicit send.
6. JSONL logs written with required fields.
7. `make gate` passes on host with real tmux/audio.

## Assumptions and Defaults
1. Platform target: Ubuntu/TUXEDO first.
2. Default STT mode: CPU-safe (`--device cpu`, `--compute-type int8`).
3. Offline-capable after model download.
4. No telemetry.
5. English-only docs.
6. Conventional commits + branch naming rules remain enforced.
