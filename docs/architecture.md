# Architecture — DevPath

This document explains how DevPath is structured, how data flows through the
system, and why each module exists.

---

## High-Level Architecture

```
Browser
  |
  |  HTTP request (GET / or POST /api/recommend)
  v
Flask Application (app.py)
  |
  |-- Blueprint registration
  v
routes/main_routes.py        <-- receives requests, validates, delegates
  |
  |-- calls utils/recommender.py    (scoring + filtering logic)
  |-- calls utils/data_loader.py    (reads projects.json)
  |-- calls utils/file_server.py    (resolves + serves starter code)
  |
  v
templates/ + static/         <-- rendered HTML + JS + CSS served to browser
```

---

## Module Responsibilities

### app.py

The entry point. Its only jobs are:

- Create the Flask app instance
- Register the `main` Blueprint from `routes/`
- Register the 404 and 500 error handlers
- Start the dev server when run directly

No business logic, no data access, no file handling.

---

### routes/main_routes.py

Contains all URL route handlers, registered as a Flask Blueprint named `main`.

Each route handler follows the same pattern:

1. Read and strip input from the request
2. Call one or more utility functions
3. Return a rendered template or a JSON response

Routes defined:

| Method | Path                          | Description                       |
|--------|-------------------------------|-----------------------------------|
| GET    | `/`                           | Render homepage                   |
| POST   | `/api/recommend`              | Return matching project JSON      |
| GET    | `/project/<id>`               | Render project detail page        |
| GET    | `/project/<id>/code`          | Return starter code content JSON  |
| GET    | `/project/<id>/download`      | Serve starter code as download    |

---

### utils/data_loader.py

Handles all reading and lookup of project data.

Functions:

- `load_all_projects()` — reads and returns the full JSON array
- `find_project_by_id(project_id)` — returns a single project dict or None

The data file path is resolved relative to the module file itself, so the app
works correctly regardless of the working directory it is started from.

---

### utils/recommender.py

Contains all recommendation logic. Nothing in this module knows about HTTP,
Flask, or file paths.

Functions:

- `parse_skills(skills_string)` — converts `"Python, HTML"` to `["python", "html"]`
- `score_single_project(project, user_skills, level, interest, time)` — returns an integer score
- `get_recommendations(skills, level, interest, time)` — returns the top N projects
- `validate_recommendation_inputs(...)` — returns a list of error strings

Scoring weights are named module-level constants:

```python
WEIGHT_SKILL    = 3   # Points per matching skill
WEIGHT_LEVEL    = 2   # Points for matching experience level
WEIGHT_INTEREST = 2   # Points for matching interest area
WEIGHT_TIME     = 1   # Points for matching time availability
```

Changing a weight number changes the relative influence of each criterion
across all recommendations.

---

### utils/file_server.py

Handles safe resolution and serving of starter code files.

Functions:

- `resolve_starter_file(project)` — returns the absolute path to the file, or None
- `read_starter_code(project)` — returns `{"filename": ..., "code": ...}` or None
- `get_starter_code_dir()` — returns the directory path for `send_from_directory`

The `os.path.basename()` call in `resolve_starter_file` ensures that a
malicious `starter_code` value in the JSON (such as `../../etc/passwd`) cannot
cause a path traversal vulnerability.

---

## Data Flow: Recommendation Request

```
1. User submits form
   |
2. script.js sends POST /api/recommend
   {skills: "Python", level: "Beginner", interest: "Data", time: "Low"}
   |
3. main_routes.recommend() reads and strips each field
   |
4. validate_recommendation_inputs() checks for empty fields
   - Returns 400 JSON error if any field missing
   |
5. get_recommendations() is called
   |
   5a. parse_skills("Python") -> ["python"]
   |
   5b. load_all_projects() reads data/projects.json (7 projects)
   |
   5c. For each project, score_single_project() computes:
       - Skill matches   x3 points each
       - Level match     +2 points
       - Interest match  +2 points
       - Time match      +1 point
   |
   5d. Projects with score > 0 are collected
   |
   5e. Sorted descending by score
   |
   5f. Top 3 returned
   |
6. main_routes.recommend() returns 200 JSON {projects: [...]}
   |
7. script.js receives response and calls renderResults()
   |
8. buildProjectCard() creates DOM elements for each project
   |
9. Cards inserted into #results-grid and section scrolled into view
```

---

## Data Flow: Project Detail Page

```
1. User clicks "View Full Project" link -> GET /project/1
   |
2. main_routes.project_detail(1) calls find_project_by_id(1)
   |
3. project dict passed to render_template("project.html", project=project)
   |
4. Jinja2 renders the template, iterating roadmap steps with loop.index
   |
5. Browser receives complete HTML
   |
6. User clicks "View Code" button
   |
7. script.js calls GET /project/1/code
   |
8. main_routes.view_code(1):
   - find_project_by_id(1) -> project dict
   - read_starter_code(project) -> {filename, code}
   - Returns 200 JSON
   |
9. script.js injects filename + code into the slide-up code panel
```

---

## Template Rendering

DevPath uses Flask's built-in Jinja2 templating. Templates receive data through
`render_template()` keyword arguments. The project detail template uses
`{{ project.title }}`, `{% for step in project.roadmap %}`, and similar
expressions to render dynamic content server-side.

No client-side template engine is used. The frontend JavaScript only handles
interactivity (form submission, chip management, code panel) and rendering of
the recommendation cards (which come back from the API as JSON).

---

## Static Files

CSS and JavaScript are served from the `static/` directory by Flask's built-in
static file handler. In production, these would ideally be served directly by
a web server like Nginx rather than through Flask.

---

## Testing Strategy

Tests live in `tests/test_basic.py` and are grouped into four categories:

1. **Data loader tests** — verify the JSON file loads and has correct structure
2. **Recommender unit tests** — test scoring, parsing, and validation in isolation
3. **HTTP route tests** — use Flask's test client to verify status codes and response shapes
4. **Edge case tests** — empty inputs, missing IDs, no-match scenarios

Run with: `python tests/test_basic.py` or `pytest tests/`

---

## Extending the Project

The most common extension points are:

| What to change          | Where to change it                          |
|-------------------------|---------------------------------------------|
| Add a new project       | `data/projects.json`                        |
| Change scoring weights  | `utils/recommender.py` (top constants)      |
| Add a new route         | `routes/main_routes.py`                     |
| Change recommendation count | `utils/recommender.py` (MAX_RESULTS)   |
| Add a new interest area | `data/projects.json` + `templates/index.html` dropdown |
| Change UI styling       | `static/style.css` CSS variables block      |
