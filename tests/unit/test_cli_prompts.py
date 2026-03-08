from __future__ import annotations

import pytest

from silicato.ui.cli.prompts import prompt_confirm, prompt_edit_text, prompt_turn_start


def test_prompt_turn_start_accepts_enter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "")

    assert prompt_turn_start() is True


def test_prompt_turn_start_displays_start_recording_helper_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_prompts: list[str] = []

    def _input(prompt: str) -> str:
        seen_prompts.append(prompt)
        return ""

    monkeypatch.setattr("builtins.input", _input)

    assert prompt_turn_start() is True
    assert seen_prompts == ["Press Enter to start recording, or type 'q' then Enter to quit: "]


def test_prompt_turn_start_rejects_quit_aliases(monkeypatch: pytest.MonkeyPatch) -> None:
    for value in ("q", "quit", "exit"):
        monkeypatch.setattr("builtins.input", lambda _prompt, text=value: text)
        assert prompt_turn_start() is False


def test_prompt_turn_start_handles_eof(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def _raise_eof(_prompt: str) -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", _raise_eof)

    assert prompt_turn_start() is False
    assert capsys.readouterr().out == "\n"


def test_prompt_confirm_returns_raw_input(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: " y ")

    assert prompt_confirm() == " y "


def test_prompt_edit_text_keeps_current_on_empty(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "   ")

    assert prompt_edit_text("existing text") == "existing text"
    assert "Current transcript: existing text" in capsys.readouterr().out


def test_prompt_edit_text_returns_new_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "edited")

    assert prompt_edit_text("existing text") == "edited"
