from __future__ import annotations

import array
from pathlib import Path

from silicato.application.use_cases.run_capture_transcribe import (
    RunCaptureTranscribeUseCase,
    TurnConfig,
)
from silicato.domain.auto_stop import AutoStopConfig, evaluate_pcm16le_auto_stop
from silicato.ports.audio import AudioAutoStopSettings, AudioChunkObservation, AudioChunkObserver
from silicato.ports.stt import TranscriptResult


def _pcm_chunk(amplitude: int, sample_count: int) -> bytes:
    samples = array.array("h", [amplitude] * sample_count)
    return samples.tobytes()


class _ObserverCapture:
    def __init__(self, chunks: list[bytes], settings: AudioAutoStopSettings) -> None:
        self._chunks = chunks
        self._settings = settings
        self.stop_reason: str | None = None
        self.callback_used = False

    def record_once(
        self,
        output_path: Path,
        sample_rate: int,
        input_device: str | None,
        on_chunk: AudioChunkObserver | None = None,
    ) -> None:
        _ = input_device
        output_path.write_bytes(b"RIFF....WAVE")
        elapsed = 0.0
        for chunk in self._chunks:
            elapsed += (len(chunk) // 2) / sample_rate
            if on_chunk is None:
                continue
            self.callback_used = True
            decision = on_chunk(
                AudioChunkObservation(
                    pcm_bytes=chunk,
                    end_time_seconds=elapsed,
                    auto_stop_settings=self._settings,
                )
            )
            if decision is not None and decision.stop:
                self.stop_reason = decision.reason
                break


class _FakeStt:
    def transcribe(self, wav_path: Path, language: str) -> TranscriptResult:
        _ = wav_path
        return TranscriptResult(text="captured", language=language)


def test_run_capture_transcribe_uses_shared_detector_callback_for_live_chunks(
    tmp_path: Path,
) -> None:
    chunks = [
        _pcm_chunk(1200, 200),
        _pcm_chunk(1200, 200),
        _pcm_chunk(0, 200),
        _pcm_chunk(0, 200),
        _pcm_chunk(0, 200),
    ]
    settings = AudioAutoStopSettings(
        silence_stop_seconds=0.6,
        speech_rms_threshold=500,
        frame_bytes=len(chunks[0]),
        max_recording_seconds=30.0,
    )
    capture = _ObserverCapture(chunks, settings)
    use_case = RunCaptureTranscribeUseCase(capture=capture, stt=_FakeStt())

    result = use_case.execute(tmp_path / "turn.wav", TurnConfig(sample_rate=1000, language="en"))
    offline = evaluate_pcm16le_auto_stop(
        b"".join(chunks),
        sample_rate_hz=1000,
        config=AutoStopConfig(
            silence_stop_seconds=settings.silence_stop_seconds,
            speech_rms_threshold=settings.speech_rms_threshold,
            frame_bytes=settings.frame_bytes,
            max_recording_seconds=settings.max_recording_seconds,
        ),
    )

    assert result.text == "captured"
    assert capture.callback_used is True
    assert capture.stop_reason == offline.reason == "silence"


def test_run_capture_transcribe_uses_shared_max_duration_fallback_for_live_chunks(
    tmp_path: Path,
) -> None:
    chunks = [
        _pcm_chunk(1200, 200),
        _pcm_chunk(1200, 200),
        _pcm_chunk(1200, 200),
        _pcm_chunk(1200, 200),
    ]
    settings = AudioAutoStopSettings(
        silence_stop_seconds=1.4,
        speech_rms_threshold=500,
        frame_bytes=len(chunks[0]),
        max_recording_seconds=0.5,
    )
    capture = _ObserverCapture(chunks, settings)
    use_case = RunCaptureTranscribeUseCase(capture=capture, stt=_FakeStt())

    result = use_case.execute(tmp_path / "turn.wav", TurnConfig(sample_rate=1000, language="en"))
    offline = evaluate_pcm16le_auto_stop(
        b"".join(chunks),
        sample_rate_hz=1000,
        config=AutoStopConfig(
            silence_stop_seconds=settings.silence_stop_seconds,
            speech_rms_threshold=settings.speech_rms_threshold,
            frame_bytes=settings.frame_bytes,
            max_recording_seconds=settings.max_recording_seconds,
        ),
    )

    assert result.text == "captured"
    assert capture.callback_used is True
    assert capture.stop_reason == offline.reason == "max_duration"
