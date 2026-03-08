# Patterns Deep Dive

This document explains why Milestone 2 chose each pattern and where not to apply it.

## 1. Layered hexagonal boundaries

Pattern:
- Keep business behavior in `domain` and `application`.
- Isolate side effects behind `ports` and `adapters`.

Why:
- Reduces merge conflicts across parallel agents.
- Makes behavior testable without hardware.

Tradeoffs:
- More files and explicit wiring overhead.
- Slightly higher cognitive load for small changes.

When not to use:
- Tiny script-level one-offs that are intentionally disposable.

## 2. Ports-first side-effect isolation

Pattern:
- Define capability contracts in `ports` before writing adapter code.

Why:
- Prevents adapter details leaking into orchestration logic.
- Enables contract tests across multiple implementations.

Tradeoffs:
- Overly granular ports can create noisy abstractions.

When not to use:
- If only one trivial call site exists and no behavioral abstraction is needed yet.

## 3. Domain turn state machine

Pattern:
- Model confirm actions (`send/edit/retry/skip/quit`) as explicit state transitions.

Why:
- Keeps control-flow decisions deterministic and unit-testable.
- Avoids CLI branching drift over time.

Tradeoffs:
- Requires up-front transition design.

When not to use:
- If logic is purely presentational and has no state transition semantics.

## 4. UI composition root

Pattern:
- CLI owns args/prompt rendering and dependency wiring only.

Why:
- UI changes remain isolated from business behavior.
- Makes alternate frontends possible without rewriting use-cases.

Tradeoffs:
- Extra wiring code can feel verbose.

When not to use:
- In throwaway prototypes where architecture longevity is not a goal.

## 5. Architecture checks in local gate

Pattern:
- Enforce import boundaries automatically in `make check` and `make gate` via `make test-arch`.

Why:
- Prevents boundary erosion from regressions.
- Makes review objective and faster.

Tradeoffs:
- Rule maintenance required when package layout changes.
- False positives possible if rules are too broad.

When not to use:
- Never skipped for production paths. For experiments, isolate outside protected tree.

Checks reference:
- `docs/dev/repo-checks.md`
