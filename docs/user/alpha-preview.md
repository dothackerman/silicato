# Alpha Preview

The alpha preview helper is for exploratory and manual UX testing. It does not change RC scope.

## Scope reminder

Release scope remains:
- push-to-talk flow
- optional `--preview` confirmation flow
- tmux + terminal agent CLI transport

## Supported platform statement

- Official support: TUXEDO OS 24.04 LTS
- Best effort: Ubuntu 24.04-compatible Linux environments

## Start from source checkout

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

This helper:
- verifies `tmux` and `arecord`
- runs `silicato --doctor`
- prints active config/log paths
- starts Silicato with higher-quality defaults (`small`, `cuda`, `float16`, `auto`)

If CUDA runtime is unavailable, Silicato falls back to CPU `int8`.

Default helper flow runs direct-send mode. Add `--preview` to require explicit action before send.

## Override defaults

CLI override example:

```bash
./scripts/alpha_preview.sh --model medium --language en --preview
```

Environment overrides:

```bash
export SILICATO_ALPHA_MODEL=medium
export SILICATO_ALPHA_DEVICE=cuda
export SILICATO_ALPHA_COMPUTE_TYPE=float16
export SILICATO_ALPHA_LANGUAGE=auto
make alpha-preview
```

## Optional authenticated model downloads

```bash
export HF_TOKEN=hf_xxx
# optional alpha-scoped passthrough
export SILICATO_ALPHA_HF_TOKEN=hf_xxx
```

## Dry run without interactive loop

```bash
make alpha-preview-no-run
```

## Reset local alpha state

```bash
make alpha-reset
```

This removes local state files if present:
- `$XDG_CONFIG_HOME/silicato/config.toml` (fallback `~/.config/silicato/config.toml`)
- `$XDG_STATE_HOME/silicato/turns.jsonl` (fallback `~/.local/state/silicato/turns.jsonl`)

## Known issue note: submit timing in tmux agent pane

Silicato mitigates missed submits by splitting text send and submit key into separate tmux operations with a conservative 250ms delay.
If the target pane is still loading environment state, Silicato waits briefly before sending.
Silicato also fails fast if the target pane is already busy (for example showing `Thinking ... ctrl+q enqueue`) so users can retry after the current turn completes.

If the symptom persists (text appears but prompt does not submit), include these details in bug reports:
- OS version
- terminal emulator
- tmux version
- agent CLI + version (for example Codex CLI or Claude Code)
- exact reproduction steps
