#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -x ".venv/bin/python3" ]]; then
  PYTHON=".venv/bin/python3"
else
  PYTHON="python3"
fi

NO_RUN=0
FORWARD_ARGS=()
for arg in "$@"; do
  if [[ "$arg" == "--no-run" ]]; then
    NO_RUN=1
  else
    FORWARD_ARGS+=("$arg")
  fi
done

MISSING=()
for binary in tmux arecord; do
  if ! command -v "$binary" >/dev/null 2>&1; then
    MISSING+=("$binary")
  fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "Missing required binaries: ${MISSING[*]}" >&2
  echo "Install on Ubuntu/TUXEDO with: sudo apt install -y tmux alsa-utils ffmpeg" >&2
  exit 1
fi

if ! "$PYTHON" -c 'import dialogos' >/dev/null 2>&1; then
  echo "Dialogos package is not installed in the active environment." >&2
  echo "Run: make install-dev" >&2
  exit 1
fi

CONFIG_PATH="$($PYTHON - <<'PY'
from dialogos.config import default_config_path
print(default_config_path())
PY
)"

LOG_PATH="$($PYTHON - <<'PY'
from dialogos.logging_jsonl import default_log_path
print(default_log_path())
PY
)"

echo "== Dialogos Alpha Preview =="
echo "Project root: $ROOT_DIR"
echo "Python: $PYTHON"
echo "Config path: $CONFIG_PATH"
echo "Log path: $LOG_PATH"
echo "Target resolution order: --tmux-target -> DIALOGOS_TMUX_TARGET -> remembered config -> picker"

echo
echo "Running diagnostics (dialogos --doctor)..."
"$PYTHON" -m dialogos --doctor

echo
if tmux list-panes -a >/dev/null 2>&1; then
  echo "tmux session detected."
else
  echo "No active tmux session detected."
  echo "Start one with: tmux new -s codex"
  echo "Then start Codex in that tmux session."
fi

if [[ "$NO_RUN" -eq 1 ]]; then
  echo
  echo "Preview checks complete (--no-run)."
  exit 0
fi

echo
echo "Launching Dialogos with alpha defaults (override by passing your own args):"
echo "  $PYTHON -m dialogos --model base --device cpu --compute-type int8 --language auto ${FORWARD_ARGS[*]:-}"

exec "$PYTHON" -m dialogos \
  --model base \
  --device cpu \
  --compute-type int8 \
  --language auto \
  "${FORWARD_ARGS[@]}"
