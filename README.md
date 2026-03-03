# Local Whisper Voice Input (Linux)

This is a local-only voice-to-text loop:
- Record from your microphone
- Transcribe with local Whisper (`faster-whisper`)
- Print text (and optionally copy to clipboard)

No paid API is required for transcription.

## 1. System dependencies

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y alsa-utils ffmpeg python3-venv
```

Optional clipboard support:

```bash
sudo apt install -y wl-clipboard xclip
```

## 2. Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
```

For development checks (linter + formatter):

```bash
python3 -m pip install -r requirements-dev.txt
```

## 3. Run

```bash
python3 talk_to_codex.py --copy --append-file output/transcripts.txt
```

Controls:
- Press `Enter` to start recording
- Press `Enter` again to stop
- Transcript is printed and copied to clipboard (`--copy`)
- Paste into chat with `Ctrl+Shift+V`

## Useful flags

```bash
# One-shot capture
python3 talk_to_codex.py --once

# Show environment diagnostics
python3 talk_to_codex.py --doctor

# Smaller/faster model (multilingual)
python3 talk_to_codex.py --model tiny

# Better quality (slower)
python3 talk_to_codex.py --model small

# Force German
python3 talk_to_codex.py --language de

# Force English
python3 talk_to_codex.py --language en

# Try GPU explicitly (falls back to CPU if CUDA runtime is missing)
python3 talk_to_codex.py --device cuda --compute-type float16

# Use a specific ALSA capture device if default mic fails
python3 talk_to_codex.py --input-device hw:0,0
```

## Notes

- First run downloads the Whisper model weights.
- Default mode is bilingual-friendly (`--model base`, `--language auto`).
- Default settings are CPU-safe: `--device cpu --compute-type int8`.
- If you have CUDA support, try: `--device cuda`.

## Troubleshooting mic input

Show diagnostics and available ALSA capture devices:

```bash
python3 talk_to_codex.py --doctor
```

If recording fails on default device, pick one from `arecord -l` output:

```bash
python3 talk_to_codex.py --input-device hw:0,0
```

## Quality loop (maintainability)

Before sharing changes, run:

```bash
source .venv/bin/activate
make check
```

This runs:
- `ruff format .`
- `ruff check .`
