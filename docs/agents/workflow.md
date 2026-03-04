# Agent Workflow

## Branch naming

Allowed branch patterns:
- `feat/<slug>`
- `fix/<slug>`
- `docs/<slug>`
- `refactor/<slug>`
- `test/<slug>`
- `chore/<slug>`
- `main` (protected target branch)

## Commit message format

Conventional commits are mandatory:
- `feat(scope): summary`
- `fix(scope): summary`
- `docs(scope): summary`
- `refactor(scope): summary`
- `test(scope): summary`
- `chore(scope): summary`

## Knowledge gradient

Mandatory bootstrap docs for every session:
- `AGENTS.md`
- `docs/dev/patterns-quickstart.md`
- `docs/dev/dependency-rules.md`
- `docs/agents/new-session-handoff.md`

On-demand docs:
- `docs/dev/patterns-deep-dive.md`
- `docs/dev/adr/*`
- `src/dialogos/<layer>/README.md` for touched layer(s)

## Spec lifecycle

- `specs/*.md` files are historical plan records.
- Once implemented and merged, specs are immutable.
- Do not edit old specs to reflect later behavior.
- For new behavior, write a new spec and link back to the superseded plan.
- Keep current behavior in README and user/dev docs.

## Required local gate

Run architecture checks early:

```bash
make test-arch
```

Before pushing:

```bash
make gate
```

`make gate` is blocking and includes:
- architecture/dependency enforcement checks
- `make check` (format + lint + typing)
- `make test-fast` (non-hardware suite)
- `make test` (includes hardware tests)

If hardware tests fail, the gate fails.

## Workflow per feature

1. Create or update `specs/<feature>.md` before implementation.
2. Builder agent implements code + tests in owned layer(s).
3. Builder validates layer dependency rules (`make test-arch`).
4. Quality agent runs `make gate` and reviews architecture fit.
5. Docs agent updates affected docs, and updates specs only when creating a new plan.
6. Merge only after required signoffs.
