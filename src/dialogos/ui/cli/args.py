"""CLI argument parsing."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    examples = """Examples:
  dialogos --model small --language auto
  dialogos --pick-target
  dialogos --tmux-target codex:0.1 --preview
  dialogos --doctor
"""
    parser = argparse.ArgumentParser(
        prog="dialogos",
        description=(
            "Record mic audio, transcribe locally, and send text to tmux "
            "(direct in normal mode, confirmed in preview)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples,
    )
    parser.add_argument(
        "--model",
        default="base",
        help=(
            "Whisper model size/name (default: base). Examples: tiny, base, small, medium, large-v3"
        ),
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Inference device: auto, cpu, or cuda (default: cpu).",
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="Compute type passed to faster-whisper (default: int8).",
    )
    parser.add_argument(
        "--language",
        default="auto",
        choices=["de", "en", "auto"],
        help="Language hint (default: auto).",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Recording sample rate in Hz (default: 16000).",
    )
    parser.add_argument(
        "--input-device",
        default=None,
        help="Optional ALSA capture device passed to arecord -D (example: hw:0,0).",
    )
    parser.add_argument(
        "--tmux-target",
        default=None,
        help="Explicit tmux target pane (highest priority).",
    )
    parser.add_argument(
        "--pick-target",
        action="store_true",
        help="Always open interactive tmux pane picker at startup.",
    )
    parser.add_argument(
        "--no-remember-target",
        action="store_true",
        help="Do not save chosen target into the config file.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help=("Preview mode: show confirm/edit/retry/skip flow and require explicit send (y)."),
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Override JSONL log path (default uses XDG_STATE_HOME fallback).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run exactly one completed turn and exit.",
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Print local environment checks and exit.",
    )
    return parser.parse_args()
