"""CLI argument parsing."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from silicato.ui.cli.runtime_plugins import available_runtime_profiles


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    available_profiles = available_runtime_profiles()
    profiles_text = ", ".join(available_profiles) if available_profiles else "(none)"
    examples = """Examples:
  silicato -m small -l auto
  silicato
  silicato --reuse-target
  silicato -t codex:0.1 -p
  silicato route add gaia codex:0.1
  silicato route list
  silicato inject --to gaia --text "hello"
  silicato --doctor
  silicato --spawn
  silicato --profile my-custom-plugin
"""
    parser = argparse.ArgumentParser(
        prog="silicato",
        description=(
            "Record mic audio, transcribe locally, and send text to tmux "
            "(direct in normal mode, explicit action in preview)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples,
    )
    parser.add_argument(
        "-m",
        "--model",
        default="base",
        help=(
            "Whisper model size/name (default: base). Examples: tiny, base, small, medium, large-v3"
        ),
    )
    parser.add_argument(
        "-d",
        "--device",
        default="cpu",
        help="Inference device: auto, cpu, or cuda (default: cpu).",
    )
    parser.add_argument(
        "-c",
        "--compute-type",
        default="int8",
        help="Compute type passed to faster-whisper (default: int8).",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="auto",
        choices=["de", "en", "auto"],
        help="Language hint (default: auto).",
    )
    parser.add_argument(
        "-r",
        "--sample-rate",
        type=int,
        default=16000,
        help="Recording sample rate in Hz (default: 16000).",
    )
    parser.add_argument(
        "--silence-stop-seconds",
        type=float,
        default=1.4,
        help=(
            "Auto-stop recording after this many silent seconds (default: 1.4). "
            "Set to 0 to disable auto-stop and require Enter to stop."
        ),
    )
    parser.add_argument(
        "--silence-rms-threshold",
        type=int,
        default=80,
        help=(
            "RMS threshold used to classify frames as speech for auto-stop "
            "(default: 80). Lower values are more tolerant of quiet speech."
        ),
    )
    parser.add_argument(
        "-i",
        "--input-device",
        default=None,
        help="Optional ALSA capture device passed to arecord -D (example: hw:0,0).",
    )
    parser.add_argument(
        "-t",
        "--tmux-target",
        default=None,
        help="Explicit tmux target pane (highest priority).",
    )
    picker_mode = parser.add_mutually_exclusive_group()
    picker_mode.add_argument(
        "--pick-target",
        action="store_true",
        default=True,
        help="Force interactive tmux pane picker at startup (default behavior).",
    )
    picker_mode.add_argument(
        "-R",
        "--reuse-target",
        dest="pick_target",
        action="store_false",
        help=(
            "Reuse env/config target before picker "
            "(SILICATO_TMUX_TARGET -> remembered config -> picker)."
        ),
    )
    parser.add_argument(
        "-n",
        "--no-remember-target",
        action="store_true",
        help="Do not save chosen target into the config file.",
    )
    parser.add_argument(
        "-p",
        "--preview",
        action="store_true",
        help=("Preview mode: require explicit action (y=send, e=edit, r=retry, s=skip, q=quit)."),
    )
    parser.add_argument(
        "-f",
        "--log-file",
        type=Path,
        default=None,
        help="Override JSONL log path (default uses XDG_STATE_HOME fallback).",
    )
    parser.add_argument(
        "-o",
        "--once",
        action="store_true",
        help="Run exactly one completed turn and exit.",
    )
    parser.add_argument(
        "--profile",
        metavar="PLUGIN",
        default=None,
        help=(
            f"Apply a runtime plugin profile by name. Available now: {profiles_text}. "
            "External plugins can be provided via Python entry points group "
            "'silicato.runtime_profiles'."
        ),
    )
    parser.add_argument(
        "--spawn",
        action="store_true",
        help="Alias for --profile spawn.",
    )
    parser.add_argument(
        "-D",
        "--doctor",
        action="store_true",
        help="Print local environment checks and exit.",
    )
    subparsers = parser.add_subparsers(dest="command")

    route_parser = subparsers.add_parser(
        "route",
        help="Manage named tmux pane routes.",
    )
    route_subparsers = route_parser.add_subparsers(dest="route_command", required=True)

    route_add = route_subparsers.add_parser(
        "add",
        help="Create a named route.",
    )
    route_add.add_argument("identifier", help="Stable route identifier (for example gaia).")
    route_add.add_argument("tmux_target", help="Pane-scoped tmux target.")
    route_add.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing route binding.",
    )

    route_update = route_subparsers.add_parser(
        "update",
        help="Update an existing named route.",
    )
    route_update.add_argument("identifier", help="Existing route identifier.")
    route_update.add_argument("tmux_target", help="New pane-scoped tmux target.")

    route_remove = route_subparsers.add_parser(
        "remove",
        help="Delete a named route.",
    )
    route_remove.add_argument("identifier", help="Existing route identifier.")

    route_resolve = route_subparsers.add_parser(
        "resolve",
        help="Print the tmux target for a named route.",
    )
    route_resolve.add_argument("identifier", help="Existing route identifier.")

    route_check = route_subparsers.add_parser(
        "check",
        help="Validate a named route against the current tmux runtime.",
    )
    route_check.add_argument("identifier", help="Existing route identifier.")

    route_subparsers.add_parser(
        "list",
        help="List all named routes.",
    )

    inject_parser = subparsers.add_parser(
        "inject",
        help="Send text to a named route without entering the voice capture flow.",
    )
    inject_parser.add_argument(
        "--to",
        dest="route_identifier",
        required=True,
        help="Named route identifier.",
    )
    inject_source = inject_parser.add_mutually_exclusive_group(required=True)
    inject_source.add_argument(
        "--text",
        dest="inject_text",
        help="Literal text to send.",
    )
    inject_source.add_argument(
        "--from-file",
        dest="inject_from_file",
        type=Path,
        help="Read text to send from a file.",
    )
    args = parser.parse_args(argv)
    if args.spawn:
        args.profile = "spawn"
    return args
