# Dialogos Agent Playbook

This file defines how agents collaborate in this repository.

## Roles
- Builder: implements code and tests from specs.
- Quality: validates maintainability, architecture boundaries, and gate checks.
- Docs: updates user-facing, agent-facing, and developer-only documentation.

## Knowledge gradient
Mandatory bootstrap pack for every new session:
1. `AGENTS.md`
2. `docs/dev/patterns-quickstart.md`
3. `docs/dev/dependency-rules.md`
4. `docs/agents/new-session-handoff.md`

On-demand pack (read only when needed for the task):
- `docs/dev/patterns-deep-dive.md`
- `docs/dev/adr/*`
- `src/dialogos/<layer>/README.md` for touched layer(s)
- `specs/milestone-2-architecture.md` for migration details

Session-lead rule:
- Do not require deep-dive docs when bootstrap plus touched layer README is sufficient.

## Spec lifecycle policy
- Files in `specs/` are plan snapshots, not living requirement docs.
- After a spec is implemented and merged, treat it as immutable history.
- Do not rewrite implemented specs to match later behavior.
- For behavior changes, create a new spec and reference superseded specs.
- Current behavior must be documented in README and user/dev docs, not retrofitted into old specs.

## Required flow
1. Start from `specs/<feature>.md` (create/update first).
2. Implement inside layer boundaries (`ui -> application -> domain`, application via ports).
3. Use `make test-arch` for fast boundary validation while developing.
4. Run `make gate` before push (blocking).
5. Quality reviews architecture fit and gate evidence.
6. Docs updates all impacted docs.
7. Merge only with quality signoff.

## Branch rules
- `feat/<slug>`
- `fix/<slug>`
- `docs/<slug>`
- `refactor/<slug>`
- `test/<slug>`
- `chore/<slug>`

## Commit rules
Use Conventional Commits only:
- `feat(scope): ...`
- `fix(scope): ...`
- `docs(scope): ...`
- `refactor(scope): ...`
- `test(scope): ...`
- `chore(scope): ...`

## Commands
- Install runtime deps: `make install`
- Install dev deps: `make install-dev`
- Install hooks: `make hooks`
- Architecture checks: `make test-arch`
- Quality checks: `make check`
- Fast tests (no hardware): `make test-fast`
- Full gate (blocking): `make gate`
