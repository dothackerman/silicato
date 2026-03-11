# Ralph Loop for Silicato

Silicato can use a Ralph-style controller loop when one feature wave benefits from parallel implementation but still needs disciplined integration.

## Why use it here

It fits the current two-track architecture work:

- named pane routing
- auto-stop detector unification

These can be developed in parallel, but only if:
- seams are frozen first
- conflict zones are reserved
- a merger step is mandatory before completion
- each worker has a hard write scope and a fixed handoff format

Otherwise parallelism just becomes merge debt with better branding.

## Ralph invariants

1. Stable objective per wave.
2. Persistent repo state across iterations.
3. Explicit completion promise.
4. Max-iterations guard.
5. No false completion.
6. Mandatory merger after parallel work.

## Silicato wave plan

### Wave 0: seam freeze

Serial wave.

Define:
- route storage and use-case seam
- shared auto-stop detector seam
- reserved conflict-zone files

Completion promise:
- `WAVE0_SEAMS_COMPLETE`

### Wave 1: parallel implementation

Parallel wave.

Workers:
- Worker A: named pane routing
- Worker B: auto-stop detector unification

Completion promise:
- `WAVE1_PARALLEL_COMPLETE`

### Wave 2: merger and integration

Serial wave.

Merger integrates both tracks, resolves shared CLI/doc/rule conflicts, and runs the full gate.

Completion promise:
- `WAVE2_INTEGRATION_COMPLETE`

## Prompt pack

Repo-local Codex prompts live here:

- `.codex/agents/silicato-ralph-loop-controller.md`
- `.codex/agents/silicato-worker-pane-routing.md`
- `.codex/agents/silicato-worker-auto-stop-unification.md`
- `.codex/agents/silicato-merger.md`
- `.codex/ralph-loop.local.example.md`

Local state file during execution:

- `.codex/ralph-loop.local.md`

This local state file is intentionally ignored by git.

## Conflict zones

Treat these as merger-owned unless Wave 0 explicitly narrows ownership:

- `src/silicato/ui/cli/main.py`
- `src/silicato/ui/cli/args.py`
- `README.md`
- `docs/user/*`
- `docs/dev/business-rules.toml`
- cross-track integration tests

## Legibility rules for prompts

To keep agent execution predictable:

1. Worker prompts should define `Write scope` explicitly.
2. Worker prompts should define a fixed `Handoff` format.
3. The controller prompt should stay procedural and point here for shared policy.
4. Merger owns shared CLI, shared docs, and cross-track rule updates unless Wave 0 reassigns them explicitly.

## Minimum quality policy

Workers:

```bash
make test-arch
make test-rules-fast
```

Merger:

```bash
make gate
```

## Recommended execution model

Best option:
- separate git worktrees or branches for worker A and worker B
- one dedicated merger branch

Weaker option:
- one orchestrator session with sub-agents and strict file ownership

The first is safer. The second is faster. Pretending they are equivalent is how repos grow fungus.
