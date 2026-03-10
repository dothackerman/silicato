# Changelog

All notable changes to this project are documented in this file.

## [0.1.0rc5] - 2026-03-10

### Added
- Guided local auto-stop tuning workflow with a structured bilingual fixture recorder and deterministic evaluator.
- Replayable auto-stop fixture harness and regression coverage for endpoint behavior outside live ALSA capture.
- User-facing auto-stop tuning guidance for quickly adjusting pause length and RMS sensitivity per microphone and room setup.

### Changed
- Tuned the default auto-stop behavior to `1.4` seconds of silence with RMS threshold `80` based on local fixture collection and live validation.
- CLI now exposes `--silence-rms-threshold` so speech sensitivity can be tuned directly.
- User and developer documentation synchronized around the new auto-stop defaults and local tuning workflow.
- Bumped package version to `0.1.0rc5`.

## [0.1.0rc4] - 2026-03-08

### Added
- Runtime profile plugin architecture in the CLI layer with dynamic discovery via Python entry points group `silicato.runtime_profiles`.
- Built-in `spawn` runtime plugin implementation separated from core CLI runtime flow.
- Dynamic CLI helper text that lists currently discovered runtime plugins at execution time.
- New rule-catalog coverage for runtime plugin resolution semantics.

### Changed
- `--profile` now accepts plugin names dynamically instead of a fixed choice list.
- Core CLI runtime now resolves profile behavior through plugin boundaries (no spawn-specific tuning logic in core flow).
- Documentation synchronized for plugin-based runtime tuning and release candidate `0.1.0rc4`.
- Bumped package version to `0.1.0rc4`.

## [0.1.0rc3] - 2026-03-06

### Added
- Dedicated tmux runtime boundary adapter and contract tests for centralized tmux command construction.
- Dedicated `make test-e2e-tmux` command for tmux hardware smoke checks.
- New short CLI aliases for frequent options (`-m/-d/-c/-l/-r/-i/-t/-R/-n/-p/-f/-o/-D`).

### Changed
- Default target selection now opens the interactive tmux picker at startup unless an explicit target is provided.
- Added explicit `--reuse-target` mode to restore env/config fallback target behavior.
- Normal mode no longer prints transcript text locally; preview mode keeps transcript visibility.
- User and developer docs aligned to new target-selection defaults and CLI aliases.
- Bumped package version to `0.1.0rc3`.

## [0.1.0rc2] - 2026-03-06

### Changed
- Bumped package version to `0.1.0rc2`.
- README install guidance now uses canonical PyPI install instructions (`pipx install silicato==0.1.0rc2`) so PyPI project page instructions are production-safe.
- User quickstart install guidance aligned to PyPI RC install; TestPyPI workflow kept in maintainer release docs.
- RC-facing docs and issue template examples updated from `0.1.0rc1` to `0.1.0rc2`.

## [0.1.0rc1] - 2026-03-04

### Added
- RC release handoff docs for open-source readiness.
- Community docs: `CONTRIBUTING.md`, `SECURITY.md`, and GitHub issue templates.
- Release candidate install guidance for TestPyPI + pipx validation flow.

### Changed
- Public-facing README and user docs aligned to locked RC scope:
  - push-to-talk + optional preview
  - tmux + terminal agent CLI requirement
  - official support target: TUXEDO OS 24.04 LTS
  - Ubuntu 24.04-compatible best-effort support
- Packaging metadata hardened for public release and versioned to `0.1.0rc1`.
- Release pipeline documentation updated for build, twine check, TestPyPI upload, and pipx install simulation.

### Fixed
- Repository transparency around known submit-timing behavior in tmux agent panes, including actionable bug-report data requirements.
