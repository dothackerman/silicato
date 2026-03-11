# Agent: Silicato Worker A - Named Pane Routing

Use this prompt for the worker responsible for named pane routing.

Read first:
1. `AGENTS.md`
2. `docs/dev/patterns-quickstart.md`
3. `docs/dev/dependency-rules.md`
4. `docs/dev/business-rules.md`
5. `docs/dev/architecture.md`
6. `docs/feature-requests/2026-03-10-pane-identifier-routing-plugin.md`
7. `docs/agents/ralph-loop.md`

## Mission

Implement the named pane routing track without expanding Silicato into a generic plugin architecture.

## Write scope

Owned:
- `src/silicato/ports/storage.py`
- new route-oriented application files under `src/silicato/application/use_cases/`
- new route-oriented adapter files under `src/silicato/adapters/storage/`
- routing tests

Avoid unless Wave 0 explicitly assigns them:
- `src/silicato/ui/cli/main.py`
- `src/silicato/ui/cli/args.py`
- `README.md`
- `docs/user/*`
- `docs/dev/business-rules.toml`

## Non-negotiable constraints

1. Treat this as a core feature, not a runtime plugin.
2. Respect existing layer boundaries:
   - UI parses and wires
   - application owns route orchestration
   - ports define contracts
   - adapters persist and validate
3. Do not duplicate tmux validation logic in the CLI.
4. Do not edit auto-stop internals.
5. You are not alone in the codebase. Other workers may be active. Do not revert their work.

## Expected architecture shape

Preferred direction:
- add a dedicated route storage port
- add route CRUD / resolve / check use cases
- reuse target validation through the existing tmux targeting boundary
- keep storage TOML-backed in the Silicato config directory

Avoid:
- ad hoc JSON side stores
- pluginizing routing
- pushing route policy into `ui`

If CLI command restructuring is needed, keep changes minimal and record open issues for merger if the surface overlaps with worker B.

## Required checks before claiming completion

```bash
make test-arch
make test-rules-fast
```

Run additional focused tests for the routing work as needed.

## Completion truth

You may claim your branch ready only if:

1. route management behavior is implemented or clearly scaffolded with tests
2. architecture checks pass
3. no unresolved hidden CLI conflict is being ignored
4. open issues are documented explicitly for the merger

## Required handoff note

Use exactly this format:

```markdown
## What Changed
- ...

## Checks Run
- ...

## Open Issues
- ...

## Conflict Files
- ...
```
