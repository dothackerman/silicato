"""Audio capture port."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class AudioAutoStopSettings:
    """Adapter-provided auto-stop settings for chunk observers."""

    silence_stop_seconds: float
    speech_rms_threshold: int
    frame_bytes: int
    max_recording_seconds: float


@dataclass(frozen=True)
class AudioChunkObservation:
    """One chunk observation emitted during live capture."""

    pcm_bytes: bytes
    end_time_seconds: float
    auto_stop_settings: AudioAutoStopSettings


@dataclass(frozen=True)
class AudioChunkDecision:
    """Observer response describing whether capture should stop."""

    stop: bool
    reason: str | None = None


AudioChunkObserver = Callable[[AudioChunkObservation], AudioChunkDecision | None]


class AudioCapturePort(Protocol):
    """Capability for recording one audio turn."""

    def record_once(
        self,
        output_path: Path,
        sample_rate: int,
        input_device: str | None,
        on_chunk: AudioChunkObserver | None = None,
    ) -> None: ...
