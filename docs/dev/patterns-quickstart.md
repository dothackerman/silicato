# Patterns Quickstart

Use this file as the mandatory 10-15 minute bootstrap for Milestone 2 work.

## One-page architecture map

Layers and allowed direction:
1. `ui` -> parse args, prompt user, wire dependencies
2. `application` -> run use-cases and orchestrate flow
3. `domain` -> pure state and transition rules
4. `ports` -> interfaces for side effects
5. `adapters` -> concrete implementations of ports

Allowed dependency flow:
- `ui -> application -> domain`
- `application -> ports`
- `adapters -> ports`
- `ui -> adapters` for composition only

## Five core rules

1. Domain stays pure.
- No `subprocess`, filesystem, env reads, terminal I/O, network I/O.

2. Application owns orchestration.
- Use-cases call domain and ports; they do not import adapters.

3. Adapters only implement ports.
- Adapter behavior is side-effectful but isolated behind contracts.

4. UI is composition root, not business logic.
- CLI can parse/prompt/wire; turn decisions belong in application/domain.

5. Boundaries are enforced, not optional.
- Run `make test-arch` and `make test-rules-fast` during development and `make gate` before push.

## If you only remember three things

1. Do not import adapters from application or domain.
2. Put decision logic in domain/application, not CLI prompt code.
3. Before handoff, run `make test-arch`, `make test-rules-fast`, and then `make gate`.

## Fast start checklist

1. Read this file, `docs/dev/dependency-rules.md`, and `docs/dev/business-rules.md`.
2. Open only the touched layer README under `src/silicato/<layer>/README.md`.
3. Implement in the lowest valid layer.
4. Add or update tests in the expected test category.

Checks reference:
- `docs/dev/repo-checks.md`
