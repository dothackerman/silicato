from __future__ import annotations

from pathlib import Path

from silicato.adapters.storage.config_store import TomlConfigStore
from silicato.application.use_cases.resolve_target import ResolveTargetUseCase
from silicato.application.use_cases.run_capture_transcribe import (
    RunCaptureTranscribeUseCase,
    TurnConfig,
)
from silicato.domain.confirm_actions import parse_confirm_action
from silicato.ports.audio import AudioChunkObserver
from silicato.ports.storage import SilicatoConfig
from silicato.ports.stt import TranscriptResult
from silicato.ports.targeting import PaneEntry


class CaptureAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def record_once(
        self,
        output_path: Path,
        sample_rate: int,
        input_device: str | None,
        on_chunk: AudioChunkObserver | None = None,
    ) -> None:
        self.calls += 1
        output_path.write_bytes(b"RIFF....WAVE")
        _ = sample_rate
        _ = input_device
        _ = on_chunk


class SttAdapter:
    def __init__(self, transcripts: list[str]) -> None:
        self._transcripts = transcripts
        self._index = 0

    def transcribe(self, wav_path: Path, language: str) -> TranscriptResult:
        _ = wav_path
        text = self._transcripts[self._index]
        self._index += 1
        return TranscriptResult(text=text, language=language)


class SenderAdapter:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send(self, text: str) -> None:
        self.messages.append(text)


class FlakySenderAdapter(SenderAdapter):
    def __init__(self, failures_before_success: int) -> None:
        super().__init__()
        self.failures_before_success = failures_before_success

    def send(self, text: str) -> None:
        if self.failures_before_success > 0:
            self.failures_before_success -= 1
            raise RuntimeError("send failed")
        super().send(text)


class FakeTargetResolver:
    def __init__(self) -> None:
        self.validated: list[str] = []

    def validate_target(self, target: str) -> None:
        self.validated.append(target)

    def list_panes(self) -> list[PaneEntry]:
        return [PaneEntry(target="picked:0.1", command="bash", title="main")]

    def pick_target_interactive(self, panes: list[PaneEntry], **kwargs: object) -> str:
        _ = panes
        _ = kwargs
        return "picked:0.1"

    def print_no_tmux_guidance(self, **kwargs: object) -> None:
        _ = kwargs


class FakeOrchestrator:
    def __init__(self, capture: CaptureAdapter, stt: SttAdapter, sender: SenderAdapter) -> None:
        self.capture = capture
        self.stt = stt
        self.sender = sender
        self.runner = RunCaptureTranscribeUseCase(capture, stt)

    def run_turn(self, wav_path: Path, config: TurnConfig, *, send_text: bool) -> TranscriptResult:
        result = self.runner.execute(wav_path=wav_path, config=config)
        if send_text:
            self.sender.send(result.text)
        return result


def run_fake_turn_direct(
    *,
    orchestrator: FakeOrchestrator,
    tmp_path: Path,
) -> tuple[str, str | None]:
    result = orchestrator.run_turn(
        wav_path=tmp_path / f"turn-{orchestrator.capture.calls}.wav",
        config=TurnConfig(language="auto"),
        send_text=False,
    )
    current_text = result.text
    if not current_text:
        return "skip", None

    try:
        orchestrator.sender.send(current_text)
    except RuntimeError:
        return "send_failed", None
    return "send", current_text


def run_fake_turn_preview(
    *,
    orchestrator: FakeOrchestrator,
    tmp_path: Path,
    decision_inputs: list[str],
    edit_inputs: list[str],
) -> tuple[str, str | None]:
    decisions = iter(decision_inputs)
    edits = iter(edit_inputs)
    turn_index = 0

    while True:
        result = orchestrator.run_turn(
            wav_path=tmp_path / f"preview-turn-{turn_index}.wav",
            config=TurnConfig(language="auto"),
            send_text=False,
        )
        turn_index += 1
        current_text = result.text

        while True:
            action = parse_confirm_action(next(decisions), preview_mode=True)
            assert action is not None
            if action == "edit":
                current_text = next(edits)
                continue
            if action == "retry":
                break
            if action == "skip":
                return "skip", None
            if action == "quit":
                return "quit", None
            orchestrator.sender.send(current_text)
            return "send", current_text


def test_end_to_end_fake_turn_direct_send_without_preview(tmp_path: Path) -> None:
    sender = SenderAdapter()
    orchestrator = FakeOrchestrator(
        capture=CaptureAdapter(),
        stt=SttAdapter(["integration transcript"]),
        sender=sender,
    )

    action, sent_text = run_fake_turn_direct(orchestrator=orchestrator, tmp_path=tmp_path)

    assert action == "send"
    assert sent_text == "integration transcript"
    assert sender.messages == ["integration transcript"]


def test_end_to_end_fake_turn_direct_empty_transcript_skips_send(tmp_path: Path) -> None:
    sender = SenderAdapter()
    orchestrator = FakeOrchestrator(
        capture=CaptureAdapter(),
        stt=SttAdapter([""]),
        sender=sender,
    )

    action, sent_text = run_fake_turn_direct(orchestrator=orchestrator, tmp_path=tmp_path)

    assert action == "skip"
    assert sent_text is None
    assert sender.messages == []


def test_end_to_end_fake_turn_preview_send_edit_retry_skip(tmp_path: Path) -> None:
    # send
    sender = SenderAdapter()
    send_orchestrator = FakeOrchestrator(
        capture=CaptureAdapter(),
        stt=SttAdapter(["integration transcript"]),
        sender=sender,
    )
    action, sent_text = run_fake_turn_preview(
        orchestrator=send_orchestrator,
        tmp_path=tmp_path,
        decision_inputs=["y"],
        edit_inputs=[],
    )
    assert action == "send"
    assert sent_text == "integration transcript"
    assert sender.messages == ["integration transcript"]

    # edit then send
    sender = SenderAdapter()
    edit_orchestrator = FakeOrchestrator(
        capture=CaptureAdapter(),
        stt=SttAdapter(["raw text"]),
        sender=sender,
    )
    action, sent_text = run_fake_turn_preview(
        orchestrator=edit_orchestrator,
        tmp_path=tmp_path,
        decision_inputs=["e", "y"],
        edit_inputs=["edited text"],
    )
    assert action == "send"
    assert sent_text == "edited text"
    assert sender.messages == ["edited text"]

    # retry then send
    sender = SenderAdapter()
    retry_capture = CaptureAdapter()
    retry_orchestrator = FakeOrchestrator(
        capture=retry_capture,
        stt=SttAdapter(["first", "second"]),
        sender=sender,
    )
    action, sent_text = run_fake_turn_preview(
        orchestrator=retry_orchestrator,
        tmp_path=tmp_path,
        decision_inputs=["r", "y"],
        edit_inputs=[],
    )
    assert action == "send"
    assert sent_text == "second"
    assert sender.messages == ["second"]
    assert retry_capture.calls == 2

    # skip
    sender = SenderAdapter()
    skip_orchestrator = FakeOrchestrator(
        capture=CaptureAdapter(),
        stt=SttAdapter(["discard me"]),
        sender=sender,
    )
    action, sent_text = run_fake_turn_preview(
        orchestrator=skip_orchestrator,
        tmp_path=tmp_path,
        decision_inputs=["s"],
        edit_inputs=[],
    )
    assert action == "skip"
    assert sent_text is None
    assert sender.messages == []

    # quit
    sender = SenderAdapter()
    quit_orchestrator = FakeOrchestrator(
        capture=CaptureAdapter(),
        stt=SttAdapter(["anything"]),
        sender=sender,
    )
    action, sent_text = run_fake_turn_preview(
        orchestrator=quit_orchestrator,
        tmp_path=tmp_path,
        decision_inputs=["q"],
        edit_inputs=[],
    )
    assert action == "quit"
    assert sent_text is None
    assert sender.messages == []


def test_direct_send_failure_does_not_block_next_turn(tmp_path: Path) -> None:
    sender = FlakySenderAdapter(failures_before_success=1)
    orchestrator = FakeOrchestrator(
        capture=CaptureAdapter(),
        stt=SttAdapter(["first", "second"]),
        sender=sender,
    )

    action, sent_text = run_fake_turn_direct(orchestrator=orchestrator, tmp_path=tmp_path)
    assert action == "send_failed"
    assert sent_text is None

    action, sent_text = run_fake_turn_direct(orchestrator=orchestrator, tmp_path=tmp_path)
    assert action == "send"
    assert sent_text == "second"
    assert sender.messages == ["second"]


def test_remembered_target_reuse_and_cli_override(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_store = TomlConfigStore(path=config_path)
    config_store.save(SilicatoConfig(tmux_target="remembered:0.1"))
    loaded = config_store.load()
    assert loaded.tmux_target == "remembered:0.1"

    resolver = FakeTargetResolver()
    use_case = ResolveTargetUseCase(resolver)

    resolved = use_case.execute(
        explicit_target=None,
        pick_target=False,
        env_target=None,
        remembered_target=loaded.tmux_target,
    )
    assert resolved.target == "remembered:0.1"

    override = use_case.execute(
        explicit_target="override:0.2",
        pick_target=False,
        env_target=None,
        remembered_target=loaded.tmux_target,
    )
    assert override.target == "override:0.2"
    assert resolver.validated == ["remembered:0.1", "override:0.2"]
