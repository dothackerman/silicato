# Dependency Rules

These rules define legal imports for Milestone 2 architecture.

## Allowed import matrix

`Y` means allowed; `N` means forbidden.

| Importer \ Imported | domain | application | ports | adapters | ui |
| --- | --- | --- | --- | --- | --- |
| domain | Y | N | N | N | N |
| application | Y | Y | Y | N | N |
| ports | N | N | Y | N | N |
| adapters | N | N | Y | Y | N |
| ui | N | Y | Y | Y | Y |

Notes:
- `ui -> domain` is forbidden; use application use-cases instead.
- `ports` must remain interface-only and dependency-light.

## Forbidden examples

```python
# forbidden: application importing concrete adapter
from silicato.adapters.tmux.sender import TmuxSender
```

```python
# forbidden: domain depending on side-effect boundary
from silicato.ports.sender import Sender
```

```python
# forbidden: adapter calling application orchestration
from silicato.application.use_cases.send_turn import send_turn
```

## Required architecture checks

Run during development:

```bash
make test-arch
make test-rules-fast
```

Run before push:

```bash
make gate
```

Architecture violations are blocking.

Checks reference:
- `docs/dev/repo-checks.md`

## Review checklist

1. Is the change in the correct layer for its responsibility?
2. Are imports legal per the matrix?
3. Is business decision logic outside adapters/UI prompt code?
4. Are side effects behind ports?
5. Are tests in the correct category (unit/contracts/integration/hardware)?
