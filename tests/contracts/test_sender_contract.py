from __future__ import annotations

import subprocess
import time

import pytest

from dialogos.adapters.tmux.sender import TmuxSender


def test_tmux_sender_contract_sends_message(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []
    sleep_calls: list[float] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        _ = kwargs
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(time, "sleep", sleep_calls.append)

    sender = TmuxSender("codex:0.1")
    sender.send("hello")

    assert calls == [
        ["tmux", "send-keys", "-t", "codex:0.1", "hello"],
        ["tmux", "send-keys", "-t", "codex:0.1", "Enter"],
    ]
    assert sleep_calls == [TmuxSender.SUBMIT_DELAY_SECONDS]


def test_tmux_sender_contract_raises_on_text_send_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        _ = kwargs
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
        if len(calls) == 1:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
        return subprocess.CompletedProcess(
            args=cmd, returncode=1, stdout="", stderr="submit key failed"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)

    sender = TmuxSender("codex:0.1")
    with pytest.raises(RuntimeError, match="submit key failed"):
        sender.send("hello")
