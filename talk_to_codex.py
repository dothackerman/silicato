#!/usr/bin/env python3
"""Local push-to-talk transcription loop for Linux."""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    examples = """Examples:
  python3 talk_to_codex.py --copy
  python3 talk_to_codex.py --model small --language auto
  python3 talk_to_codex.py --model base --language de --once
  python3 talk_to_codex.py --doctor
  python3 talk_to_codex.py --device cuda --compute-type float16
  python3 talk_to_codex.py --input-device hw:0,0
"""
    parser = argparse.ArgumentParser(
        description="Record mic audio (push-to-talk) and transcribe locally with faster-whisper.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples,
    )
    parser.add_argument(
        "--model",
        default="base",
        help=(
            "Whisper model size/name (default: base). Example: tiny, base, small, medium, large-v3."
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
        help="Language hint (default: auto). Examples: en, de, auto.",
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
        "--once",
        action="store_true",
        help="Record/transcribe once, then exit.",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy transcript to clipboard automatically when possible.",
    )
    parser.add_argument(
        "--append-file",
        type=Path,
        default=None,
        help="Append every transcript line to this file.",
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Print local environment checks (arecord, clipboard tools, Python deps) and exit.",
    )
    return parser.parse_args()


def require_binary(binary: str) -> None:
    if shutil.which(binary):
        return
    print(f"Missing required binary: {binary}", file=sys.stderr)
    print("Install it first (Ubuntu/Debian): sudo apt install alsa-utils", file=sys.stderr)
    sys.exit(1)


def pick_clipboard_cmd() -> list[str] | None:
    # Wayland first, then X11.
    if os.environ.get("WAYLAND_DISPLAY") and shutil.which("wl-copy"):
        return ["wl-copy"]
    if os.environ.get("DISPLAY") and shutil.which("xclip"):
        return ["xclip", "-selection", "clipboard"]
    if shutil.which("wl-copy"):
        return ["wl-copy"]
    if shutil.which("xclip"):
        return ["xclip", "-selection", "clipboard"]
    return None


def copy_to_clipboard(text: str) -> bool:
    cmd = pick_clipboard_cmd()
    if not cmd:
        return False
    try:
        subprocess.run(cmd, input=text.encode("utf-8"), check=True)
        return True
    except subprocess.SubprocessError:
        return False


def record_once(output_path: Path, sample_rate: int, input_device: str | None) -> None:
    cmd = [
        "arecord",
        "-q",
        "-f",
        "S16_LE",
        "-r",
        str(sample_rate),
        "-c",
        "1",
        str(output_path),
    ]
    if input_device:
        cmd[1:1] = ["-D", input_device]

    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    try:
        print("Recording started. Speak now, then press Enter to stop.")
        input()
    except KeyboardInterrupt:
        pass
    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
        try:
            _stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            _stdout, stderr = proc.communicate()

    stderr_text = stderr or ""
    stderr_lower = stderr_text.lower()
    benign_interrupt = "interrupted system call" in stderr_lower

    if proc.returncode not in (0, 130, 1):
        details = stderr_text.strip().splitlines()
        short = details[0] if details else "unknown recording error"
        raise RuntimeError(f"arecord failed (exit code {proc.returncode}): {short}")

    if proc.returncode == 1 and not benign_interrupt:
        details = stderr_text.strip().splitlines()
        short = details[0] if details else "unknown recording error"
        raise RuntimeError(f"arecord failed (exit code 1): {short}")

    if stderr_text:
        filtered = [
            line
            for line in stderr_text.splitlines()
            if "Interrupted system call" not in line and line.strip()
        ]
        if filtered:
            print("Recorder message:", " | ".join(filtered))

    # A WAV with only header bytes usually means no usable audio was captured.
    try:
        if output_path.stat().st_size < 512:
            raise RuntimeError("No audio captured. Check microphone input and ALSA device.")
    except OSError as exc:
        raise RuntimeError(f"Could not read temporary recording: {exc}") from exc


def is_cuda_runtime_missing(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(
        token in msg
        for token in (
            "libcublas",
            "libcudnn",
            "cuda",
            "cannot be loaded",
            "not found",
        )
    )


def build_model(model_name: str, device: str, compute_type: str):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        print("Python package 'faster-whisper' is not installed.", file=sys.stderr)
        print("Run: python3 -m pip install -r requirements.txt", file=sys.stderr)
        raise SystemExit(1) from exc

    print(
        f"Loading model '{model_name}' (device={device}, compute_type={compute_type}). "
        "First run can take a while due to model download."
    )
    start = time.time()
    try:
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
        elapsed = time.time() - start
        print(f"Model ready in {elapsed:.1f}s.")
        return model, device, compute_type
    except RuntimeError as exc:
        if device in {"auto", "cuda"} and is_cuda_runtime_missing(exc):
            print("CUDA runtime not available. Falling back to CPU (compute_type=int8).")
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
            elapsed = time.time() - start
            print(f"Model ready on CPU in {elapsed:.1f}s.")
            return model, "cpu", "int8"
        raise


def transcribe(model, wav_path: Path, language: str) -> str:
    kwargs = {
        "beam_size": 5,
        "vad_filter": True,
        "condition_on_previous_text": False,
    }
    if language.lower() != "auto":
        kwargs["language"] = language

    segments, _info = model.transcribe(str(wav_path), **kwargs)
    return "".join(segment.text for segment in segments).strip()


def run_doctor() -> int:
    print("Environment checks:")
    print(f"- arecord: {'OK' if shutil.which('arecord') else 'MISSING'}")
    print(f"- ffmpeg: {'OK' if shutil.which('ffmpeg') else 'MISSING'}")
    print(f"- wl-copy: {'OK' if shutil.which('wl-copy') else 'MISSING'}")
    print(f"- xclip: {'OK' if shutil.which('xclip') else 'MISSING'}")
    try:
        from faster_whisper import WhisperModel as _WhisperModel  # noqa: F401

        print("- faster-whisper: OK")
    except ImportError:
        print(
            "- faster-whisper: MISSING (install with: python3 -m pip install -r requirements.txt)"
        )
    if shutil.which("arecord"):
        print("- ALSA capture devices (arecord -l):")
        result = subprocess.run(["arecord", "-l"], capture_output=True, text=True, check=False)
        text = (result.stdout or result.stderr or "").strip()
        if text:
            for line in text.splitlines()[:20]:
                print(f"  {line}")
        else:
            print("  (no output)")
    return 0


def main() -> int:
    args = parse_args()
    if args.doctor:
        return run_doctor()

    require_binary("arecord")

    model, active_device, _active_compute_type = build_model(
        args.model, args.device, args.compute_type
    )

    while True:
        try:
            choice = input("Press Enter to talk, or type 'q' then Enter to quit: ").strip().lower()
        except EOFError:
            print()
            return 0
        if choice in {"q", "quit", "exit"}:
            return 0

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = Path(tmp.name)

        text = ""
        try:
            record_once(wav_path, args.sample_rate, args.input_device)
            print("Transcribing...")
            try:
                text = transcribe(model, wav_path, args.language)
            except RuntimeError as exc:
                if active_device in {"auto", "cuda"} and is_cuda_runtime_missing(exc):
                    print("CUDA inference failed during transcription. Retrying on CPU.")
                    model, active_device, _active_compute_type = build_model(
                        args.model, "cpu", "int8"
                    )
                    text = transcribe(model, wav_path, args.language)
                else:
                    raise
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            if args.once:
                return 1
            continue
        finally:
            wav_path.unlink(missing_ok=True)

        if not text:
            print("Transcript: [no speech detected]")
            if args.once:
                return 0
            continue

        print(f"Transcript: {text}")

        if args.append_file:
            args.append_file.parent.mkdir(parents=True, exist_ok=True)
            with args.append_file.open("a", encoding="utf-8") as handle:
                handle.write(text + "\n")

        if args.copy:
            if copy_to_clipboard(text):
                print("Copied transcript to clipboard.")
            else:
                print("Clipboard tool not found. Install wl-clipboard or xclip.")

        if args.once:
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
