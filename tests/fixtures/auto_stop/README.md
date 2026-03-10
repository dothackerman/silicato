# Auto-Stop Fixtures

This directory stores prerecorded WAV fixtures for deterministic auto-stop evaluation.

## Files

- `local/manifest.toml`: local generated fixture metadata and expected stop windows
- `local/wav/*.wav`: mono 16-bit recordings captured for endpointing evaluation
- `plans/*.toml`: guided prompt plans for structured recording sessions
- `local/diagnostics/*.json`: transcription sidecars with word timestamps and confidence data

## Recording guidance

Use short clips that reflect real Silicato usage:

1. normal pace
2. slow pace
3. quiet sentence ending
4. reflective pause mid-thought
5. filler pause (`um`, `so`)
6. louder voice
7. softer voice
8. mild background noise

Each clip should include enough trailing silence for the evaluator to observe the stop window.

## Annotation fields

Each fixture entry should include:

- `id`
- `wav`
- `script`
- `target_stop_seconds`
- `min_stop_seconds`
- `max_stop_seconds`
- `tags`
- `expected_transcript` (optional)

`target_stop_seconds` is the ideal moment a user would expect recording to end.
The min/max window defines acceptable UX around that point.

## Guided collection

To collect a structured fixture set without manual naming or manifest editing:

```bash
.venv/bin/python3 scripts/auto_stop_record.py --plan tests/fixtures/auto_stop/plans/de-en-core.toml --takes 2
```

This walks through each prompt, records the WAV, transcribes it, writes diagnostics, and updates `local/manifest.toml`.

## Git policy

The recording harness and plans are committed.
The generated recordings, diagnostics, and manifest under `local/` are intentionally gitignored because they are machine-local tuning data.
