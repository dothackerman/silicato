# Quickstart

## 1) Platform and baseline

Official support target:
- TUXEDO OS 24.04 LTS (Ubuntu noble base)

Best effort target:
- Ubuntu 24.04-compatible Linux environments

Validated RC baseline:
- Python 3.12.3
- tmux 3.4
- Codex CLI 0.107.0

## 2) Install required system packages

```bash
sudo apt update
sudo apt install -y alsa-utils ffmpeg python3-venv tmux
```

## 3) Install Dialogos

### Option A: RC install from TestPyPI (`0.1.0rc1`)

```bash
pipx install --index-url https://test.pypi.org/simple --pip-args='--extra-index-url https://pypi.org/simple' dialogos==0.1.0rc1
```

### Option B: install from source checkout

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
make install-dev
make hooks
```

## 4) Start Codex in tmux

```bash
tmux new -s codex
# run codex in this tmux session
```

## 5) Verify runtime dependencies

```bash
dialogos --doctor
```

## 6) Run Dialogos

Normal mode (direct send):

```bash
dialogos
```

Preview mode (explicit action before send):

```bash
dialogos --preview
```

Preview controls:
- `y=send`
- `e=edit`
- `r=retry`
- `s=skip`
- `q=quit`

## 7) Target selection and overrides

```bash
# one-off explicit target
dialogos --tmux-target codex:0.1

# force picker even if a target is remembered
dialogos --pick-target

# env fallback target
export DIALOGOS_TMUX_TARGET=codex:0.1
dialogos
```

Resolution order:
1. `--tmux-target`
2. `DIALOGOS_TMUX_TARGET`
3. remembered config target
4. interactive picker

## 8) Optional model download auth

If Hugging Face warns about anonymous download limits:

```bash
export HF_TOKEN=hf_xxx
```

This token is only used for model downloads.
