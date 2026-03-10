# Capabilities

## RC5 scope (`0.1.0rc5`)

In scope:
- Push-to-talk speech capture with Enter start and auto-stop on long pause (manual Enter stop remains available, tuned default: `1.4s` pause and RMS threshold `80`)
- Local transcription via `faster-whisper`
- Language selection: `de`, `en`, `auto`
- tmux pane selection at startup by default, with optional env/config reuse mode
- Reuse mode validation: invalid `SILICATO_TMUX_TARGET` exits with error; invalid remembered target falls back to picker
- Normal mode direct send after transcription (without local transcript echo)
- Preview mode (`--preview`) with `send/edit/retry/skip/quit`
- Local JSONL turn logs
- Runtime diagnostics (`silicato --doctor`)
- Runtime profile plugins via `--profile` (built-in `spawn` + optional external plugins)
- Hardware-aware spawn plugin (`silicato --spawn`) for multi-instance stability

## Runtime plugin behavior

`silicato --spawn` (alias: `--profile spawn`) auto-tunes model/device/compute type to make
3-4 parallel local sessions realistic on the detected hardware.

External plugins can be installed via Python entry points group:
- `silicato.runtime_profiles`

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

## Out of scope for RC5

- Always-on mode with silence segmentation
- Spoken assistant replies (TTS)
- Non-Linux platform support
- Cloud-only runtime dependencies

## Support policy

- Official support: TUXEDO OS 24.04 LTS
- Best effort: Ubuntu 24.04-compatible Linux environments
