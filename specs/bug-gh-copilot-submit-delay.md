# Silicato Bug Spec - GitHub Copilot tmux Submit Timing Reliability

Status: In Progress
Created on: 2026-03-15

## Problem

In live tmux runs targeting GitHub Copilot CLI, prompt submission can intermittently fail even when text injection succeeds.  
Two observed cases:
1. Idle-pane timing misses when delay is too short.
2. Busy-pane false success: when Copilot is already thinking, injected text is appended but not submitted, yet Silicato reported success.

## Goal

Improve submit reliability for tmux-based agent CLIs (including GitHub Copilot) without changing user-facing CLI flows.

## Scope

1. Reproduce and document submit reliability under current timing.
2. Harden submit timing in `TmuxSender`.
3. Add busy-pane guard in `TmuxSender` so Silicato fails fast instead of reporting false success.
4. Add a short readiness wait when the pane is still loading environment state.
5. Keep explicit failure behavior if tmux operations fail.
6. Update regression tests and rule mappings where behavior contracts change.

## Non-Goals

1. No redesign of tmux transport architecture.
2. No change to target resolution precedence.
3. No hidden retry loops that can duplicate prompt submissions.

## Acceptance Criteria

1. `TmuxSender` applies a delay value that addresses observed idle-pane submit misses in live tmux + GitHub Copilot probing.
2. `TmuxSender` raises an explicit runtime error when the target pane is already busy (thinking/processing with enqueue hint), instead of reporting send success.
3. `TmuxSender` waits for loading panes before attempting submit and raises explicit error if loading does not finish within timeout.
4. Contract tests for sender behavior remain green and validate split send + delayed submit semantics plus busy-pane and loading-state safeguards.
5. Rule-catalog mappings remain valid for tmux sender reliability behavior.
