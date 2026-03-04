# Alpha Preview

The alpha preview helper is for exploratory and manual UX testing. It does not change RC scope.

## Scope reminder

Release scope remains:
- push-to-talk flow
- optional `--preview` confirmation flow
- tmux + Codex CLI transport

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
- runs `dialogos --doctor`
- prints active config/log paths
- starts Dialogos with higher-quality defaults (`small`, `cuda`, `float16`, `auto`)

If CUDA runtime is unavailable, Dialogos falls back to CPU `int8`.

Default helper flow runs direct-send mode. Add `--preview` to require explicit action before send.

## Override defaults

CLI override example:

```bash
./scripts/alpha_preview.sh --model medium --language en --preview
```

Environment overrides:

```bash
export DIALOGOS_ALPHA_MODEL=medium
export DIALOGOS_ALPHA_DEVICE=cuda
export DIALOGOS_ALPHA_COMPUTE_TYPE=float16
export DIALOGOS_ALPHA_LANGUAGE=auto
make alpha-preview
```

## Optional authenticated model downloads

```bash
export HF_TOKEN=hf_xxx
# optional alpha-scoped passthrough
export DIALOGOS_ALPHA_HF_TOKEN=hf_xxx
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
- `$XDG_CONFIG_HOME/dialogos/config.toml` (fallback `~/.config/dialogos/config.toml`)
- `$XDG_STATE_HOME/dialogos/turns.jsonl` (fallback `~/.local/state/dialogos/turns.jsonl`)

## Known issue note: submit timing in Codex tmux pane

Dialogos mitigates missed submits by splitting text send and Enter into separate tmux operations with a short delay.

If the symptom persists (text appears but prompt does not submit), include these details in bug reports:
- OS version
- terminal emulator
- tmux version
- Codex CLI version
- exact reproduction steps
