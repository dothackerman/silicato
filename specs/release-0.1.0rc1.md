# Dialogos 0.1.0rc1 Release Candidate Handoff

## Summary
This spec captures the release-handoff scope for `0.1.0rc1` as of 2026-03-04.
It is release-preparation work only: documentation, packaging metadata, and validation gates.

No new product features are introduced.

## Relationship to prior specs
- Preserves runtime behavior from `specs/mvp-push-to-talk.md`
- Uses architecture and gate rules from `specs/milestone-2-architecture.md`
- Assumes hardening baseline from `specs/milestone-3-agent-first-hardening.md`

## Locked release scope
1. Push-to-talk transcription flow.
2. Optional preview mode (`--preview`) for `send/edit/retry/skip/quit`.
3. Existing tmux target resolution, config persistence, JSONL logging, and doctor diagnostics.

## Support policy for RC1
1. Officially supported:
   - TUXEDO OS 24.04 LTS (Ubuntu noble base)
2. Best effort:
   - Ubuntu 24.04-compatible Linux environments

## Non-goals
1. Always-on mode.
2. TTS or spoken replies.
3. Non-Linux platform support.
4. Runtime behavior redesign.

## Implementation scope
1. Professionalize OSS-facing repository documentation:
   - root README scope/support/install sections
   - aligned user docs
   - clear Known Issues and actionable diagnostics guidance
2. Add/refresh community docs:
   - `CHANGELOG.md`
   - `CONTRIBUTING.md`
   - `SECURITY.md`
   - GitHub issue templates (bug + feature request)
3. Harden packaging metadata and release artifact flow for `0.1.0rc1`.
4. Run required validation commands:
   - `make check`
   - `make test-rules-fast`
   - `make gate`
   - `make test-rules`
5. Run TestPyPI RC simulation and pipx install path validation when credentials are present.

## Acceptance criteria
1. Project docs consistently state release scope and support policy.
2. Known Issues are transparent and include reproducibility details.
3. Package metadata is public-release ready and versioned `0.1.0rc1`.
4. Build artifacts pass `python3 -m build` and `python3 -m twine check dist/*`.
5. All required quality commands complete successfully on the local environment.
6. TestPyPI upload and pipx validation are executed or explicitly blocked by missing credentials.
7. Process stops before real PyPI upload pending explicit user go/no-go after manual UX signoff.
