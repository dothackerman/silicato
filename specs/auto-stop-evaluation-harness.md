# Silicato Spec - Auto-Stop Evaluation Harness

Status: Proposed
Created on: 2026-03-09

## Problem

Silicato's auto-stop behavior is currently tuned by live trial and error.
That makes it difficult to:

1. converge on a stable default for slow and reflective speech
2. compare candidate endpointing configurations objectively
3. detect UX regressions when auto-stop logic changes later

## Goal

Create a deterministic evaluation harness for auto-stop behavior based on prerecorded WAV fixtures and annotated stop expectations.

## Scope

1. Extract endpoint detection into a pure component that can evaluate prerecorded audio.
2. Add a fixture manifest format for WAV files, scripts, tags, and expected stop windows.
3. Support scoring one endpoint configuration against a fixture set.
4. Provide starter tests and fixture metadata so real recordings can be added without changing the harness shape.

## Non-goals

1. No live microphone calibration workflow yet.
2. No automatic parameter search CLI yet.
3. No change to runtime capture UX in this slice.
4. No transcript-quality benchmarking beyond optional fixture metadata.

## Acceptance Criteria

1. Endpoint detection can run deterministically on WAV data without ALSA or tmux.
2. Fixture metadata can express:
   - id
   - wav path
   - script
   - target stop timestamp
   - acceptable stop window
   - tags
   - optional expected transcript
3. Tests cover:
   - early-stop detection
   - in-window success
   - late-stop detection
   - manifest parsing
4. The harness is structured so real recordings can be dropped into a fixtures directory and evaluated without changing production runtime wiring.
