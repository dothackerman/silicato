"""Use case for capture + transcribe execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from silicato.domain.auto_stop import (
    AutoStopConfig,
    IncrementalAutoStopDetector,
    rms_frame_from_pcm_s16le,
)
from silicato.domain.turn_state import normalize_transcript
from silicato.ports.audio import AudioCapturePort, AudioChunkDecision, AudioChunkObservation
from silicato.ports.stt import SpeechToTextPort, TranscriptResult


@dataclass(frozen=True)
class TurnConfig:
    sample_rate: int = 16000
    input_device: str | None = None
    language: str = "auto"


class RunCaptureTranscribeUseCase:
    """Orchestrates one capture/transcribe pass."""

    def __init__(self, capture: AudioCapturePort, stt: SpeechToTextPort) -> None:
        self._capture = capture
        self._stt = stt

    def execute(self, wav_path: Path, config: TurnConfig) -> TranscriptResult:
        detector: IncrementalAutoStopDetector | None = None

        def _observe_chunk(chunk: AudioChunkObservation) -> AudioChunkDecision:
            nonlocal detector
            if detector is None:
                detector = IncrementalAutoStopDetector(
                    AutoStopConfig(
                        silence_stop_seconds=chunk.auto_stop_settings.silence_stop_seconds,
                        speech_rms_threshold=chunk.auto_stop_settings.speech_rms_threshold,
                        frame_bytes=chunk.auto_stop_settings.frame_bytes,
                        max_recording_seconds=chunk.auto_stop_settings.max_recording_seconds,
                    )
                )
            frame = rms_frame_from_pcm_s16le(
                chunk.pcm_bytes,
                sample_rate_hz=config.sample_rate,
                start_time_seconds=chunk.end_time_seconds
                - ((len(chunk.pcm_bytes) // 2) / config.sample_rate),
            )
            if frame is None:
                return AudioChunkDecision(stop=False)
            decision = detector.observe(frame)
            if decision is None:
                return AudioChunkDecision(stop=False)
            return AudioChunkDecision(stop=True, reason=decision.reason)

        self._capture.record_once(
            wav_path,
            config.sample_rate,
            config.input_device,
            on_chunk=_observe_chunk,
        )
        result = self._stt.transcribe(wav_path, config.language)
        return TranscriptResult(text=normalize_transcript(result.text), language=result.language)
