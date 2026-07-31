## [Unreleased]

### Added
- "Share My Result" button on results page that copies a pre-filled URL to clipboard (#411)
- Auto-fill form and trigger recommendations when opening a shared URL (#411)
- Initial CHANGELOG.md setup for tracking project history
- Documentation structure for future contributor updates
- Added .flake8 config file to enforce consistent 88-character line limit for all contributors
- Added `SKILL_SYNONYMS` dictionary to `utils/recommender.py` mapping 28 common tech abbreviations
  (e.g. `js`, `reactjs`, `ts`, `node`, `py`) to their canonical lowercase names (#1116)
- Added 5 new unit tests in `tests/test_basic.py` to verify synonym normalization end-to-end (#1116)
- DevPath Sentinel developer tool for repository health and dataset integrity validation (#1295)
- Dataset Validator to detect duplicate project IDs, duplicate project titles, missing required fields, empty required fields, and missing starter code references
- Starter Code Integrity Validator to detect orphan starter code files, empty starter code files, hidden files, and unsupported file types

### Changed

- DevPath Sentinel now executes all available validators through a unified CLI with consolidated validation reporting
- Updated Sentinel documentation to include the Starter Code Integrity Validator and multi-validator workflow
- Contributors are now expected to document user-facing changes in CHANGELOG.md
- `parse_skills()` now normalizes skill abbreviations via `SKILL_SYNONYMS` before scoring,
  so inputs like "JS, ReactJS, Node" correctly match projects tagged "JavaScript, React, Node.js" (#1116)

### Fixed

- Fixed missed skill matches when users enter common abbreviations (e.g. "JS" instead of "JavaScript"),
  which previously caused skill coverage score to drop to 0 and returned poor recommendations (#1116)
- Correct skills suggestions dropdown overlapping with available skill chips and resolve white background conflict in dark theme
