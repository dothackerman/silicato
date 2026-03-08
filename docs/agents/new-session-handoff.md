# New Session Handoff

## Read first (bootstrap pack)
1. `AGENTS.md`
2. `docs/dev/patterns-quickstart.md`
3. `docs/dev/dependency-rules.md`
4. `docs/dev/business-rules.md`
5. `docs/agents/new-session-handoff.md` (this file)
6. `docs/agents/workflow.md`

## Read on-demand (task-dependent)
1. `docs/dev/patterns-deep-dive.md`
2. `docs/dev/adr/README.md` and related ADR file(s)
3. `src/silicato/<layer>/README.md` for touched layer(s)
4. `specs/milestone-2-architecture.md` for migration context

## Execution rule
- Implement exactly approved scope from the active spec.
- Preserve MVP runtime behavior unless the spec explicitly changes behavior.
- Run `make test-arch`, `make test-rules-fast`, and `make gate` before final push.
- For release-prep tasks, also run `make test-rules` and `make test-e2e-tmux`.
- Use `docs/dev/repo-checks.md` as the canonical checks matrix.

Kickoff prompt for a new Codex session:

```text
Read AGENTS.md, docs/dev/patterns-quickstart.md, docs/dev/dependency-rules.md, and docs/dev/business-rules.md first. Then execute the assigned scope and keep layer boundaries strict.
```
