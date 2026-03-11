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
- `docs/dev/business-rules.md`
- `docs/agents/new-session-handoff.md`

On-demand docs:
- `docs/dev/patterns-deep-dive.md`
- `docs/dev/adr/*`
- `src/silicato/<layer>/README.md` for touched layer(s)

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
- business-rule mapping checks (`make check-rules`)
- fast business-rule regressions (`make test-rules-fast`)
- `make check` (format + lint + typing)
- `make test-fast` (non-hardware suite)
- `make test` (includes hardware tests)

If hardware tests fail, the gate fails.

For release-prep work, also run:

```bash
make test-rules
make test-e2e-tmux
```

Canonical check matrix:
- `docs/dev/repo-checks.md`

## Workflow per feature

1. Create or update `specs/<feature>.md` before implementation.
2. Builder agent implements code + tests in owned layer(s).
3. Builder validates layer dependency rules (`make test-arch`).
4. Quality agent runs `make gate` and reviews architecture fit.
5. Docs agent updates affected docs, and updates specs only when creating a new plan.
6. Merge only after required signoffs.

## Ralph Loop Option

For bounded multi-track work that benefits from parallel implementation plus mandatory integration, use the Ralph-loop prompt pack:

- [Ralph Loop Overview](ralph-loop.md)
- `.codex/agents/silicato-ralph-loop-controller.md`
- `.codex/agents/silicato-worker-pane-routing.md`
- `.codex/agents/silicato-worker-auto-stop-unification.md`
- `.codex/agents/silicato-merger.md`

Use it when:
- the objective can be split into parallel-safe tracks
- conflict zones are known up front
- a dedicated merger pass will own shared CLI/docs/rule integration

Do not use it when:
- both tracks must heavily edit the same files from the start
- no one owns the merger step
- the scope is small enough that parallelism would cost more than it saves
