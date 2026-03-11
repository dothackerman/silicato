from __future__ import annotations

from pathlib import Path

from silicato.application.use_cases.run_capture_transcribe import (
    RunCaptureTranscribeUseCase,
    TurnConfig,
)
from silicato.application.use_cases.send_turn import SendTurnUseCase
from silicato.domain.confirm_actions import parse_confirm_action
from silicato.ports.audio import AudioChunkObserver
from silicato.ports.stt import TranscriptResult


class FakeCapture:
    def __init__(self) -> None:
        self.called = False

    def record_once(
        self,
        output_path: Path,
        sample_rate: int,
        input_device: str | None,
        on_chunk: AudioChunkObserver | None = None,
    ) -> None:
        self.called = True
        output_path.write_bytes(b"RIFF....WAVE")
        _ = sample_rate
        _ = input_device
        _ = on_chunk


class FakeStt:
    def transcribe(self, wav_path: Path, language: str) -> TranscriptResult:
        _ = wav_path
        return TranscriptResult(text="hello world", language=language)


class FakeSender:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send(self, text: str) -> None:
        self.messages.append(text)


def test_run_turn_without_send(tmp_path: Path) -> None:
    capture = FakeCapture()
    stt = FakeStt()
    use_case = RunCaptureTranscribeUseCase(capture=capture, stt=stt)
    result = use_case.execute(
        tmp_path / "turn.wav",
        TurnConfig(language="de"),
    )
    assert capture.called
    assert result.text == "hello world"
    assert result.language == "de"


def test_run_turn_with_send(tmp_path: Path) -> None:
    capture = FakeCapture()
    stt = FakeStt()
    sender = FakeSender()

    use_case = RunCaptureTranscribeUseCase(capture=capture, stt=stt)
    transcript = use_case.execute(
        tmp_path / "turn.wav",
        TurnConfig(language="en"),
    )
    SendTurnUseCase(sender=sender).execute(transcript.text)
    assert sender.messages == ["hello world"]


def test_confirm_actions_normal_mode() -> None:
    assert parse_confirm_action("", preview_mode=False) == "send"
    assert parse_confirm_action("e", preview_mode=False) == "edit"
    assert parse_confirm_action("r", preview_mode=False) == "retry"
    assert parse_confirm_action("s", preview_mode=False) == "skip"
    assert parse_confirm_action("q", preview_mode=False) == "quit"


def test_confirm_actions_preview_mode_explicit_send() -> None:
    assert parse_confirm_action("", preview_mode=True) is None
    assert parse_confirm_action("y", preview_mode=True) == "send"
    assert parse_confirm_action("send", preview_mode=True) == "send"
    assert parse_confirm_action("e", preview_mode=True) == "edit"
    assert parse_confirm_action("r", preview_mode=True) == "retry"
    assert parse_confirm_action("s", preview_mode=True) == "skip"
    assert parse_confirm_action("q", preview_mode=True) == "quit"
