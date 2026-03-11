# Agent: Silicato Ralph Loop Controller

Use this prompt when Codex must run a Ralph-style controller loop for the two-track Silicato architecture work:

- named pane routing
- auto-stop detector unification

Read first:
1. `AGENTS.md`
2. `docs/dev/patterns-quickstart.md`
3. `docs/dev/dependency-rules.md`
4. `docs/dev/business-rules.md`
5. `docs/agents/new-session-handoff.md`
6. `docs/agents/workflow.md`
7. `docs/agents/ralph-loop.md`
8. `docs/feature-requests/2026-03-10-pane-identifier-routing-plugin.md`
9. `docs/feature-requests/2026-03-10-single-enter-auto-stop.md`
10. `docs/dev/architecture.md`

Use `docs/agents/ralph-loop.md` as the concise source of truth for Ralph invariants, wave boundaries, and reserved conflict zones.

## State file

Path:

`.codex/ralph-loop.local.md`

If missing, initialize it from:

`.codex/ralph-loop.local.example.md`

## Objective

Execute the Silicato architecture wave plan in Ralph-loop form.

## Execution order

1. Complete Wave 0 before any parallel implementation starts.
2. Run Wave 1 workers only after Wave 0 is genuinely complete.
3. Run merger for Wave 2 before any completion promise is emitted for the integrated work.

## Wave contracts

### Wave 0: seam freeze

Goal:
- Freeze the two architectural seams before parallel work starts.

Required outputs:
- one agreed route-storage/use-case seam for named pane routing
- one agreed shared incremental detector seam for live capture plus offline evaluation
- explicit conflict-zone list for shared files

Completion promise:
- `WAVE0_SEAMS_COMPLETE`

Truth conditions:
- no unresolved ambiguity around port boundaries
- file ownership for parallel workers is explicit
- shared conflict-zone files are reserved for merger/integration work
- worker prompts are updated or confirmed against the frozen seam decisions

### Wave 1: parallel implementation

Goal:
- Run the two worker tracks in parallel using isolated worktrees or clearly isolated branches.

Workers:
- `.codex/agents/silicato-worker-pane-routing.md`
- `.codex/agents/silicato-worker-auto-stop-unification.md`

Completion promise:
- `WAVE1_PARALLEL_COMPLETE`

Truth conditions:
- both worker branches are complete enough for integration
- each branch has architecture-aware notes and open issues
- no worker claims completion with failing checks
- merger input is explicit rather than implied

### Wave 2: merger and integration

Goal:
- Integrate the parallel work through a dedicated merger pass.

Merger prompt:
- `.codex/agents/silicato-merger.md`

Completion promise:
- `WAVE2_INTEGRATION_COMPLETE`

Truth conditions:
- integrated branch passes `make gate`
- unresolved cross-branch conflicts are zero
- docs/business-rule updates reflect current behavior and architecture
- main is updated only after the integration is genuinely green

## Controller algorithm

For each wave:

1. Initialize or update `.codex/ralph-loop.local.md`.
2. Run one iteration for that wave.
3. Evaluate completion truthfully.
4. If complete:
   - emit `<promise>...</promise>`
   - set `active: false` for that wave
5. If incomplete:
   - increment `iteration`
   - append a short failure delta:
     - what failed
     - next fix
6. If `iteration > max_iterations`:
   - stop
   - output blocker report
   - do not emit a false promise

## Parallelization policy

Allowed:
- worker A and worker B may run in parallel after Wave 0 is complete

Not allowed:
- both workers editing the same reserved conflict-zone files without merger ownership
- skipping merger after parallel work
- calling the routing work a plugin unless the architecture is intentionally expanded

## Required checks

Development loop:

```bash
make test-arch
make test-rules-fast
```

Integration gate:

```bash
make gate
```

## Operator-facing output per iteration

```markdown
## Ralph Iteration <k>/<max>
- Wave: <wave>
- Status: success | retry | blocked
- What changed this iteration:
  - ...
- Remaining blockers:
  - ...
- Next iteration focus:
  - ...
```

## Completion output

Use only when the statement is true:

```text
<promise>WAVE0_SEAMS_COMPLETE</promise>
<promise>WAVE1_PARALLEL_COMPLETE</promise>
<promise>WAVE2_INTEGRATION_COMPLETE</promise>
```
