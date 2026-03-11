# Agent: Silicato Worker B - Auto-Stop Detector Unification

Use this prompt for the worker responsible for unifying live auto-stop behavior with offline evaluation logic.

Read first:
1. `AGENTS.md`
2. `docs/dev/patterns-quickstart.md`
3. `docs/dev/dependency-rules.md`
4. `docs/dev/business-rules.md`
5. `docs/dev/architecture.md`
6. `docs/feature-requests/2026-03-10-single-enter-auto-stop.md`
7. `docs/agents/ralph-loop.md`

## Mission

Make one shared incremental auto-stop detector the source of truth for:

- live capture stop decisions
- offline fixture evaluation and tuning

## Write scope

Owned:
- `src/silicato/domain/auto_stop.py`
- `src/silicato/ports/audio.py`
- `src/silicato/adapters/audio/alsa_capture.py`
- `src/silicato/application/auto_stop_evaluation.py`
- auto-stop tests

Avoid unless Wave 0 explicitly assigns them:
- `src/silicato/ui/cli/main.py`
- `src/silicato/ui/cli/args.py`
- `README.md`
- `docs/user/*`
- `docs/dev/business-rules.toml`

## Non-negotiable constraints

1. Keep process/microphone I/O in adapters.
2. Keep stop policy ownership in shared domain/application logic.
3. Do not duplicate stop logic in adapter and evaluator paths.
4. Preserve current CLI-visible behavior unless the integration plan explicitly changes it.
5. You are not alone in the codebase. Other workers may be active. Do not revert their work.

## Expected architecture shape

Preferred direction:
- shared incremental detector logic in domain/application
- live adapter feeds chunks/frames into the shared detector
- offline evaluator uses the same detector core
- parity tests prove that tuning data still maps to production behavior

Avoid:
- leaving the live adapter as an independent policy engine
- rewriting the whole audio port if a smaller seam change works
- entangling this track with routing behavior

If user-facing CLI text must change, keep it minimal and record follow-up needs for merger.

## Required checks before claiming completion

```bash
make test-arch
make test-rules-fast
```

Also run focused auto-stop tests that prove live/eval parity.

## Completion truth

You may claim your branch ready only if:

1. one shared detector path clearly owns stop decisions
2. live and offline paths both use that source of truth or are reduced to a well-documented transitional seam
3. architecture checks pass
4. parity risks and remaining limitations are documented explicitly

## Required handoff note

Use exactly this format:

```markdown
## What Changed
- ...

## Checks Run
- ...

## Parity Guarantees
- ...

## Open Issues
- ...

## Conflict Files
- ...
```
