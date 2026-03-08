# Capabilities

## RC3 scope (`0.1.0rc3`)

In scope:
- Push-to-talk speech capture with Enter start/stop
- Local transcription via `faster-whisper`
- Language selection: `de`, `en`, `auto`
- tmux pane selection at startup by default, with optional env/config reuse mode
- Reuse mode validation: invalid `SILICATO_TMUX_TARGET` exits with error; invalid remembered target falls back to picker
- Normal mode direct send after transcription (without local transcript echo)
- Preview mode (`--preview`) with `send/edit/retry/skip/quit`
- Local JSONL turn logs
- Runtime diagnostics (`silicato --doctor`)
- Hardware-aware spawn profile (`silicato --spawn`) for multi-instance stability

## Spawn profile behavior

`silicato --spawn` (alias: `--profile spawn`) auto-tunes model/device/compute type to make
3-4 parallel local sessions realistic on the detected hardware.

Current preset strategy:
- No NVIDIA GPU detected: `small + cpu + int8`
- <5GB VRAM: `tiny + cuda + int8_float16`
- 5GB-12GB VRAM: `small + cuda + int8_float16`
- >=12GB VRAM: `base + cuda + int8_float16`

For 6GB GPUs (for example RTX 3060 Laptop), expected resolution is:
`small + cuda + int8_float16`.

## Required runtime model

- Linux terminal workflow
- Terminal agent CLI running inside tmux (for example Codex or Claude Code)
- Silicato injects transcript text into selected tmux pane and submits the prompt

## Out of scope for RC3

- Always-on mode with silence segmentation
- Spoken assistant replies (TTS)
- Non-Linux platform support
- Cloud-only runtime dependencies

## Support policy

- Official support: TUXEDO OS 24.04 LTS
- Best effort: Ubuntu 24.04-compatible Linux environments
