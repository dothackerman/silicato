"""Named route storage adapter."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from silicato.ports.storage import NamedPaneRoute, RouteStorePort


def default_routes_path() -> Path:
    """Resolve the default named-routes path using XDG conventions."""

    xdg_root = os.environ.get("XDG_CONFIG_HOME")
    if xdg_root:
        return Path(xdg_root) / "silicato" / "routes.toml"
    return Path.home() / ".config" / "silicato" / "routes.toml"


class TomlRouteStore(RouteStorePort):
    """Adapter for persisted named pane routes."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path

    def list_routes(self) -> tuple[NamedPaneRoute, ...]:
        routes = self._load_routes()
        return tuple(routes[key] for key in sorted(routes))

    def get(self, identifier: str) -> NamedPaneRoute | None:
        return self._load_routes().get(identifier)

    def upsert(self, route: NamedPaneRoute) -> Path:
        route_path = self._path or default_routes_path()
        routes = self._load_routes()
        routes[route.identifier] = route
        self._write_routes(route_path, routes)
        return route_path

    def delete(self, identifier: str) -> Path | None:
        route_path = self._path or default_routes_path()
        routes = self._load_routes()
        if identifier not in routes:
            return None
        del routes[identifier]
        self._write_routes(route_path, routes)
        return route_path

    def _load_routes(self) -> dict[str, NamedPaneRoute]:
        route_path = self._path or default_routes_path()
        if not route_path.exists():
            return {}

        try:
            data = tomllib.loads(route_path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise RuntimeError(f"Failed to load route file at {route_path}: {exc}") from exc

        version = data.get("version", 1)
        if version != 1:
            raise RuntimeError(f"Invalid route file version in {route_path}: expected 1")

        entries = data.get("route", [])
        if not isinstance(entries, list):
            raise RuntimeError(f"Invalid route file in {route_path}: expected [[route]] entries")

        routes: dict[str, NamedPaneRoute] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                raise RuntimeError(f"Invalid route entry in {route_path}: expected table")
            identifier = _required_string(entry, "identifier", route_path)
            tmux_target = _required_string(entry, "tmux_target", route_path)
            updated_at = _required_string(entry, "updated_at", route_path)
            if identifier in routes:
                raise RuntimeError(f"Duplicate route identifier in {route_path}: {identifier}")
            routes[identifier] = NamedPaneRoute(
                identifier=identifier,
                tmux_target=tmux_target,
                updated_at=updated_at,
            )
        return routes

    def _write_routes(self, route_path: Path, routes: dict[str, NamedPaneRoute]) -> None:
        route_path.parent.mkdir(parents=True, exist_ok=True)

        lines = ["version = 1", ""]
        for identifier in sorted(routes):
            route = routes[identifier]
            lines.extend(
                [
                    "[[route]]",
                    f"identifier = {_quote(route.identifier)}",
                    f"tmux_target = {_quote(route.tmux_target)}",
                    f"updated_at = {_quote(route.updated_at)}",
                    "",
                ]
            )

        route_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _required_string(entry: dict[str, object], key: str, route_path: Path) -> str:
    raw = entry.get(key)
    if not isinstance(raw, str):
        raise RuntimeError(f"Invalid {key} in {route_path}: expected string")
    normalized = raw.strip()
    if not normalized:
        raise RuntimeError(f"Invalid {key} in {route_path}: cannot be blank")
    return normalized


def _quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
