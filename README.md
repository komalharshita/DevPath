<div align="center">

<br/>

```
 ____            ____       _   _
|  _ \  _____  _|  _ \ __ _| |_| |__
| | | |/ _ \ \/ / |_) / _` | __| '_ \
| |_| |  __/>  <|  __/ (_| | |_| | | |
|____/ \___/_/\_\_|   \__,_|\__|_| |_|
```

**Skill to Project Recommender**

*Find your next coding project in under 30 seconds.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.8%2B-2335c2?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-2335c2?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-fbbf24?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-27%20passing-22c55e?style=flat-square&logo=checkmarx&logoColor=white)](#testing)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-7c3aed?style=flat-square&logo=git&logoColor=white)](CONTRIBUTING.md)
[![GSSoC](https://img.shields.io/badge/GSSoC-2026-fbbf24?style=flat-square&logo=opensourceinitiative&logoColor=0f1560)](https://gssoc.girlscript.tech/)

<br/>


[![Open Issues](https://img.shields.io/github/issues/komalharshita/devpath?color=2335c2&style=flat-square&logo=github)](https://github.com/komalharshita/devpath/issues)
[![Forks](https://img.shields.io/github/forks/komalharshita/devpath?color=7c3aed&style=flat-square&logo=github)](https://github.com/komalharshita/devpath/network/members)
[![Stars](https://img.shields.io/github/stars/komalharshita/devpath?color=fbbf24&style=flat-square&logo=github)](https://github.com/komalharshita/devpath/stargazers)
[![Contributors](https://img.shields.io/github/contributors/komalharshita/devpath?color=22c55e&style=flat-square&logo=github)](https://github.com/komalharshita/devpath/graphs/contributors)

[Get Started](#quick-start) &nbsp;&bull;&nbsp;
[How It Works](#how-it-works) &nbsp;&bull;&nbsp;
[Contribute](#contributing) &nbsp;&bull;&nbsp;
[Docs](docs/) &nbsp;&bull;&nbsp;
[Issues](https://github.com/komalharshita/devpath/issues)

<br/>

---

</div>

## Overview

DevPath is a beginner-friendly, open-source Flask application that solves
a real problem: **knowing what to build**.

Enter what you know. Choose your level and interests. DevPath runs a
rule-based scoring engine against a curated project dataset and returns
the top three matches — each with a full step-by-step roadmap and a
starter code template you can download and run immediately.

No database. No machine learning. No account required.
Clean Python, readable code, and 27 passing tests.

---

## Quick Start

### Standard Setup

```bash
git clone https://github.com/komalharshita/devpath.git
cd devpath
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Using Docker (Recommended)

**Prerequisites**: You must have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine.

To start the project using Docker without installing Python locally:

```bash
git clone https://github.com/komalharshita/devpath.git
cd devpath
docker-compose up --build
```

**http://127.0.0.1:5000** — that is the entire setup.

```bash
# Verify everything works (Standard setup)
python tests/test_basic.py
# 27 passed, 0 failed out of 27 tests
```

---

## How It Works

```
User inputs                 Scoring engine              Output
-----------                 --------------              ------
Skills (Python, HTML)  -->  +3 per skill match   -->   Top 3 projects
Level (Beginner)       -->  +2 if level matches         with:
Interest (Data)        -->  +2 if interest matches       - Roadmap
Time (Low)             -->  +1 if time matches           - Resources
                                                          - Starter code
```

The algorithm lives entirely in `utils/recommender.py`. Weights are named
constants at the top of the file — easy to tune without reading the whole module.

---

## Structure

```
devpath/
├── app.py                   Entry point (30 lines)
├── routes/main_routes.py    5 HTTP routes as a Blueprint
├── utils/
│   ├── data_loader.py       Reads projects.json
│   ├── recommender.py       Scores + filters projects
│   └── file_server.py       Serves starter code safely
├── data/projects.json       Project dataset (extend this)
├── templates/               Jinja2 HTML
├── static/                  CSS + vanilla JS
├── starter_code/            7 starter templates
├── tests/test_basic.py      27 tests
└── docs/                    Architecture + contribution guides
```

---

## Routes

| Method | Path | Returns |
|--------|------|---------|
| GET | `/` | Homepage with skill form |
| POST | `/api/recommend` | JSON — top 3 matched projects |
| GET | `/project/<id>` | HTML — full project detail page |
| GET | `/project/<id>/code` | JSON — starter code content |
| GET | `/project/<id>/download` | File — starter code download |

---

## Extending the Dataset

The dataset is a plain JSON file. Add a new project by appending to
`data/projects.json`:

```json
{
  "id": 8,
  "title": "Todo CLI App",
  "skills": ["Python"],
  "level": "Beginner",
  "interest": "Automation",
  "time": "Low",
  "description": "A command-line task manager that saves to JSON.",
  "features": ["Add/remove tasks", "Mark complete", "Filter by status"],
  "tech_stack": ["Python", "json module"],
  "roadmap": ["Step 1: Define data structure", "Step 2: Write add_task()"],
  "resources": ["Python docs: https://docs.python.org"],
  "starter_code": "starter_code/todo_cli.py"
}
```

No backend changes needed. The engine picks it up on the next request.

---

## Contributing

<div align="center">

[![Issues](https://img.shields.io/github/issues/komalharshita/devpath?color=0f1560&style=flat-square)](https://github.com/komalharshita/devpath/issues)
[![Good first issues](https://img.shields.io/github/issues/komalharshita/devpath/good%20first%20issue?color=22c55e&style=flat-square&label=good+first+issues)](https://github.com/komalharshita/devpath/issues?q=label%3A%22good+first+issue%22)

</div>

This project is designed to be contributed to. The codebase is small,
modular, and thoroughly documented. If this is your first open-source
contribution, this is a good place to start.

**Step-by-step process:**

```
1. Browse issues          github.com/komalharshita/devpath/issues
2. Comment to claim       Leave a comment before starting
3. Fork the repo          Fork button on GitHub
4. Create a branch        git checkout -b feat/your-change
5. Make the change        Follow the code style in CONTRIBUTING.md
6. Run tests              python tests/test_basic.py
7. Push and open a PR     Use the template in CONTRIBUTING.md
```

**Branch naming:**

```
feat/description          New feature
fix/description           Bug fix
docs/description          Documentation only
data/description          New projects in the dataset
style/description         CSS or visual changes
test/description          Test additions or fixes
```

---

## Open Issues


**Beginner**
- Fix form label spacing on mobile screens
- Improve submit button hover state
- Add three new projects to the dataset
- Add ARIA attributes to form inputs
- Add inline comments to script.js

**Intermediate**
- Refactor scoring weights into a config dictionary
- Improve roadmap timeline visual styling
- Add live keyword filter to results section
- Fix card overflow at 360px width

**Advanced**
- Add localStorage bookmarking system
- Add session-based recently viewed projects
- Cache JSON data in memory

---

## GSSoC 2026

<div align="center">

[![GSSoC 2025](https://img.shields.io/badge/GSSoC-2026%20Participant-fbbf24?style=for-the-badge&logo=opensourceinitiative&logoColor=0f1560)](https://gssoc.girlscript.tech)

</div>

DevPath is an active GSSoC 2026 project. Contributions are mentored and
welcomed at all skill levels.

Before starting work: comment on the issue, then fork and branch. Do not
open a PR for an issue that is not assigned or claimed in the comments.

Read the full onboarding guide: [docs/contribution_guide.md](docs/contribution_guide.md)

---

## Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | This file — setup, structure, contributing |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Code style, branch naming, PR template |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |
| [docs/architecture.md](docs/architecture.md) | System design and data flow |
| [docs/contribution_guide.md](docs/contribution_guide.md) | Beginner onboarding (8 steps) |
| [docs/project_overview.md](docs/project_overview.md) | What DevPath is and why |
| [docs/github_issues.md](docs/github_issues.md) | All 12 issues with full descriptions |

---

## Code of Conduct

All contributors are expected to follow the
[Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">


<br/>

*DevPath — open source, built for learners, by learners.*

<br/>

</div>
