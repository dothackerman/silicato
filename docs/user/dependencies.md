# Dependencies

## Platform support

Official support:
- TUXEDO OS 24.04 LTS (Ubuntu noble base)

Best effort:
- Ubuntu 24.04-compatible Linux environments

Validated baseline:
- Python 3.12.3
- tmux 3.4
- Codex CLI 0.107.0

## System runtime dependencies

Install with apt:

```bash
sudo apt update
sudo apt install -y alsa-utils ffmpeg python3-venv tmux
```

Required tools:
- `arecord` (from `alsa-utils`)
- `ffmpeg`
- `tmux`

## Python package dependencies

Runtime dependencies are defined in `pyproject.toml`.

Install from source:

```bash
python3 -m pip install -e .
```

Install with dev extras:

```bash
python3 -m pip install -e .[dev]
```

## Optional GPU acceleration

Optional components:
- NVIDIA driver
- CUDA runtime libraries (for example `libcublas12`)

CPU mode remains supported.

## Optional model download authentication

Set `HF_TOKEN` for authenticated Hugging Face downloads:

```bash
export HF_TOKEN=hf_xxx
```

Transcription still runs locally.

## tmux behavior requirement

Dialogos validates tmux target availability before sending.
If no tmux session exists, Dialogos prints setup guidance and exits non-zero.
