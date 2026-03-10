"""ALSA audio capture adapter."""

from __future__ import annotations

import array
import math
import os
import select
import signal
import subprocess
import sys
import time
import wave
from pathlib import Path

from silicato.ports.audio import AudioCapturePort


class AlsaCaptureAdapter(AudioCapturePort):
    """Capture adapter backed by `arecord`."""

    def __init__(
        self,
        *,
        silence_stop_seconds: float = 1.4,
        silence_rms_threshold: int = 80,
        poll_interval_seconds: float = 0.1,
    ) -> None:
        self._silence_stop_seconds = max(0.0, float(silence_stop_seconds))
        self._silence_rms_threshold = max(1, int(silence_rms_threshold))
        self._poll_interval_seconds = max(0.02, float(poll_interval_seconds))

    def record_once(self, output_path: Path, sample_rate: int, input_device: str | None) -> None:
        cmd = [
            "arecord",
            "-q",
            "-t",
            "raw",
            "-f",
            "S16_LE",
            "-r",
            str(sample_rate),
            "-c",
            "1",
        ]
        if input_device:
            cmd[1:1] = ["-D", input_device]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.stdout is None:
            raise RuntimeError("Failed to open arecord stdout stream.")
        if proc.stderr is None:
            raise RuntimeError("Failed to open arecord stderr stream.")

        captured_pcm = bytearray()
        try:
            self._wait_for_stop(proc, captured_pcm)
        except KeyboardInterrupt:
            pass
        finally:
            if proc.poll() is None:
                proc.send_signal(signal.SIGINT)
            try:
                stdout_tail, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout_tail, stderr = proc.communicate()
            if stdout_tail:
                captured_pcm.extend(stdout_tail)

        stderr_text = (stderr or b"").decode(errors="replace")
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

        try:
            with wave.open(str(output_path), "wb") as handle:
                handle.setnchannels(1)
                handle.setsampwidth(2)
                handle.setframerate(sample_rate)
                handle.writeframes(captured_pcm)
        except OSError as exc:
            raise RuntimeError(f"Could not write temporary recording: {exc}") from exc

        try:
            if output_path.stat().st_size < 512:
                raise RuntimeError("No audio captured. Check microphone input and ALSA device.")
        except OSError as exc:
            raise RuntimeError(f"Could not read temporary recording: {exc}") from exc

    def _wait_for_stop(self, proc: subprocess.Popen[bytes], captured_pcm: bytearray) -> None:
        if proc.stdout is None:
            return
        if self._silence_stop_seconds <= 0:
            print("Recording started. Speak now, then press Enter to stop.")
        else:
            print(
                "Recording started. Speak now. "
                f"Auto-stop after {self._silence_stop_seconds:.1f}s of silence "
                "(press Enter to stop manually)."
            )

        speech_seen = False
        last_voice_at: float | None = None
        stdin_fd = _stdin_fd_if_tty()
        stdout_fd = proc.stdout.fileno()

        while proc.poll() is None:
            watched: list[int] = [stdout_fd]
            if stdin_fd is not None:
                watched.append(stdin_fd)
            readable, _, _ = select.select(watched, [], [], self._poll_interval_seconds)

            if stdin_fd is not None and stdin_fd in readable:
                _consume_stdin_line()
                return

            pcm_chunk = b""
            if stdout_fd in readable:
                pcm_chunk = os.read(stdout_fd, 4096)
            if pcm_chunk:
                captured_pcm.extend(pcm_chunk)
                rms = _rms_s16le(pcm_chunk)
                now = time.monotonic()
                if rms >= self._silence_rms_threshold:
                    speech_seen = True
                    last_voice_at = now
                elif self._silence_stop_seconds > 0 and speech_seen and last_voice_at is not None:
                    if now - last_voice_at >= self._silence_stop_seconds:
                        return
            elif speech_seen and last_voice_at is not None:
                if (
                    self._silence_stop_seconds > 0
                    and time.monotonic() - last_voice_at >= self._silence_stop_seconds
                ):
                    return

            if not readable:
                continue


def _stdin_fd_if_tty() -> int | None:
    try:
        fd = sys.stdin.fileno()
    except (AttributeError, OSError):
        return None
    if not os.isatty(fd):
        return None
    return fd


def _consume_stdin_line() -> None:
    try:
        sys.stdin.readline()
    except OSError:
        return


def _rms_s16le(pcm_chunk: bytes) -> int:
    if len(pcm_chunk) < 2:
        return 0
    if len(pcm_chunk) % 2 == 1:
        pcm_chunk = pcm_chunk[:-1]
    if not pcm_chunk:
        return 0
    samples = array.array("h")
    samples.frombytes(pcm_chunk)
    if sys.byteorder != "little":
        samples.byteswap()
    if not samples:
        return 0
    square_sum = sum(sample * sample for sample in samples)
    return int(math.sqrt(square_sum / len(samples)))
