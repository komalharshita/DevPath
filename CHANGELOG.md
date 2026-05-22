# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project does not currently follow Semantic Versioning — version numbers
reflect development milestones.

---

## [Unreleased]

### Added

- `CHANGELOG.md` to track project version history (this file)
- `GET /health` endpoint returning server status and app version
- `get_project_stats()` in `utils/data_loader.py` — exposes total projects,
  unique skills count, and beginner-friendly project count to the homepage
- In-memory project cache with `clear_cache()` in `utils/data_loader.py` to
  eliminate repeated disk reads on every recommendation request
- `scripts/benchmark_cache.py` — performance benchmark comparing cached vs
  uncached JSON reads
- Skill aliases in `utils/recommender.py` (`js → javascript`, `py → python`,
  `html5 → html`, `css3 → css`, `c++ → cpp`) to normalise user input before scoring
- `Password Strength Checker` project entry (id 8) covering Cybersecurity interest
- `Feedback Survey Form` project entry (id 9) with HTML-only starter template
  including a multi-field form with dropdown and textarea
- `API ETL Pipeline` project entry (id 10) covering pandas/requests data
  engineering workflow with 10-step roadmap
- `survey_form/` starter code directory with `index.html` and `style.css`
- Custom 405 Method Not Allowed error page and handler in `app.py`
- GitHub Actions workflows: CI (`ci.yml`), deploy (`deploy.yml`),
  auto-labelling for issues and PRs, and contributor greetings
- Issue templates for bug reports, feature requests, data contributions,
  documentation, and good-first-issues
- `SECURITY.md` documenting the project's security policy
- `PULL_REQUEST_TEMPLATE.md` to standardise PR descriptions

### Changed

- Contributors are now expected to update `CHANGELOG.md` for every
  user-facing or documentation change (documented in `CONTRIBUTING.md`)

---

## [0.2.0] - YYYY-XX-XX

### Added

- `validate_recommendation_inputs()` in `utils/recommender.py` — returns a
  list of error strings for any missing form field; the API returns the first
  error with HTTP 400
- `find_project_by_id()` in `utils/data_loader.py` for direct project lookup
  by integer ID
- `GET /project/<id>/code` route — returns starter code filename and content
  as JSON for inline display in the browser
- `GET /project/<id>/download` route — serves the starter code file as a
  downloadable attachment using `send_from_directory`
- `utils/file_server.py` module encapsulating all starter code file resolution
  and serving logic; uses `os.path.basename()` to prevent path traversal from
  untrusted `starter_code` values in the dataset
- `starter_code/` directory with 7 starter templates:
  `expense_tracker.py`, `weather_dashboard.html`, `grade_manager.py`,
  `task_api.py`, `portfolio.html`, `url_shortener.py`, `data_report.py`
- `templates/project.html` — full project detail page rendering roadmap steps,
  resources, tech stack, and inline code viewer
- `templates/404.html`, `templates/500.html` — custom error pages with
  "Back to Home" navigation
- `static/data/skills.js` — client-side skill chip autocomplete data
- `docs/architecture.md` — detailed module responsibilities and data flow diagrams
- `docs/contribution_guide.md` — 8-step beginner onboarding guide
- `docs/github_issues.md` — descriptions of all 12 tracked issues
- `docs/project_overview.md` — project purpose and goals
- `CONTRIBUTING.md` — code style rules, branch naming, commit format, and PR guide
- `CODE_OF_CONDUCT.md` — Contributor Covenant community standards
- 27-test suite in `tests/test_basic.py` covering data loading, scoring,
  input validation, and all HTTP routes

### Changed

- Routes extracted from `app.py` into `routes/main_routes.py` as a Flask
  Blueprint, keeping `app.py` to ~30 lines

---

## [0.1.0] - YYYY-XX-XX

### Added

- Initial Flask application (`app.py`) with development server entry point
- `GET /` homepage route rendering a skill input form via Jinja2
- `POST /api/recommend` route accepting skills, level, interest, and time
  availability; returns top 3 matched projects as JSON
- `GET /project/<id>` route rendering a full project detail page
- Rule-based scoring engine in `utils/recommender.py`:
  - `parse_skills()` — splits and lowercases comma-separated skill input
  - `score_single_project()` — awards +3 per skill match, +2 for level,
    +2 for interest, +1 for time availability
  - `get_recommendations()` — filters zero-score projects, sorts descending,
    returns top 3
- `utils/data_loader.py` with `load_all_projects()` reading `data/projects.json`
- `data/projects.json` dataset with 7 initial projects:
  1. Personal Expense Tracker (Python, Beginner, Data)
  2. Weather Dashboard (JavaScript/HTML/CSS, Beginner, Web)
  3. Student Grade Manager (Python, Beginner, Education)
  4. Task Manager REST API (Python, Intermediate, Web)
  5. Portfolio Website (HTML/CSS/JS, Beginner, Web)
  6. URL Shortener (Python + full-stack, Intermediate, Web)
  7. Data Analysis Report Generator (Python/pandas, Intermediate, Data)
- Each project includes: description, features list, tech stack, step-by-step
  roadmap (5–10 steps), curated learning resources, and a starter code reference
- `templates/index.html` — homepage with skill form, interest dropdown,
  level selector, and time availability selector
- `static/style.css` — CSS custom properties design system and responsive layout
- `static/script.js` — form submission, skill chip management, results rendering,
  and code panel interactivity
- `static/favicon.svg`
- `requirements.txt` with Flask 3.0.3 and pytest 8.2.2
- `.gitignore` for Python and virtual environment artefacts
- `LICENSE` (MIT)
- `README.md` with setup instructions, architecture overview, route table,
  dataset extension guide, and contribution workflow

[Unreleased]: https://github.com/komalharshita/devpath/compare/main...HEAD
[0.2.0]: https://github.com/komalharshita/devpath/commits/main
[0.1.0]: https://github.com/komalharshita/devpath/commits/main
