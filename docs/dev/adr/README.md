# ADR Guide

Architecture Decision Records (ADRs) capture stable technical decisions and their rationale.

## Naming format

Use:
- `ADR-0001-short-kebab-case-title.md`
- Four-digit, zero-padded sequence number
- Immutable number once published

## Required ADR structure

Each ADR must include:
1. Status
2. Date
3. Context
4. Decision
5. Consequences
6. Alternatives considered

## Lifecycle

- `Proposed`: under discussion
- `Accepted`: active decision
- `Superseded`: replaced by another ADR (include pointer)
- `Deprecated`: no longer recommended but not fully replaced

When a decision changes:
- Do not rewrite history in-place.
- Add a new ADR and mark the old one superseded.

## Current ADR index

1. [ADR-0001 Layered Hexagonal Boundaries](ADR-0001-layered-hexagonal-boundaries.md)
2. [ADR-0002 Turn State Machine](ADR-0002-turn-state-machine.md)
3. [ADR-0003 Knowledge Gradient and Onboarding](ADR-0003-knowledge-gradient-and-onboarding.md)
4. [ADR-0004 Architecture Enforcement in Gate](ADR-0004-architecture-enforcement-in-gate.md)
5. [ADR-0005 Bounded Recording and Fallback Policy](ADR-0005-bounded-recording-and-fallback-policy.md)
6. [ADR-0006 Max Recording Default Disabled](ADR-0006-max-recording-default-disabled.md)
