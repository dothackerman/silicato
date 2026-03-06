# Changelog

All notable changes to this project are documented in this file.

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
