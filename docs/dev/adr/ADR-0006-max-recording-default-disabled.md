# ADR-0006 Max Recording Default Disabled

Status: Accepted
Date: 2026-03-11

## Context

ADR-0005 established a bounded-recording fallback with an enabled default.
Operator feedback clarified that default behavior should prioritize explicit
manual/silence stop behavior and avoid hidden hard caps unless requested.

The project still needs deterministic fallback capability for environments that
want enforced recording limits.

## Decision

1. Keep max-duration fallback as a supported feature via
   `--max-recording-seconds`.
2. Change the default max-duration fallback to `0` (disabled).
3. Keep silence-stop behavior unchanged and independently configurable.
4. Keep `max_recording_seconds > 0` semantics unchanged when users opt in.

## Consequences

Positive:
- default behavior aligns with operator expectation of no hidden hard cap
- limit policy becomes explicit opt-in at runtime

Negative / tradeoffs:
- if silence-stop fails and no max-duration is configured, recording can run
  until manual interruption
- users in noisy environments may need to set an explicit cap for guardrails

## Alternatives considered

1. Keep enabled default cap and rely on documentation only
- Rejected: violates explicit operator intent and can feel like hidden policy.

2. Remove max-duration feature entirely
- Rejected: removes a useful safety control for teams that want strict bounds.

3. Tie max-duration automatically to silence settings
- Rejected: couples independent controls and reduces clarity.
