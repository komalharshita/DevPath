# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- Authentication-based progress tracking — sign in / sign up, with progress, badges, and saved projects synced to a SQLite-backed account instead of the browser only
- Slide-in account dashboard showing points, activity stats, badges, and saved projects
- Saving projects and earning badges now requires being signed in
- "Share My Result" button on results page that copies a pre-filled URL to clipboard (#411)
- Auto-fill form and trigger recommendations when opening a shared URL (#411)
- Initial CHANGELOG.md setup for tracking project history
- Documentation structure for future contributor updates
- Added .flake8 config file to enforce consistent 88-character line limit for all contributors

### Changed

- Contributors are now expected to document user-facing changes in CHANGELOG.md
- Progress tracking moved from localStorage-only to server-backed, scoped per signed-in account

### Fixed

- Manual test runner (`python tests/test_basic.py`) failing on `test_score_coverage_ratio_exact_values` because it could not supply the `monkeypatch` fixture outside of pytest
