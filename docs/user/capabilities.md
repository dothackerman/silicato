# Capabilities

## RC1 scope (`0.1.0rc1`)

In scope:
- Push-to-talk speech capture with Enter start/stop
- Local transcription via `faster-whisper`
- Language selection: `de`, `en`, `auto`
- tmux pane selection and persisted default target
- Normal mode direct send after transcription
- Preview mode (`--preview`) with `send/edit/retry/skip/quit`
- Local JSONL turn logs
- Runtime diagnostics (`dialogos --doctor`)

## Required runtime model

- Linux terminal workflow
- Codex CLI running inside tmux
- Dialogos injects transcript text into selected tmux pane and submits the prompt

## Out of scope for RC1

- Always-on mode with silence segmentation
- Spoken assistant replies (TTS)
- Non-Linux platform support
- Cloud-only runtime dependencies

## Support policy

- Official support: TUXEDO OS 24.04 LTS
- Best effort: Ubuntu 24.04-compatible Linux environments
