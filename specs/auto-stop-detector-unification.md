# Silicato Spec - Auto-Stop Detector Unification

Status: Approved for implementation
Created on: 2026-03-10

## Problem

Silicato already has deterministic auto-stop evaluation logic, but live ALSA capture still owns a separate silence policy loop.
That split means fixture tuning can drift away from production behavior.

## Goal

Make one shared incremental auto-stop detector the source of truth for both live capture and offline evaluation.

## Frozen seam

1. Stop-policy ownership moves to one shared incremental detector in [`src/silicato/domain/auto_stop.py`](/home/oriol/Projects/private/silicato/src/silicato/domain/auto_stop.py).
2. Live ALSA capture feeds PCM chunks or RMS frames into that detector instead of implementing its own silence policy.
3. Offline evaluation reuses the same detector core rather than maintaining a separate decision path.
4. The existing audio capture port surface should stay stable in Wave 1 unless a smaller-safe change proves impossible.
5. Deterministic max-duration fallback belongs to the shared detector configuration, not to ad hoc adapter-only logic.

## Architecture shape

### Domain

- Introduce an incremental detector that can consume sequential frames and emit a stop decision when:
  - silence threshold is met
  - max-duration fallback is hit
  - auto-stop is disabled
- Existing batch helpers should become convenience wrappers over the same detector core, not a separate engine.

### Application

- [`src/silicato/application/auto_stop_evaluation.py`](/home/oriol/Projects/private/silicato/src/silicato/application/auto_stop_evaluation.py) must feed prerecorded WAV frames through the shared detector path.
- Evaluation scoring remains application-owned, but detector semantics come from the domain source of truth.

### Adapters

- [`src/silicato/adapters/audio/alsa_capture.py`](/home/oriol/Projects/private/silicato/src/silicato/adapters/audio/alsa_capture.py) stays responsible for microphone I/O, chunk reads, WAV persistence, and manual Enter interruption.
- It must stop delegating silence policy to adapter-local timers and RMS rules once the shared detector exists.
- If max-duration fallback triggers during live capture, the runtime must explain that stop reason explicitly.

### UI / Merger ownership

- Shared CLI text, docs, business rules, and integration tests remain merger-owned:
  - `src/silicato/ui/cli/main.py`
  - `src/silicato/ui/cli/args.py`
  - `README.md`
  - `docs/user/*`
  - `docs/dev/business-rules.toml`
  - cross-track integration tests

## Worker B scope

Owned for Wave 1:
- `src/silicato/domain/auto_stop.py`
- `src/silicato/adapters/audio/alsa_capture.py`
- `src/silicato/application/auto_stop_evaluation.py`
- `src/silicato/ports/audio.py` only if needed for a minimal seam clarification
- auto-stop unit/integration coverage that proves live/eval parity

## Non-goals

1. No second policy engine hidden in the adapter after unification.
2. No rewrite of unrelated capture/transcribe flow.
3. No coupling to routing work.

## Tradeoffs

1. Keeping the port stable reduces merger pressure, but it limits how richly live stop metadata can flow back to CLI code.
2. A conservative silence threshold avoids truncation, but it makes turns feel slightly slower.

## Failure modes to guard

1. Evaluation and live capture still diverge because one path bypasses the shared detector.
2. Max-duration fallback exists only in live capture and is impossible to replay offline.
3. Manual Enter interruption regresses because adapter stop handling becomes entangled with detector state.

## Acceptance criteria

1. One shared incremental detector clearly owns auto-stop decisions.
2. Live capture and offline evaluation both use that detector or a wrapper built directly on it.
3. Silence stop, no-speech, and max-duration behavior are covered by deterministic tests.
4. Existing preview/send behavior remains unchanged outside stop-trigger semantics.
