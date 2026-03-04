# Quickstart

## 1) Install system packages (Ubuntu / TUXEDO OS)

```bash
sudo apt update
sudo apt install -y alsa-utils ffmpeg python3-venv tmux
```

## 2) Create virtual environment and install

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
make install-dev
make hooks
```

## Optional) Enable authenticated model downloads

If you see Hugging Face anonymous-download warnings, set a token:

```bash
export HF_TOKEN=hf_xxx
```

## 3) Fastest way to try Dialogos (alpha preview)

```bash
make alpha-preview
```

If you only want checks and environment info (no interactive run):

```bash
make alpha-preview-no-run
```

To reset local alpha state and replay first-run behavior:

```bash
make alpha-reset
```

## 4) Manual run path

Start a tmux session with Codex:

```bash
tmux new -s codex
# start Codex in that tmux session
```

Run Dialogos manually:

```bash
dialogos --model small --language auto
# or
python3 -m dialogos --model small --language auto
```

First run behavior:
- Dialogos opens an indexed tmux pane picker
- You choose by number
- Selected target is remembered in config by default

Controls (normal mode):
- Press `Enter` to start recording
- Press `Enter` to stop recording
- Transcript is sent to Codex directly (no confirm prompt)
- Dialogos submits automatically (text send + short delayed Enter in tmux)
- If an older Dialogos version injects text but does not submit, press Enter once manually

Preview mode:

```bash
dialogos --preview
```

Preview mode enables confirmation controls before send:
- `y=send`, `e=edit`, `r=retry`, `s=skip`, `q=quit`

## 5) Target overrides

```bash
# one-off explicit target
dialogos --tmux-target codex:0.1

# force picker even if a target is remembered
dialogos --pick-target

# env fallback target
export DIALOGOS_TMUX_TARGET=codex:0.1
dialogos
```

## 6) Diagnostics

```bash
dialogos --doctor
```

## 7) Quality gate before changes

```bash
source .venv/bin/activate
make gate
```
