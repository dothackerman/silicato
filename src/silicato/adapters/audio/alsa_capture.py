"""ALSA audio capture adapter."""

from __future__ import annotations

import os
import select
import signal
import subprocess
import sys
import wave
from pathlib import Path

from silicato.ports.audio import (
    AudioAutoStopSettings,
    AudioCapturePort,
    AudioChunkDecision,
    AudioChunkObservation,
    AudioChunkObserver,
)


class AlsaCaptureAdapter(AudioCapturePort):
    """Capture adapter backed by `arecord`."""

    def __init__(
        self,
        *,
        silence_stop_seconds: float = 1.4,
        silence_rms_threshold: int = 80,
        max_recording_seconds: float = 0.0,
        poll_interval_seconds: float = 0.1,
    ) -> None:
        self._auto_stop_settings = AudioAutoStopSettings(
            silence_stop_seconds=max(0.0, float(silence_stop_seconds)),
            speech_rms_threshold=max(1, int(silence_rms_threshold)),
            frame_bytes=4096,
            max_recording_seconds=max(0.0, float(max_recording_seconds)),
        )
        self._poll_interval_seconds = max(0.02, float(poll_interval_seconds))

    def record_once(
        self,
        output_path: Path,
        sample_rate: int,
        input_device: str | None,
        on_chunk: AudioChunkObserver | None = None,
    ) -> None:
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
            self._wait_for_stop(
                proc,
                captured_pcm,
                sample_rate=sample_rate,
                on_chunk=on_chunk,
            )
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

    def _wait_for_stop(
        self,
        proc: subprocess.Popen[bytes],
        captured_pcm: bytearray,
        *,
        sample_rate: int,
        on_chunk: AudioChunkObserver | None,
    ) -> None:
        if proc.stdout is None:
            return
        if self._auto_stop_settings.silence_stop_seconds <= 0:
            print("Recording started. Speak now, then press Enter to stop.")
        else:
            print(
                "Recording started. Speak now. "
                f"Auto-stop after {self._auto_stop_settings.silence_stop_seconds:.1f}s of silence "
                "(press Enter to stop manually)."
            )

        stdin_fd = _stdin_fd_if_tty()
        stdout_fd = proc.stdout.fileno()
        elapsed_seconds = 0.0

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
                pcm_chunk = os.read(stdout_fd, self._auto_stop_settings.frame_bytes)
            if pcm_chunk:
                captured_pcm.extend(pcm_chunk)
                sample_count = len(pcm_chunk) // 2
                if sample_count <= 0:
                    continue
                elapsed_seconds += sample_count / sample_rate
                if on_chunk is not None:
                    decision = on_chunk(
                        AudioChunkObservation(
                            pcm_bytes=pcm_chunk,
                            end_time_seconds=elapsed_seconds,
                            auto_stop_settings=self._auto_stop_settings,
                        )
                    )
                    if isinstance(decision, AudioChunkDecision) and decision.stop:
                        if decision.reason == "max_duration":
                            print(
                                "Recording stopped at the max duration fallback "
                                f"({self._auto_stop_settings.max_recording_seconds:.1f}s)."
                            )
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
