#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -x ".venv/bin/python3" ]]; then
  PYTHON=".venv/bin/python3"
else
  PYTHON="python3"
fi

ASSUME_YES=0
if [[ "${1:-}" == "--yes" ]]; then
  ASSUME_YES=1
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

if [[ "$ASSUME_YES" -eq 0 ]]; then
  echo "This will delete alpha-local state files if they exist:"
  echo "- $CONFIG_PATH"
  echo "- $LOG_PATH"
  read -r -p "Continue? [y/N] " answer
  case "$answer" in
    y|Y|yes|YES) ;;
    *)
      echo "Cancelled."
      exit 0
      ;;
  esac
fi

removed=0
for path in "$CONFIG_PATH" "$LOG_PATH"; do
  if [[ -f "$path" ]]; then
    rm -f "$path"
    echo "Removed: $path"
    removed=1
  else
    echo "Not found: $path"
  fi
done

if [[ "$removed" -eq 0 ]]; then
  echo "No state files were removed."
else
  echo "Alpha state reset complete."
fi
