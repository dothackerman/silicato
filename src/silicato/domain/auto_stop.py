"""Pure auto-stop endpoint detection logic."""

from __future__ import annotations

import array
import math
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

AutoStopReason = Literal["disabled", "silence", "exhausted", "no_speech"]
_FLOAT_EPSILON = 1e-9


@dataclass(frozen=True)
class AutoStopConfig:
    """Parameters controlling silence-end detection."""

    silence_stop_seconds: float = 1.4
    speech_rms_threshold: int = 80
    frame_bytes: int = 4096


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
        sample_count = len(chunk) // 2
        if sample_count <= 0:
            continue
        elapsed += sample_count / sample_rate_hz
        yield RmsFrame(rms=_rms_s16le(chunk), end_time_seconds=elapsed)


def evaluate_rms_frames(
    frames: Iterable[RmsFrame],
    *,
    config: AutoStopConfig,
) -> AutoStopDecision:
    """Return when auto-stop would fire for the provided RMS frames."""

    clip_duration_seconds = 0.0
    speech_detected = False
    last_voice_at: float | None = None

    if config.silence_stop_seconds <= 0:
        for frame in frames:
            clip_duration_seconds = frame.end_time_seconds
            if frame.rms >= config.speech_rms_threshold:
                speech_detected = True
        return AutoStopDecision(
            stop_time_seconds=None,
            clip_duration_seconds=clip_duration_seconds,
            speech_detected=speech_detected,
            reason="disabled",
        )

    for frame in frames:
        clip_duration_seconds = frame.end_time_seconds
        if frame.rms >= config.speech_rms_threshold:
            speech_detected = True
            last_voice_at = frame.end_time_seconds
            continue

        if speech_detected and last_voice_at is not None:
            silent_for = frame.end_time_seconds - last_voice_at
            if silent_for + _FLOAT_EPSILON >= config.silence_stop_seconds:
                return AutoStopDecision(
                    stop_time_seconds=frame.end_time_seconds,
                    clip_duration_seconds=clip_duration_seconds,
                    speech_detected=True,
                    reason="silence",
                )

    reason: AutoStopReason = "no_speech" if not speech_detected else "exhausted"
    return AutoStopDecision(
        stop_time_seconds=None,
        clip_duration_seconds=clip_duration_seconds,
        speech_detected=speech_detected,
        reason=reason,
    )


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
