# Agent Roles

Silicato uses a 3-role multi-agent model.

## 1) Builder Agent
- Implements feature code and tests from spec.
- Keeps module boundaries aligned with architecture docs.
- Must update or add tests for every behavior change.

## 2) Quality Agent
- Reviews maintainability, correctness, and legibility.
- Enforces formatting, linting, typing, and full gate checks.
- Confirms hardware tests remain blocking for gate signoff.
- Uses `docs/dev/repo-checks.md` as the canonical checks matrix.

## 3) Docs Agent
- Updates user-facing docs for behavior/dependency changes.
- Updates agent-facing docs for workflow/process changes.
- Updates developer docs/spec deltas after milestone scope lands.

## Merge policy
- `main` requires quality signoff.
- Docs signoff is required when behavior, dependencies, setup, or CLI options change.
