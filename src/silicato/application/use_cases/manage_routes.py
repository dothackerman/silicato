"""Use cases for named tmux pane route management."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from silicato.ports.storage import NamedPaneRoute, RouteStorePort
from silicato.ports.targeting import TargetResolverPort

_ROUTE_IDENTIFIER_RE = re.compile(r"^[a-z0-9_-]+$")


class RouteManagementError(RuntimeError):
    """Base class for route management failures."""


class InvalidRouteIdentifierError(RouteManagementError):
    """Raised when a route identifier does not match the allowed format."""


class RouteAlreadyExistsError(RouteManagementError):
    """Raised when creating a route would overwrite an existing target."""


class RouteNotFoundError(RouteManagementError):
    """Raised when a named route does not exist."""


def normalize_route_identifier(identifier: str) -> str:
    """Return the canonical route identifier or raise."""

    normalized = identifier.strip().lower()
    if not normalized or not _ROUTE_IDENTIFIER_RE.fullmatch(normalized):
        raise InvalidRouteIdentifierError(
            "route identifier must match [a-z0-9_-]+ and cannot be blank"
        )
    return normalized


def normalize_tmux_target(target: str) -> str:
    """Return a non-empty tmux target string."""

    normalized = target.strip()
    if not normalized:
        raise ValueError("tmux target cannot be blank")
    return normalized


@dataclass(frozen=True)
class SaveRouteResult:
    route: NamedPaneRoute
    created: bool


class SaveRouteUseCase:
    """Create or update a named route in the route store."""

    def __init__(
        self,
        store: RouteStorePort,
        *,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._store = store
        self._now_fn = now_fn or (lambda: datetime.now(tz=UTC))

    def execute(
        self,
        *,
        identifier: str,
        tmux_target: str,
        allow_overwrite: bool = False,
    ) -> SaveRouteResult:
        normalized_identifier = normalize_route_identifier(identifier)
        normalized_target = normalize_tmux_target(tmux_target)
        existing = self._store.get(normalized_identifier)

        if existing is not None:
            if existing.tmux_target == normalized_target:
                return SaveRouteResult(route=existing, created=False)
            if not allow_overwrite:
                raise RouteAlreadyExistsError(
                    f"route '{normalized_identifier}' already exists for {existing.tmux_target}"
                )

        route = NamedPaneRoute(
            identifier=normalized_identifier,
            tmux_target=normalized_target,
            updated_at=self._now_fn().isoformat(),
        )
        self._store.upsert(route)
        return SaveRouteResult(route=route, created=existing is None)


class ListRoutesUseCase:
    """Return the stored named routes."""

    def __init__(self, store: RouteStorePort) -> None:
        self._store = store

    def execute(self) -> tuple[NamedPaneRoute, ...]:
        return self._store.list_routes()


class ResolveRouteUseCase:
    """Resolve one stored route by identifier."""

    def __init__(self, store: RouteStorePort) -> None:
        self._store = store

    def execute(self, identifier: str) -> NamedPaneRoute:
        normalized_identifier = normalize_route_identifier(identifier)
        route = self._store.get(normalized_identifier)
        if route is None:
            raise RouteNotFoundError(f"route '{normalized_identifier}' was not found")
        return route


class RemoveRouteUseCase:
    """Remove one stored route by identifier."""

    def __init__(self, store: RouteStorePort) -> None:
        self._store = store

    def execute(self, identifier: str) -> bool:
        normalized_identifier = normalize_route_identifier(identifier)
        return self._store.delete(normalized_identifier) is not None


class CheckRouteUseCase:
    """Validate a stored route against the tmux target resolver."""

    def __init__(self, store: RouteStorePort, resolver: TargetResolverPort) -> None:
        self._resolve = ResolveRouteUseCase(store)
        self._resolver = resolver

    def execute(self, identifier: str) -> NamedPaneRoute:
        route = self._resolve.execute(identifier)
        self._resolver.validate_target(route.tmux_target)
        return route
