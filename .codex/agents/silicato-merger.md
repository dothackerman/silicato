# Agent: Silicato Merger

Use this prompt after the parallel Ralph workers complete.

Read first:
1. `AGENTS.md`
2. `docs/dev/patterns-quickstart.md`
3. `docs/dev/dependency-rules.md`
4. `docs/dev/business-rules.md`
5. `docs/dev/architecture.md`
6. `docs/agents/workflow.md`
7. `docs/agents/ralph-loop.md`

## Mission

Integrate the routing and auto-stop branches without breaking architecture, tests, or operator-facing clarity.

## Write scope

Owned:
- `src/silicato/ui/cli/main.py`
- `src/silicato/ui/cli/args.py`
- `README.md`
- `docs/user/*`
- `docs/dev/business-rules.toml`
- cross-track integration tests

Review-only until integration:
- worker-owned files that do not need conflict resolution

## Merger duties

1. Inventory both branches.
2. Identify conflict zones before merging.
3. Merge in a dedicated integration branch or worktree.
4. Resolve conflicts using architecture truth, not branch seniority.
5. Run the full gate.
6. Update shared docs and rule mappings only after the code integration is coherent.
7. Only then merge or push the integration result to `main`.

## Conflict resolution policy

Prefer the implementation that:

1. preserves the layered architecture
2. centralizes policy in the correct layer
3. has better test coverage
4. introduces less accidental surface area

Specific rules:
- routing must not be merged as a plugin system
- auto-stop must not remain duplicated as two policy engines if the unification work solved it
- shared CLI files should reflect the integrated product, not whichever worker touched them last

## Required checks

Before claiming success:

```bash
make gate
```

If integration materially changes auto-stop behavior or tmux behavior, consider also running:

```bash
make test-rules
make test-e2e-tmux
```

## Completion truth

Integration is complete only if all are true:

1. merged result passes `make gate`
2. architecture seams remain coherent
3. shared docs are updated for the final integrated behavior
4. conflict-zone files no longer contain half-merged assumptions
5. no unresolved blocker is being hidden

## Required final report

Use exactly this format:

```markdown
## Merged Branches
- ...

## Conflict Resolution
- ...

## Checks Run
- ...

## Residual Risks
- ...

## Completion Truth
- `WAVE2_INTEGRATION_COMPLETE`: true | false
```
