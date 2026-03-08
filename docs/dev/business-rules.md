# Business Rules

This document defines how Silicato tracks and validates behavior regressions using a rule catalog.

## Source of truth

- Catalog file: `docs/dev/business-rules.toml`
- Validation script: `scripts/business_rules.py`

`specs/*.md` remain historical plans. Current behavior coverage stays in this developer catalog.

## Rule entry format

Each `[[rule]]` entry must define:
1. `id`: stable rule identifier (for example `BR-TARGET-001`)
2. `statement`: behavior contract in plain language
3. `owner_layer`: primary architecture layer owning the rule
4. `requires_hardware`: `true` if validation requires local tmux/audio runtime
5. `tests`: one or more pytest node ids validating the rule

## Commands

```bash
make check-rules
make test-rules-fast
make test-rules
```

Behavior:
- `make check-rules`: validates catalog schema + mapped pytest node existence
- `make test-rules-fast`: runs non-hardware rule regressions
- `make test-rules`: runs full rule regressions (including hardware-tagged rules)

`make gate` runs fast rule regressions by default.

Checks reference:
- `docs/dev/repo-checks.md`

## Update policy

When behavior changes:
1. Update or add a new rule entry in `business-rules.toml`.
2. Add/update mapped regression tests.
3. Keep rule IDs stable once published.
4. Include touched rule IDs in implementation handoff notes.
