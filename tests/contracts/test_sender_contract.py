from __future__ import annotations

import subprocess
import time

import pytest

from silicato.adapters.tmux.sender import TmuxSender


def test_tmux_sender_contract_sends_message(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []
    sleep_calls: list[float] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        _ = kwargs
        if cmd[:3] == ["tmux", "capture-pane", "-pt"]:
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout="idle prompt", stderr=""
            )
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(time, "sleep", sleep_calls.append)

    sender = TmuxSender("codex:0.1")
    sender.send("hello")

    assert calls == [
        ["tmux", "capture-pane", "-pt", "codex:0.1"],
        ["tmux", "send-keys", "-t", "codex:0.1", "hello"],
        ["tmux", "send-keys", "-t", "codex:0.1", "Enter"],
    ]
    assert TmuxSender.SUBMIT_DELAY_SECONDS == pytest.approx(0.25)
    assert sleep_calls == [TmuxSender.SUBMIT_DELAY_SECONDS]


def test_tmux_sender_contract_raises_on_text_send_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        _ = kwargs
        if cmd[:3] == ["tmux", "capture-pane", "-pt"]:
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout="idle prompt", stderr=""
            )
        return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="tmux error")

    monkeypatch.setattr(subprocess, "run", fake_run)

    sender = TmuxSender("codex:0.1")
    with pytest.raises(RuntimeError, match="tmux error"):
        sender.send("hello")


def test_tmux_sender_contract_raises_on_submit_key_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        _ = kwargs
        if len(calls) <= 2:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
        return subprocess.CompletedProcess(
            args=cmd, returncode=1, stdout="", stderr="submit key failed"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)

    sender = TmuxSender("codex:0.1")
    with pytest.raises(RuntimeError, match="submit key failed"):
        sender.send("hello")


def test_tmux_sender_contract_raises_when_target_is_busy(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        _ = kwargs
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=0,
            stdout="● Thinking (Esc to cancel)\nshift+tab switch mode · ctrl+q enqueue",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    sender = TmuxSender("codex:0.1")
    with pytest.raises(RuntimeError, match="tmux target is busy"):
        sender.send("hello")

    assert calls == [["tmux", "capture-pane", "-pt", "codex:0.1"]]


def test_tmux_sender_contract_waits_for_environment_load_before_sending(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        _ = kwargs
        if cmd[:3] == ["tmux", "capture-pane", "-pt"] and len(calls) == 1:
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout="● Loading environment:",
                stderr="",
            )
        if cmd[:3] == ["tmux", "capture-pane", "-pt"]:
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout="idle prompt", stderr=""
            )
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    sleep_calls: list[float] = []
    monkeypatch.setattr(time, "sleep", sleep_calls.append)

    sender = TmuxSender("codex:0.1")
    sender.send("hello")

    assert calls == [
        ["tmux", "capture-pane", "-pt", "codex:0.1"],
        ["tmux", "capture-pane", "-pt", "codex:0.1"],
        ["tmux", "capture-pane", "-pt", "codex:0.1"],
        ["tmux", "send-keys", "-t", "codex:0.1", "hello"],
        ["tmux", "send-keys", "-t", "codex:0.1", "Enter"],
    ]
    assert TmuxSender.READY_WAIT_POLL_SECONDS in sleep_calls
    assert TmuxSender.READY_STABILIZATION_SECONDS in sleep_calls
    assert TmuxSender.SUBMIT_DELAY_SECONDS in sleep_calls


def test_tmux_sender_contract_raises_when_environment_stays_loading(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        _ = kwargs
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=0,
            stdout="● Loading environment:",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(TmuxSender, "READY_WAIT_TIMEOUT_SECONDS", 0.0)

    sender = TmuxSender("codex:0.1")
    with pytest.raises(RuntimeError, match="still loading environment"):
        sender.send("hello")


def test_tmux_sender_contract_waits_for_blank_startup_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        _ = kwargs
        if cmd[:3] == ["tmux", "capture-pane", "-pt"] and len(calls) == 1:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
        if cmd[:3] == ["tmux", "capture-pane", "-pt"]:
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout="ready prompt", stderr=""
            )
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)

    sender = TmuxSender("codex:0.1")
    sender.send("hello")

    assert calls == [
        ["tmux", "capture-pane", "-pt", "codex:0.1"],
        ["tmux", "capture-pane", "-pt", "codex:0.1"],
        ["tmux", "capture-pane", "-pt", "codex:0.1"],
        ["tmux", "send-keys", "-t", "codex:0.1", "hello"],
        ["tmux", "send-keys", "-t", "codex:0.1", "Enter"],
    ]
