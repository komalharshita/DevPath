# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- Bookmarking system for resources and topics (#1217)
- localStorage bookmarks for guests, database bookmarks for authenticated users
- Popular bookmarks endpoint for trending resources
- Community discussion threads per learning path (#1218)
- Thread creation, comments, and moderation endpoints
- Search functionality for discussion threads
- Offline mode with service worker caching for recently visited paths (#1219)
- Service worker for intelligent caching and offline fallback
- Offline detection banner with connection status feedback
- Cached paths tracking for offline access
- Completion certificate generation for finished learning paths (#1220)
- PDF certificate download with jsPDF integration
- Public certificate verification system using UUID codes
- Database storage for certificate tracking and validation
- Certificate routes for generation, download, and verification
- "Share My Result" button on results page that copies a pre-filled URL to clipboard (#411)
- Auto-fill form and trigger recommendations when opening a shared URL (#411)
- Initial CHANGELOG.md setup for tracking project history
- Documentation structure for future contributor updates
- Added .flake8 config file to enforce consistent 88-character line limit for all contributors

### Changed

- Contributors are now expected to document user-facing changes in CHANGELOG.md

### Fixed

- No fixes recorded yet