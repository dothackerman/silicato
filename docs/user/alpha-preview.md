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
- launches Dialogos with alpha-safe defaults:
  - `--model base`
  - `--device cpu`
  - `--compute-type int8`
  - `--language auto`

You can override defaults:

```bash
./scripts/alpha_preview.sh --model small --language en --preview
```

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

## Give feedback

Use the lightweight template in [Feedback Template](feedback-template.md).
