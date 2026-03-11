# Silicato Spec - Named Pane Routing

Status: Approved for implementation
Created on: 2026-03-10

## Problem

Silicato can remember one raw tmux target, but it cannot manage stable human-readable pane identifiers for multi-pane workflows.
That forces operators to reuse brittle `session:window.pane` strings and increases routing mistakes.

## Goal

Add named pane routing as a core Silicato feature, not as a runtime plugin.

## Frozen seam

1. Routing is a core product feature.
2. Route persistence uses a dedicated route store abstraction.
3. Route persistence is TOML-backed inside the Silicato config directory.
4. Route storage is separate from the existing remembered-target config path.
5. Route validation reuses the existing tmux targeting boundary instead of reimplementing tmux checks in CLI code.

## Architecture shape

### Ports

- Extend [`src/silicato/ports/storage.py`](/home/oriol/Projects/private/silicato/src/silicato/ports/storage.py) with route-oriented value objects and a dedicated `RouteStorePort`.
- Route identifiers are validated in application logic, not in CLI parsing.
- Identifier format for MVP: `[a-z0-9_-]+`.

### Adapters

- Add a TOML-backed route adapter under `src/silicato/adapters/storage/`.
- Default path: `~/.config/silicato/routes.toml` or `$XDG_CONFIG_HOME/silicato/routes.toml`.
- File shape stays adapter-private, but it must preserve:
  - identifier
  - tmux target
  - updated timestamp

### Application

- Add route-focused use cases for:
  - add/update
  - list
  - remove
  - resolve
  - check
- `check` must validate the stored tmux target through `TargetResolverPort.validate_target`.
- Route CRUD policy lives in application, not CLI.

### UI / Merger ownership

- Shared CLI entrypoints, docs, business rules, and cross-track integration tests remain merger-owned:
  - `src/silicato/ui/cli/main.py`
  - `src/silicato/ui/cli/args.py`
  - `README.md`
  - `docs/user/*`
  - `docs/dev/business-rules.toml`
  - cross-track integration tests

## Worker A scope

Owned for Wave 1:
- `src/silicato/ports/storage.py`
- new route-oriented application files under `src/silicato/application/use_cases/`
- new route-oriented adapter files under `src/silicato/adapters/storage/`
- routing unit/contract/integration tests that do not require shared CLI ownership

## Non-goals

1. No runtime plugin architecture for routing.
2. No JSON side store.
3. No tmux validation logic inside CLI flags or argparse callbacks.
4. No shared-network route registry.

## Tradeoffs

1. A separate `routes.toml` file reduces coupling with remembered-target config, but it creates one more persisted artifact.
2. Keeping CLI work merger-owned slows immediate end-user exposure slightly, but it prevents worker overlap in the highest-conflict files.

## Failure modes to guard

1. Identifier collisions overwrite routes silently.
2. Stale routes resolve but fail later because tmux validation is skipped.
3. Routing is merged as a plugin-shaped abstraction instead of a focused storage/use-case feature.

## Acceptance criteria

1. A route can be persisted, listed, updated, removed, and resolved by identifier.
2. Stored targets are pane-scoped and validated through the tmux targeting boundary when checked.
3. Routes persist under the Silicato config directory in TOML form.
4. CLI integration for `route` and `inject --to <id>` can be added by the merger without redesigning worker-owned internals.
