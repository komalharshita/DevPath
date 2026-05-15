# Contribution Guide — DevPath

Welcome. This guide is written for developers who are making their first
open-source contribution, or their first contribution to DevPath specifically.
Follow it step by step and you will have a working pull request within an hour.

---

## Step 0 — Read Before You Write

Before touching any code:

1. Read `README.md` to understand what the project does
2. Read `docs/architecture.md` to understand how the code is organised
3. Browse the open GitHub Issues and find one labeled **good first issue**
4. Comment on the issue to let others know you are working on it

This prevents duplicate work and gives maintainers a chance to clarify
requirements before you invest time writing code.

---

## Step 1 — Fork and Clone

**Fork** the repository using the "Fork" button on GitHub. This creates a
personal copy under your account.

Then clone your fork:

```bash
git clone https://github.com/komalharshita/devpath.git
cd devpath
```

Add the original repository as an upstream remote so you can pull future
changes:

```bash
git remote add upstream https://github.com/komalharshita/devpath.git
```

---

## Step 2 — Set Up Your Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate it
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows

# Install all dependencies
pip install -r requirements.txt
```

Start the app to confirm everything works:

```bash
python app.py
```

Visit http://127.0.0.1:5000. You should see the DevPath homepage.

---

## Step 3 — Create a Branch

Always work on a new branch. Never commit directly to `main`.

Branch names follow this convention:

```
<type>/<short-description>
```

Types:

| Type     | Use when                                  |
|----------|-------------------------------------------|
| `feat`   | Adding a new feature                      |
| `fix`    | Fixing a bug                              |
| `docs`   | Updating documentation only               |
| `style`  | CSS or visual changes only                |
| `test`   | Adding or updating tests                  |
| `data`   | Adding projects to `projects.json`        |
| `refactor` | Code restructuring without behaviour change |

Examples:

```bash
git checkout -b feat/add-dark-mode
git checkout -b fix/mobile-nav-overflow
git checkout -b data/add-django-blog-project
git checkout -b docs/update-architecture
```

---

## Step 4 — Make Your Changes

### Code style rules

**Python:**

- Follow PEP 8 — use 4 spaces for indentation, no tabs
- Keep functions short and focused on one task
- Add a single-line comment above any non-obvious logic
- Use `snake_case` for all variable and function names
- Every new function must have a docstring

```python
# Good — clear name, short, documented
def parse_skills(skills_string):
    """Convert 'Python, HTML' into ['python', 'html']."""
    return [s.strip().lower() for s in skills_string.split(",") if s.strip()]

# Avoid — unclear name, no docstring, mixed concerns
def proc(s):
    x = s.split(",")
    return [i.lower().strip() for i in x if i]
```

**HTML / Jinja2:**

- Use two-space indentation
- Every section must have a comment header
- Keep logic out of templates — pass computed values from Python

**CSS:**

- Add all new colour values as CSS variables in the `:root` block
- Do not use `!important` — fix specificity instead
- Group related rules under a labelled comment block

**JavaScript:**

- Use `var` (the project targets broad browser compatibility, no bundler)
- Use `camelCase` for all variable and function names
- Add a single-line comment above any non-obvious block
- Do not use `console.log` in submitted code (use it while developing, remove before PR)

---

## Step 5 — Test Your Changes

Run the full test suite before committing:

```bash
python tests/test_basic.py
```

Expected output: `27 passed, 0 failed out of 27 tests`

If you added new functionality, add at least one test for it in
`tests/test_basic.py`. Follow the existing test naming pattern:
`test_<what_it_tests>`.

If you changed the UI, test it in at least two screen widths:
- Desktop: 1280px wide
- Mobile: 375px wide (use browser dev tools)

---

## Step 6 — Commit Your Changes

Write clear, specific commit messages in imperative mood:

```
# Good
Add three beginner Python projects to dataset
Fix mobile navigation overflow on screens under 360px
Improve score_single_project docstring

# Avoid
fixed stuff
update
changes
```

For larger changes, use a short summary followed by bullet points:

```
Refactor recommender into separate utility module

- Move scoring logic out of app.py into utils/recommender.py
- Add parse_skills() helper with unit tests
- Add named constants for scoring weights
- Update all import references in routes/main_routes.py
```

Stage and commit:

```bash
git add .
git commit -m "Your commit message here"
```

---

## Step 7 — Push and Open a Pull Request

Push your branch to your fork:

```bash
git push origin your-branch-name
```

Go to your fork on GitHub and click "Compare and pull request".

### Pull request checklist

Before submitting, confirm:

- [ ] The branch is up to date with `upstream/main`
- [ ] All 27 tests pass (`python tests/test_basic.py`)
- [ ] New functions have docstrings
- [ ] No `console.log` or debug `print()` statements remain
- [ ] The app starts without errors (`python app.py`)
- [ ] If you changed the UI, it looks correct on mobile

### PR template

Use this format for your PR description:

```
## Summary
A one-paragraph description of what this PR does and why.

## Changes Made
- List of files changed and why
- ...

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Data addition (new projects)
- [ ] Style / UI change

## Testing Done
Describe how you tested the change. Include the test output if you added tests.

## Screenshots (if UI change)
Before / after screenshots if the PR changes anything visual.

## Related Issue
Closes #<issue-number>
```

---

## Step 8 — Respond to Review

Maintainers may ask for changes. This is normal and expected — it is part of
the learning process. Read the feedback carefully, make the requested changes
on the same branch, push again, and reply to each comment once addressed.

---

## Issue Selection Guide

### If you are a first-time contributor

Look for issues labeled **good first issue**. These are tasks that:

- Do not require understanding the full codebase
- Have a clear and specific expected outcome
- Have been confirmed by a maintainer as ready to work on

Examples: adding new projects to `projects.json`, fixing a typo in docs,
improving a CSS property, adding a new label or form hint.

### If you have some experience

Look for issues labeled **enhancement** or **help wanted**. These may require
reading one or two utility modules but do not require restructuring the whole
app.

### If you are experienced

Look for issues labeled **advanced**. These involve adding new features that
require understanding multiple modules, writing tests, and updating documentation.

---

## Getting Help

If you are stuck:

1. Re-read `docs/architecture.md` — most questions are answered there
2. Read the existing code for the module closest to your task
3. Open a comment on the GitHub Issue asking a specific question

Be specific when asking for help. "It doesn't work" is hard to help with.
"I get a `KeyError: 'starter_code'` on line 42 of `utils/file_server.py`
when I add a project without a `starter_code` field" is actionable.

---

## Thank You

Every contribution — a typo fix, a new project, a test, a bug report — makes
DevPath more useful for the developers who come after you. Thank you for giving
your time to this project.
