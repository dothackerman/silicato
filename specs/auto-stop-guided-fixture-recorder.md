# Silicato Spec - Auto-Stop Guided Fixture Recorder

Status: Proposed
Created on: 2026-03-10

## Problem

The auto-stop evaluation harness is only useful if collecting real fixture data is low-friction.
Manual recording, naming, transcription checks, and manifest editing would slow iteration enough that the fixture set would likely stay incomplete.

## Goal

Provide a guided recorder tool that walks an operator through a structured DE/EN prompt set, records WAV files automatically into the fixture directory, transcribes each clip, and updates the fixture manifest with inferred stop windows.

## Scope

1. Load a recording plan containing prompt text, language, tags, and scenario instructions.
2. Guide the operator through each prompt interactively.
3. Record and save WAV files with deterministic fixture IDs.
4. Transcribe each recording with word timestamps and confidence metadata.
5. Save transcription diagnostics and append/update fixture manifest entries automatically.
6. Support repeated takes so one plan can yield a larger dataset.

## Non-goals

1. No playback UI.
2. No automatic acceptance/rejection based purely on confidence.
3. No runtime integration into the end-user `silicato` command.

## Acceptance Criteria

1. The operator can run one command and be prompted through the whole recording session.
2. The tool creates:
   - WAV files
   - transcription diagnostics
   - fixture manifest entries
3. Manifest entries include inferred target/min/max stop timestamps derived from the final speech timestamp plus configurable post-speech offsets.
4. The tool can generate multiple takes per prompt without manual renaming.
