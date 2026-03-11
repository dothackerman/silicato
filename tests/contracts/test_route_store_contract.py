from __future__ import annotations

from pathlib import Path

from silicato.adapters.storage.route_store import TomlRouteStore
from silicato.ports.storage import NamedPaneRoute


def test_route_store_contract_round_trip_and_sorting(tmp_path: Path) -> None:
    path = tmp_path / "routes.toml"
    store = TomlRouteStore(path=path)

    store.upsert(
        NamedPaneRoute(
            identifier="soil",
            tmux_target="farm:0.1",
            updated_at="2026-03-10T12:00:00+00:00",
        )
    )
    store.upsert(
        NamedPaneRoute(
            identifier="gaia",
            tmux_target="codex:0.1",
            updated_at="2026-03-10T12:05:00+00:00",
        )
    )

    routes = store.list_routes()

    assert [route.identifier for route in routes] == ["gaia", "soil"]
    assert store.get("gaia") == NamedPaneRoute(
        identifier="gaia",
        tmux_target="codex:0.1",
        updated_at="2026-03-10T12:05:00+00:00",
    )


def test_route_store_contract_missing_file_returns_empty_collection(tmp_path: Path) -> None:
    store = TomlRouteStore(path=tmp_path / "missing.toml")

    assert store.list_routes() == ()
    assert store.get("gaia") is None


def test_route_store_contract_delete_removes_route(tmp_path: Path) -> None:
    path = tmp_path / "routes.toml"
    store = TomlRouteStore(path=path)
    store.upsert(
        NamedPaneRoute(
            identifier="gaia",
            tmux_target="codex:0.1",
            updated_at="2026-03-10T12:00:00+00:00",
        )
    )

    deleted_path = store.delete("gaia")

    assert deleted_path == path
    assert store.get("gaia") is None
