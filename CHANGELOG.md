# Changelog

All notable changes to this project are documented in this file.

## [0.1.0rc1] - 2026-03-04

### Added
- RC release handoff docs for open-source readiness.
- Community docs: `CONTRIBUTING.md`, `SECURITY.md`, and GitHub issue templates.
- Release candidate install guidance for TestPyPI + pipx validation flow.

### Changed
- Public-facing README and user docs aligned to locked RC scope:
  - push-to-talk + optional preview
  - tmux + Codex CLI requirement
  - official support target: TUXEDO OS 24.04 LTS
  - Ubuntu 24.04-compatible best-effort support
- Packaging metadata hardened for public release and versioned to `0.1.0rc1`.
- Release pipeline documentation updated for build, twine check, TestPyPI upload, and pipx install simulation.

### Fixed
- Repository transparency around known submit-timing behavior in Codex tmux panes, including actionable bug-report data requirements.
