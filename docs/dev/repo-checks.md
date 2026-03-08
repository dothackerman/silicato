# Repository Checks

This file is the canonical checklist for local quality and release validation commands.

## Command tiers

### 1) Development loop (fast feedback)

Run while implementing:

```bash
make test-arch
make test-rules-fast
```

Purpose:
- Catch architecture/import violations early.
- Catch non-hardware business-rule regressions quickly.

### 2) Pre-push / pre-merge (blocking)

Run before pushing:

```bash
make gate
```

`make gate` includes:
- `make check` (format + lint + typecheck + architecture + rule mapping)
- `make test-rules-fast`
- `make test-fast`
- `make test` (includes hardware-tagged tests when present)

### 3) Release-readiness validation

Run before RC/prod publish:

```bash
make gate
make test-rules
make test-e2e-tmux
```

Purpose:
- Re-validate full business-rule mappings and regressions.
- Run dedicated tmux hardware smoke checks.

## Release dispatch preflight

Use:

```bash
make release-test VERSION=<version>
make release-prod VERSION=<version>
```

These commands additionally enforce:
1. clean git worktree
2. `pyproject.toml` version match
3. GitHub CLI authentication
4. local gate run (unless `SKIP_GATE=1`)
5. workflow dispatch + completion monitoring
