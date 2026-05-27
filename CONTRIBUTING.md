# Contributing to DevPath

Thank you for your interest in contributing to DevPath. This document is your
complete guide to getting set up, following our code standards, submitting
pull requests, and picking your first issue.

DevPath is built to be contributor-friendly at all experience levels. If this
is your first open-source contribution, you are in the right place.

---

## Table of Contents

1. [Before You Start](#before-you-start)
2. [Project Structure Overview](#project-structure-overview)
3. [Development Setup](#development-setup)
4. [Branch Naming Convention](#branch-naming-convention)
5. [Code Style Rules](#code-style-rules)
6. [Commit Message Format](#commit-message-format)
7. [Running the Tests](#running-the-tests)
8. [Submitting a Pull Request](#submitting-a-pull-request)
9. [Pull Request Template](#pull-request-template)
10. [Picking Your First Issue](#picking-your-first-issue)
11. [Getting Help](#getting-help)

---

## Before You Start

- Read the [README.md](README.md) to understand what DevPath does and how it works
- Read the [docs/architecture.md](docs/architecture.md) to understand the code structure
- Browse open issues on GitHub and look for labels: `good first issue`, `help wanted`
- Check whether the issue you want to work on is already assigned to someone
- Comment on the issue to let maintainers know you are working on it

Required tools:

- Python 3.8 or higher
- Git
- A code editor (VS Code is recommended for beginners)

---

## Project Structure Overview

```
devpath/
|-- app.py                  Entry point. Creates the Flask app. Do not add logic here.
|-- routes/
|   |-- main_routes.py      All HTTP routes. Thin — no business logic.
|-- utils/
|   |-- data_loader.py      Reads projects.json and looks up projects by ID.
|   |-- recommender.py      Scoring algorithm and input validation.
|   |-- file_server.py      Starter code file resolution and serving.
|-- data/
|   |-- projects.json       The project dataset. Easy to extend.
|-- templates/              Jinja2 HTML templates.
|-- static/                 CSS and JavaScript.
|-- starter_code/           Starter templates referenced by projects.json.
|-- tests/
|   |-- test_basic.py       Test suite. Run before every pull request.
|-- docs/                   Documentation files.
```

The most beginner-friendly areas to contribute to are:

- `data/projects.json` — Add new projects
- `static/style.css` — Improve styling
- `templates/` — Improve HTML layout
- `docs/` — Improve documentation

---

## Development Setup

### Step 1: Fork and clone

Click the **Fork** button on the GitHub repository page to create your own copy.
Then clone it locally:

```bash
git clone https://github.com/komalharshita/devpath.git
cd devpath
```

### Step 2: Set up a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the app

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser. You should see the DevPath homepage.

### Step 5: Keep your fork up to date

Before starting any new work, sync your fork with the upstream repository:

```bash
git remote add upstream https://github.com/komalharshita/devpath.git
git fetch upstream
git checkout main
git merge upstream/main
```

---

## Branch Naming Convention

Always create a new branch for your work. Never commit directly to `main`.

Use this format: `type/short-description`

| Type       | When to use                                      | Example                         |
|------------|--------------------------------------------------|---------------------------------|
| `feat`     | Adding a new feature                             | `feat/dark-mode-toggle`         |
| `fix`      | Fixing a bug                                     | `fix/form-validation-error`     |
| `docs`     | Documentation changes only                       | `docs/update-contributing-guide`|
| `style`    | CSS or visual changes (no logic changes)         | `style/improve-card-spacing`    |
| `refactor` | Code restructuring without changing behaviour    | `refactor/scoring-function`     |
| `test`     | Adding or updating tests                         | `test/add-recommender-tests`    |
| `data`     | Adding or editing entries in projects.json       | `data/add-django-project`       |
| `chore`    | Maintenance tasks (dependencies, config, etc.)   | `chore/update-requirements`     |

Create your branch:

```bash
git checkout -b feat/your-feature-name
```

---

## Code Style Rules

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions
- Use `snake_case` for all variable and function names
- Maximum line length: 88 characters
- Add a single-line comment above any non-obvious logic
- Use descriptive names: `user_skills` is better than `us` or `skills_list`
- Every function should have a short docstring explaining what it does
- Do not use `print()` for debugging — remove all debug output before submitting
- Keep functions small and focused on one task

Example of acceptable Python style:

```python
def score_single_project(project, user_skills, level, interest, time_availability):
    """Calculate a relevance score for one project against the user inputs."""
    score = 0

    # Compare user skills against project requirements
    project_skills = [s.lower() for s in project.get("skills", [])]
    matched = sum(1 for skill in user_skills if skill in project_skills)
    score += matched * WEIGHT_SKILL

    return score
```

### HTML

- Use 2-space indentation
- Every `<section>` must have a comment header explaining its purpose
- All images must have an `alt` attribute
- Use `loading="lazy"` on `<img>` tags by default; omit it only for images critical to the initial render (for example, a hero photo above the fold)
- Use semantic elements: `<nav>`, `<section>`, `<footer>`, `<article>`
- Keep inline styles out of templates — use CSS classes instead

### CSS

- Group properties in this order: positioning, display, box model, typography, colours, transitions
- Use the existing CSS custom properties (variables) defined at the top of `style.css`
- Add a short comment above each major section
- Do not add vendor prefixes unless they are necessary for broad browser support

### JavaScript

- Use `var` declarations for maximum compatibility (the project targets no framework)
- Use `camelCase` for variable and function names
- Add a comment above each function explaining what it does
- Do not use arrow functions or ES6+ features — keep it ES5-compatible
- Handle all error paths in `fetch()` calls

### projects.json

- Every new project must include all required fields (see README.md for the schema)
- `id` values must be unique integers — use the next highest ID in the file
- `starter_code` must point to an actual file inside `starter_code/`
- The `roadmap` array should have between 5 and 10 entries
- Do not use markdown formatting inside JSON string values

---

### External Links

- External URLs added to `projects.json` are rendered using `target="_blank"`
- Only include trustworthy, safe, and relevant links
- Avoid shortened or obfuscated URLs
- Verify that all links are accessible before submitting a PR

## Commit Message Format

Use the same `type/scope: description` format as branch names for commit messages.

```
feat: add bookmarking system for saved projects
fix: correct skill chip removal not updating hidden input
docs: add architecture diagram to docs/architecture.md
style: improve card hover state contrast ratio
test: add validation tests for missing interest field
data: add three new data science projects to dataset
```

Rules:

- Use the present tense ("add feature" not "added feature")
- Keep the first line under 72 characters
- If more context is needed, leave a blank line and add a paragraph below
- Reference issue numbers when relevant: `fix: resolve empty state display (#23)`

---

## Running the Tests

Run the test suite before pushing any changes:

```bash
python tests/test_basic.py
```

All 27 tests must pass. If any test fails, fix the issue before opening a PR.

You can also run with pytest if you have it installed:

```bash
pip install pytest
pytest tests/ -v
```

If you add a new feature, add at least one corresponding test in `tests/test_basic.py`.

---

## Submitting a Pull Request

### Before opening a PR

- All 27 tests pass locally
- You have tested the running app in your browser
- Your branch is up to date with the upstream `main` branch
- Your code follows the style rules above
- You have removed all debug `print()` statements and commented-out code
- Update `CHANGELOG.md` for any user-facing or documentation-related changes

### Steps

1. Push your branch to your fork:
   ```bash
   git push origin your-branch-name
   ```

2. Go to your fork on GitHub and click **Compare and pull request**.

3. Fill in the PR template below.

4. Request a review if you know a maintainer; otherwise the team will review within a few days.

5. Address any review comments by pushing new commits to the same branch.

---


## Picking Your First Issue

Issues are labeled to help you find the right starting point:

| Label             | Meaning                                                              |
|-------------------|----------------------------------------------------------------------|
| `good first issue`| Small, self-contained tasks ideal for first-time contributors        |
| `help wanted`     | Tasks where maintainer input is welcome                              |
| `bug`             | Something is broken and needs fixing                                 |
| `enhancement`     | A new feature or improvement to an existing feature                  |
| `documentation`   | Writing or improving docs, comments, or guides                       |
| `beginner`        | Suitable for developers new to Python or Flask                       |
| `intermediate`    | Requires understanding of the codebase structure                     |
| `advanced`        | Requires knowledge of Flask, sessions, or frontend architecture      |

Recommended first issues:

- Adding a new project entry to `data/projects.json`
- Improving a label or placeholder text in `templates/index.html`
- Adding a new test case to `tests/test_basic.py`
- Fixing a visual spacing issue in `static/style.css`

---

## Getting Help

- Open a GitHub Discussion for questions about the codebase
- Comment directly on the issue you are working on
- Tag a maintainer in your PR if you are stuck on review feedback
- No question is too basic — this project is designed for learners
