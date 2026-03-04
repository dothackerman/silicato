# Capabilities

## Milestone 1 feature set (runtime behavior)
- Local push-to-talk speech capture (`arecord`)
- Local transcription via Whisper (`faster-whisper`)
- Language options: `de`, `en`, `auto`
- tmux mandatory transport (`tmux send-keys`)
- Interactive indexed tmux pane picker for first-time setup
- Remembered tmux target with CLI/env override support
- Confirm-before-send controls:
  - Normal mode: `Enter=send`, `e=edit`, `r=retry`, `s=skip`, `q=quit`
  - Preview mode: explicit send only (`y=send`)
- Local JSONL turn logging
- Runtime diagnostics (`--doctor`)

## Alpha preview helpers
- `make alpha-preview`: run diagnostics and start Dialogos with safe defaults
- `make alpha-preview-no-run`: diagnostics only
- `make alpha-reset`: remove local config/log state for first-run retests

## Out of scope right now
- Always-on voice mode with silence segmentation
- Spoken assistant replies (TTS)
- Cloud-only dependencies
- Telemetry/usage metrics
