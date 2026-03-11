from __future__ import annotations

from pathlib import Path

import pytest

from silicato.adapters.storage.route_store import TomlRouteStore, default_routes_path


def test_default_routes_path_uses_xdg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/xdg-config")
    assert default_routes_path() == Path("/tmp/xdg-config/silicato/routes.toml")


def test_route_store_rejects_duplicate_identifiers(tmp_path: Path) -> None:
    path = tmp_path / "routes.toml"
    path.write_text(
        """
version = 1

[[route]]
identifier = "gaia"
tmux_target = "codex:0.1"
updated_at = "2026-03-10T12:00:00+00:00"

[[route]]
identifier = "gaia"
tmux_target = "codex:0.2"
updated_at = "2026-03-10T12:05:00+00:00"
""".strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="Duplicate route identifier"):
        TomlRouteStore(path=path).list_routes()
