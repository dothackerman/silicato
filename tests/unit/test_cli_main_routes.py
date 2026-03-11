from __future__ import annotations

from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path

import pytest

from silicato.ports.storage import NamedPaneRoute


@dataclass
class _SaveRouteResult:
    route: NamedPaneRoute
    created: bool


def test_main_dispatches_route_add(monkeypatch: pytest.MonkeyPatch) -> None:
    from silicato.ui.cli import main as cli_main

    args = Namespace(
        command="route",
        route_command="add",
        identifier="gaia",
        tmux_target="codex:0.1",
        force=True,
        doctor=False,
    )

    captured: dict[str, object] = {}

    class _FakeSaveRouteUseCase:
        def __init__(self, store: object) -> None:
            captured["store"] = store

        def execute(self, **kwargs: object) -> _SaveRouteResult:
            captured.update(kwargs)
            return _SaveRouteResult(
                route=NamedPaneRoute(
                    identifier="gaia",
                    tmux_target="codex:0.1",
                    updated_at="2026-03-10T12:00:00+00:00",
                ),
                created=True,
            )

    monkeypatch.setattr(cli_main, "parse_args", lambda: args)
    monkeypatch.setattr(cli_main, "TomlRouteStore", lambda: object())
    monkeypatch.setattr(cli_main, "SaveRouteUseCase", _FakeSaveRouteUseCase)

    rc = cli_main.main()

    assert rc == 0
    assert captured["identifier"] == "gaia"
    assert captured["tmux_target"] == "codex:0.1"
    assert captured["allow_overwrite"] is True


def test_main_dispatches_named_route_injection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from silicato.ui.cli import main as cli_main

    payload_path = tmp_path / "payload.txt"
    payload_path.write_text("inject this", encoding="utf-8")
    args = Namespace(
        command="inject",
        route_identifier="gaia",
        inject_text=None,
        inject_from_file=payload_path,
        doctor=False,
    )

    captured: dict[str, object] = {}

    class _FakeCheckRouteUseCase:
        def __init__(self, store: object, resolver: object) -> None:
            captured["store"] = store
            captured["resolver"] = resolver

        def execute(self, identifier: str) -> NamedPaneRoute:
            captured["identifier"] = identifier
            return NamedPaneRoute(
                identifier="gaia",
                tmux_target="codex:0.1",
                updated_at="2026-03-10T12:00:00+00:00",
            )

    class _FakeSendTurnUseCase:
        def __init__(self, sender: object) -> None:
            captured["sender"] = sender

        def execute(self, text: str) -> None:
            captured["text"] = text

    monkeypatch.setattr(cli_main, "parse_args", lambda: args)
    monkeypatch.setattr(cli_main, "require_binary", lambda *_a, **_k: None)
    monkeypatch.setattr(cli_main, "TomlRouteStore", lambda: object())
    monkeypatch.setattr(cli_main, "TmuxTargetResolver", lambda: object())
    monkeypatch.setattr(cli_main, "CheckRouteUseCase", _FakeCheckRouteUseCase)
    monkeypatch.setattr(cli_main, "TmuxSender", lambda target: {"target": target})
    monkeypatch.setattr(cli_main, "SendTurnUseCase", _FakeSendTurnUseCase)

    rc = cli_main.main()

    assert rc == 0
    assert captured["identifier"] == "gaia"
    assert captured["text"] == "inject this"
    assert captured["sender"] == {"target": "codex:0.1"}
