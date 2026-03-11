from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from silicato.application.use_cases.manage_routes import (
    CheckRouteUseCase,
    InvalidRouteIdentifierError,
    ListRoutesUseCase,
    RemoveRouteUseCase,
    ResolveRouteUseCase,
    RouteAlreadyExistsError,
    RouteNotFoundError,
    SaveRouteUseCase,
    normalize_route_identifier,
)
from silicato.ports.storage import NamedPaneRoute
from silicato.ports.targeting import InvalidTmuxTargetError, PaneEntry


class FakeRouteStore:
    def __init__(self, routes: tuple[NamedPaneRoute, ...] = ()) -> None:
        self.routes = {route.identifier: route for route in routes}

    def list_routes(self) -> tuple[NamedPaneRoute, ...]:
        return tuple(self.routes[key] for key in sorted(self.routes))

    def get(self, identifier: str) -> NamedPaneRoute | None:
        return self.routes.get(identifier)

    def upsert(self, route: NamedPaneRoute) -> Path:
        self.routes[route.identifier] = route
        return Path("/tmp/routes.toml")

    def delete(self, identifier: str) -> Path | None:
        if identifier not in self.routes:
            return None
        del self.routes[identifier]
        return Path("/tmp/routes.toml")


class FakeTargetResolver:
    def __init__(self) -> None:
        self.validated: list[str] = []
        self.invalid_target: str | None = None

    def validate_target(self, target: str) -> None:
        self.validated.append(target)
        if self.invalid_target == target:
            raise InvalidTmuxTargetError("bad target")

    def list_panes(self) -> list[PaneEntry]:
        return []

    def pick_target_interactive(self, panes: list[PaneEntry], **kwargs: object) -> str:
        _ = panes
        _ = kwargs
        raise AssertionError("picker should not be used by route checks")

    def print_no_tmux_guidance(self, **kwargs: object) -> None:
        _ = kwargs


def test_normalize_route_identifier_lowercases_and_trims() -> None:
    assert normalize_route_identifier("  Gaia_01 ") == "gaia_01"


def test_normalize_route_identifier_rejects_invalid_values() -> None:
    with pytest.raises(InvalidRouteIdentifierError, match=r"\[a-z0-9_-\]\+"):
        normalize_route_identifier("bad route")


def test_save_route_creates_route_with_timestamp() -> None:
    store = FakeRouteStore()
    use_case = SaveRouteUseCase(
        store,
        now_fn=lambda: datetime(2026, 3, 10, 12, 0, tzinfo=UTC),
    )

    result = use_case.execute(identifier=" Gaia ", tmux_target=" codex:0.1 ")

    assert result.created is True
    assert result.route == NamedPaneRoute(
        identifier="gaia",
        tmux_target="codex:0.1",
        updated_at="2026-03-10T12:00:00+00:00",
    )
    assert store.get("gaia") == result.route


def test_save_route_requires_overwrite_for_different_target() -> None:
    store = FakeRouteStore(
        (
            NamedPaneRoute(
                identifier="gaia",
                tmux_target="codex:0.1",
                updated_at="2026-03-10T10:00:00+00:00",
            ),
        )
    )
    use_case = SaveRouteUseCase(store)

    with pytest.raises(RouteAlreadyExistsError, match="already exists"):
        use_case.execute(identifier="gaia", tmux_target="codex:0.2")


def test_save_route_allows_explicit_overwrite() -> None:
    store = FakeRouteStore(
        (
            NamedPaneRoute(
                identifier="gaia",
                tmux_target="codex:0.1",
                updated_at="2026-03-10T10:00:00+00:00",
            ),
        )
    )
    use_case = SaveRouteUseCase(
        store,
        now_fn=lambda: datetime(2026, 3, 10, 13, 30, tzinfo=UTC),
    )

    result = use_case.execute(
        identifier="gaia",
        tmux_target="codex:0.2",
        allow_overwrite=True,
    )

    assert result.created is False
    assert result.route.tmux_target == "codex:0.2"
    assert result.route.updated_at == "2026-03-10T13:30:00+00:00"


def test_list_routes_returns_sorted_routes() -> None:
    store = FakeRouteStore(
        (
            NamedPaneRoute("soil", "farm:0.1", "2026-03-10T12:00:00+00:00"),
            NamedPaneRoute("gaia", "codex:0.1", "2026-03-10T12:00:00+00:00"),
        )
    )

    routes = ListRoutesUseCase(store).execute()

    assert [route.identifier for route in routes] == ["gaia", "soil"]


def test_resolve_route_raises_when_missing() -> None:
    with pytest.raises(RouteNotFoundError, match="was not found"):
        ResolveRouteUseCase(FakeRouteStore()).execute("missing")


def test_remove_route_returns_false_for_missing_route() -> None:
    assert RemoveRouteUseCase(FakeRouteStore()).execute("missing") is False


def test_check_route_reuses_target_resolver_validation() -> None:
    store = FakeRouteStore((NamedPaneRoute("gaia", "codex:0.1", "2026-03-10T12:00:00+00:00"),))
    resolver = FakeTargetResolver()

    route = CheckRouteUseCase(store, resolver).execute("gaia")

    assert route.tmux_target == "codex:0.1"
    assert resolver.validated == ["codex:0.1"]


def test_check_route_propagates_target_validation_failures() -> None:
    store = FakeRouteStore((NamedPaneRoute("gaia", "codex:0.1", "2026-03-10T12:00:00+00:00"),))
    resolver = FakeTargetResolver()
    resolver.invalid_target = "codex:0.1"

    with pytest.raises(InvalidTmuxTargetError, match="bad target"):
        CheckRouteUseCase(store, resolver).execute("gaia")
