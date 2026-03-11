"""Pure auto-stop endpoint detection logic."""

from __future__ import annotations

import array
import math
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

AutoStopReason = Literal["disabled", "silence", "max_duration", "exhausted", "no_speech"]
_FLOAT_EPSILON = 1e-9


@dataclass(frozen=True)
class AutoStopConfig:
    """Parameters controlling silence-end detection."""

    silence_stop_seconds: float = 1.4
    speech_rms_threshold: int = 80
    frame_bytes: int = 4096
    max_recording_seconds: float = 30.0


@dataclass(frozen=True)
class RmsFrame:
    """RMS value for one sequential PCM frame."""

    rms: int
    end_time_seconds: float


@dataclass(frozen=True)
class AutoStopDecision:
    """Outcome of evaluating one clip against auto-stop settings."""

    stop_time_seconds: float | None
    clip_duration_seconds: float
    speech_detected: bool
    reason: AutoStopReason


class IncrementalAutoStopDetector:
    """Incremental endpoint detector shared by live capture and offline replay."""

    def __init__(self, config: AutoStopConfig) -> None:
        self._config = config
        self._clip_duration_seconds = 0.0
        self._speech_detected = False
        self._last_voice_at: float | None = None

    def observe(self, frame: RmsFrame) -> AutoStopDecision | None:
        """Consume one frame and return a stop decision when it becomes true."""

        self._clip_duration_seconds = frame.end_time_seconds
        if frame.rms >= self._config.speech_rms_threshold:
            self._speech_detected = True
            self._last_voice_at = frame.end_time_seconds
        elif (
            self._config.silence_stop_seconds > 0
            and self._speech_detected
            and self._last_voice_at is not None
        ):
            silent_for = frame.end_time_seconds - self._last_voice_at
            if silent_for + _FLOAT_EPSILON >= self._config.silence_stop_seconds:
                return AutoStopDecision(
                    stop_time_seconds=self._last_voice_at + self._config.silence_stop_seconds,
                    clip_duration_seconds=self._clip_duration_seconds,
                    speech_detected=True,
                    reason="silence",
                )

        if (
            self._config.max_recording_seconds > 0
            and frame.end_time_seconds + _FLOAT_EPSILON >= self._config.max_recording_seconds
        ):
            return AutoStopDecision(
                stop_time_seconds=self._config.max_recording_seconds,
                clip_duration_seconds=self._clip_duration_seconds,
                speech_detected=self._speech_detected,
                reason="max_duration",
            )

        return None

    def finish(self) -> AutoStopDecision:
        """Return the terminal decision when no stop condition fired."""

        if self._config.silence_stop_seconds <= 0:
            return AutoStopDecision(
                stop_time_seconds=None,
                clip_duration_seconds=self._clip_duration_seconds,
                speech_detected=self._speech_detected,
                reason="disabled",
            )

        reason: AutoStopReason = "no_speech" if not self._speech_detected else "exhausted"
        return AutoStopDecision(
            stop_time_seconds=None,
            clip_duration_seconds=self._clip_duration_seconds,
            speech_detected=self._speech_detected,
            reason=reason,
        )


def evaluate_pcm16le_auto_stop(
    pcm_bytes: bytes,
    *,
    sample_rate_hz: int,
    config: AutoStopConfig,
) -> AutoStopDecision:
    """Evaluate when auto-stop would trigger for raw mono s16le PCM bytes."""

    frames = tuple(iter_rms_frames_s16le(pcm_bytes, sample_rate_hz=sample_rate_hz, config=config))
    return evaluate_rms_frames(frames, config=config)


def iter_rms_frames_s16le(
    pcm_bytes: bytes,
    *,
    sample_rate_hz: int,
    config: AutoStopConfig,
) -> Iterable[RmsFrame]:
    """Yield RMS frames with cumulative end timestamps."""

    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")
    frame_bytes = max(2, int(config.frame_bytes))
    elapsed = 0.0

    for start in range(0, len(pcm_bytes), frame_bytes):
        chunk = pcm_bytes[start : start + frame_bytes]
        frame = rms_frame_from_pcm_s16le(
            chunk,
            sample_rate_hz=sample_rate_hz,
            start_time_seconds=elapsed,
        )
        if frame is None:
            continue
        elapsed = frame.end_time_seconds
        yield frame


def rms_frame_from_pcm_s16le(
    pcm_chunk: bytes,
    *,
    sample_rate_hz: int,
    start_time_seconds: float = 0.0,
) -> RmsFrame | None:
    """Convert one PCM chunk into a timestamped RMS frame."""

    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")
    sample_count = len(pcm_chunk) // 2
    if sample_count <= 0:
        return None
    end_time_seconds = start_time_seconds + (sample_count / sample_rate_hz)
    return RmsFrame(rms=_rms_s16le(pcm_chunk), end_time_seconds=end_time_seconds)


def evaluate_rms_frames(
    frames: Iterable[RmsFrame],
    *,
    config: AutoStopConfig,
) -> AutoStopDecision:
    """Return when auto-stop would fire for the provided RMS frames."""

    detector = IncrementalAutoStopDetector(config)
    for frame in frames:
        decision = detector.observe(frame)
        if decision is not None:
            return decision
    return detector.finish()


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
