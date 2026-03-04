# Alpha Preview

This mode is for exploratory testing and fast feedback, not formal release validation.

## Start from a fresh clone

```bash
sudo apt update
sudo apt install -y alsa-utils ffmpeg python3-venv tmux

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
make install-dev
```

## Run alpha preview

```bash
make alpha-preview
```

What this does:
- verifies `tmux` and `arecord`
- runs `dialogos --doctor`
- prints active config/log paths
- launches Dialogos with GPU-oriented alpha defaults:
  - `--model small`
  - `--device cuda`
  - `--compute-type float16`
  - `--language auto`

If CUDA runtime is not available, Dialogos falls back to CPU `int8` automatically.

Default alpha flow is direct send after transcription (no confirm prompt).
Use `--preview` when you want to review/edit/retry/skip before sending.

## Override defaults

You can override by passing CLI args:

```bash
./scripts/alpha_preview.sh --model medium --language en --preview
```

Or set environment overrides:

```bash
export DIALOGOS_ALPHA_MODEL=medium
export DIALOGOS_ALPHA_DEVICE=cuda
export DIALOGOS_ALPHA_COMPUTE_TYPE=float16
export DIALOGOS_ALPHA_LANGUAGE=auto
make alpha-preview
```

To avoid Hugging Face anonymous-download warnings and improve model download reliability, set a token:

```bash
export HF_TOKEN=hf_xxx
# optional alpha-scoped passthrough if you do not want to export HF_TOKEN globally:
export DIALOGOS_ALPHA_HF_TOKEN=hf_xxx
```

`HF_TOKEN` is only used for model downloads from Hugging Face Hub. Transcription still runs locally.

Dry run without launching the interactive loop:

```bash
make alpha-preview-no-run
```

## Reset local alpha state

Use this when you want to replay first-run behavior (picker + remembered target setup).

```bash
make alpha-reset
```

This removes local files if present:
- `$XDG_CONFIG_HOME/dialogos/config.toml` (fallback `~/.config/dialogos/config.toml`)
- `$XDG_STATE_HOME/dialogos/turns.jsonl` (fallback `~/.local/state/dialogos/turns.jsonl`)

## Known limitations in alpha preview
- Turn logs are plain local JSONL and may include transcript text.
- No always-on voice mode.
- No spoken assistant replies (TTS).
- Linux + tmux workflow only.

## Known issue note: Codex submit timing

Some environments using older Dialogos sender behavior may inject transcript text into Codex
without submitting the prompt until Enter is pressed manually.

Dialogos now mitigates this by sending text and submit key as two tmux operations with a short delay.
If you still observe the issue, capture your Codex CLI version, tmux version, and terminal emulator
and open a bug report with reproduction steps.

## Give feedback

Use the lightweight template in [Feedback Template](feedback-template.md).
