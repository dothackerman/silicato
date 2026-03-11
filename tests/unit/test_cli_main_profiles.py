from __future__ import annotations

from argparse import Namespace
from dataclasses import dataclass

import pytest

from silicato.ports.storage import SilicatoConfig
from silicato.ui.cli.runtime_plugins import RuntimeProfilePluginError, RuntimeSettings


@dataclass
class _TargetResult:
    target: str
    remembered_target_error: str | None = None


class _FakeConfigStore:
    def load(self) -> SilicatoConfig:
        return SilicatoConfig(tmux_target=None)

    def save(self, config: SilicatoConfig) -> None:
        _ = config


class _FakeResolveTargetUseCase:
    def __init__(self, _resolver: object) -> None:
        pass

    def execute(self, **_kwargs: object) -> _TargetResult:
        return _TargetResult(target="codex:0.1")


class _FakeRunCaptureTranscribeUseCase:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        pass


class _FakeLogTurnUseCase:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        pass


class _FakeConfirmTurnUseCase:
    def execute(self, *_args: object, **_kwargs: object) -> str | None:
        return None


def test_main_passes_tuned_auto_stop_settings_into_capture_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from silicato.ui.cli import main as cli_main

    args = Namespace(
        model="base",
        device="cpu",
        compute_type="int8",
        language="auto",
        sample_rate=16000,
        silence_stop_seconds=1.4,
        silence_rms_threshold=80,
        max_recording_seconds=0.0,
        input_device=None,
        tmux_target=None,
        pick_target=True,
        no_remember_target=False,
        preview=False,
        log_file=None,
        once=False,
        doctor=False,
        profile=None,
        spawn=False,
    )

    monkeypatch.setattr(cli_main, "parse_args", lambda: args)
    monkeypatch.setattr(cli_main, "require_binary", lambda *_a, **_k: None)
    monkeypatch.setattr(cli_main, "TomlConfigStore", _FakeConfigStore)
    monkeypatch.setattr(cli_main, "TmuxTargetResolver", lambda: object())
    monkeypatch.setattr(cli_main, "ResolveTargetUseCase", _FakeResolveTargetUseCase)
    monkeypatch.setattr(cli_main, "TmuxSender", lambda *_a, **_k: object())
    monkeypatch.setattr(cli_main, "SendTurnUseCase", lambda *_a, **_k: object())
    monkeypatch.setattr(cli_main, "WhisperSttAdapter", lambda *_a, **_k: object())
    monkeypatch.setattr(cli_main, "RunCaptureTranscribeUseCase", _FakeRunCaptureTranscribeUseCase)
    monkeypatch.setattr(cli_main, "JsonlTurnLogger", lambda *_a, **_k: object())
    monkeypatch.setattr(cli_main, "LogTurnUseCase", _FakeLogTurnUseCase)
    monkeypatch.setattr(cli_main, "ConfirmTurnUseCase", _FakeConfirmTurnUseCase)
    monkeypatch.setattr(cli_main, "prompt_turn_start", lambda: False)
    monkeypatch.setattr(
        cli_main,
        "resolve_runtime_settings",
        lambda **_k: RuntimeSettings(
            model="base",
            device="cpu",
            compute_type="int8",
            reason="manual settings",
        ),
    )
    monkeypatch.setattr(cli_main, "build_model", lambda *_a, **_k: (object(), "cpu", "int8"))

    captured_kwargs: dict[str, object] = {}

    def _fake_capture_adapter(**kwargs: object) -> object:
        captured_kwargs.update(kwargs)
        return object()

    monkeypatch.setattr(cli_main, "AlsaCaptureAdapter", _fake_capture_adapter)

    rc = cli_main.main()

    assert rc == 0
    assert captured_kwargs == {
        "silence_stop_seconds": 1.4,
        "silence_rms_threshold": 80,
        "max_recording_seconds": 0.0,
    }


def test_main_uses_profile_resolved_model_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    from silicato.ui.cli import main as cli_main

    args = Namespace(
        model="medium",
        device="cuda",
        compute_type="float16",
        language="auto",
        sample_rate=16000,
        silence_stop_seconds=1.4,
        silence_rms_threshold=80,
        max_recording_seconds=0.0,
        input_device=None,
        tmux_target=None,
        pick_target=True,
        no_remember_target=False,
        preview=False,
        log_file=None,
        once=False,
        doctor=False,
        profile="spawn",
        spawn=True,
    )

    monkeypatch.setattr(cli_main, "parse_args", lambda: args)
    monkeypatch.setattr(cli_main, "require_binary", lambda *_a, **_k: None)
    monkeypatch.setattr(cli_main, "TomlConfigStore", _FakeConfigStore)
    monkeypatch.setattr(cli_main, "TmuxTargetResolver", lambda: object())
    monkeypatch.setattr(cli_main, "ResolveTargetUseCase", _FakeResolveTargetUseCase)
    monkeypatch.setattr(cli_main, "TmuxSender", lambda *_a, **_k: object())
    monkeypatch.setattr(cli_main, "SendTurnUseCase", lambda *_a, **_k: object())
    monkeypatch.setattr(cli_main, "AlsaCaptureAdapter", lambda **_k: object())
    monkeypatch.setattr(cli_main, "WhisperSttAdapter", lambda *_a, **_k: object())
    monkeypatch.setattr(cli_main, "RunCaptureTranscribeUseCase", _FakeRunCaptureTranscribeUseCase)
    monkeypatch.setattr(cli_main, "JsonlTurnLogger", lambda *_a, **_k: object())
    monkeypatch.setattr(cli_main, "LogTurnUseCase", _FakeLogTurnUseCase)
    monkeypatch.setattr(cli_main, "ConfirmTurnUseCase", _FakeConfirmTurnUseCase)
    monkeypatch.setattr(cli_main, "prompt_turn_start", lambda: False)

    monkeypatch.setattr(
        cli_main,
        "resolve_runtime_settings",
        lambda **_k: RuntimeSettings(
            model="small",
            device="cuda",
            compute_type="int8_float16",
            reason="spawn test",
        ),
    )

    called: list[tuple[str, str, str]] = []

    def _fake_build_model(model: str, device: str, compute_type: str) -> tuple[object, str, str]:
        called.append((model, device, compute_type))
        return object(), device, compute_type

    monkeypatch.setattr(cli_main, "build_model", _fake_build_model)

    rc = cli_main.main()

    assert rc == 0
    assert called == [("small", "cuda", "int8_float16")]


def test_main_returns_nonzero_when_profile_plugin_resolution_fails(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from silicato.ui.cli import main as cli_main

    args = Namespace(
        model="medium",
        device="cuda",
        compute_type="float16",
        language="auto",
        sample_rate=16000,
        silence_stop_seconds=1.4,
        silence_rms_threshold=80,
        max_recording_seconds=0.0,
        input_device=None,
        tmux_target=None,
        pick_target=True,
        no_remember_target=False,
        preview=False,
        log_file=None,
        once=False,
        doctor=False,
        profile="eco",
        spawn=False,
    )

    monkeypatch.setattr(cli_main, "parse_args", lambda: args)
    monkeypatch.setattr(cli_main, "require_binary", lambda *_a, **_k: None)
    monkeypatch.setattr(cli_main, "TomlConfigStore", _FakeConfigStore)
    monkeypatch.setattr(cli_main, "TmuxTargetResolver", lambda: object())
    monkeypatch.setattr(cli_main, "ResolveTargetUseCase", _FakeResolveTargetUseCase)

    def _raise_profile_error(**_kwargs: object) -> RuntimeSettings:
        raise RuntimeProfilePluginError("missing plugin")

    monkeypatch.setattr(
        cli_main,
        "resolve_runtime_settings",
        _raise_profile_error,
    )

    rc = cli_main.main()

    assert rc == 1
    assert "Runtime profile error: missing plugin" in capsys.readouterr().err
