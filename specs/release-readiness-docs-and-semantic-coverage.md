# Silicato Release Readiness - Docs and Semantic Coverage Tightening

Status: Active
Created on: 2026-03-08

## Problem

Release-candidate behavior is mostly stable, but we still have coherence risk in three places:
1. CLI helper text does not fully communicate key runtime semantics.
2. Some high-signal semantics are not directly tested (prompt helpers and help text expectations).
3. User-facing docs can be tighter about target-resolution edge behavior during `--reuse-target`.

## Goal

Improve release confidence by aligning docs, CLI helper text, and semantic tests without changing runtime behavior.

## Scope

1. Tighten CLI `--help` text for target mode and preview action clarity.
2. Add semantic tests for:
   - target-resolution edge handling in reuse mode
   - CLI help text guarantees
   - prompt helper behavior
3. Tighten user/developer docs where ambiguity exists.
4. Re-run release-relevant local quality checks.

## Non-goals

1. No product-feature changes.
2. No behavior changes to capture/transcribe/send flow.
3. No release-channel publishing from this spec.

## Acceptance Criteria

1. CLI help text explicitly describes default picker behavior and preview actions.
2. Tests fail if helper text or prompt semantics drift.
3. Target resolution semantics are tested for invalid env target handling.
4. Docs and CLI semantics are coherent and non-contradictory.
5. `make gate` and `make test-rules` pass after changes.
