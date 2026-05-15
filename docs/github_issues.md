# GitHub Issues — DevPath

This file documents all structured issues ready to be created on GitHub.
Copy each block into a new GitHub Issue when setting up the repository.

---

## Beginner Issues (Good First Issue)

---

### Issue 1

**Title:** Fix vertical alignment of form labels on mobile screens

**Description:**
On screen widths below 480px, the form labels in the recommendation form sit
too close to the input field below them. There is not enough visual separation
between the label text and the input border, making the form feel cramped.

**Expected Outcome:**
On all mobile screen sizes (tested at 375px and 414px), each label has at
least 8px of space below it before the input begins. The change should only
affect the mobile breakpoint and leave desktop spacing unchanged.

**Files to look at:**
- `static/style.css` — search for the `@media (max-width: 640px)` block
- `templates/index.html` — the `.form-group` elements

**Labels:** `good first issue`, `style`, `bug`

---

### Issue 2

**Title:** Improve the styling of the submit button on hover state

**Description:**
The "Generate My Projects" submit button currently darkens slightly on hover.
The effect is subtle and does not clearly communicate that the button is
interactive, especially for users with lower vision.

**Expected Outcome:**
The hover state should include a visible change — for example, a slight
upward movement (`transform: translateY(-2px)`) and a stronger box shadow.
The change must not break the disabled state (shown during API loading).

**Files to look at:**
- `static/style.css` — the `.btn-submit` and `.btn-submit:hover` rules

**Labels:** `good first issue`, `style`, `enhancement`

---

### Issue 3

**Title:** Add three new beginner-level projects to the dataset

**Description:**
The current dataset contains 7 projects. Adding more projects gives users
more chances to find a good match, especially in underrepresented interest
areas like Automation and Games.

**Expected Outcome:**
Three new projects added to `data/projects.json`, each with:
- A complete set of all required fields (id, title, skills, level, interest,
  time, description, features, tech_stack, roadmap, resources, starter_code)
- At least one targeting the `Automation` or `Games` interest area
- A corresponding starter code template in `starter_code/`
- A unique integer ID higher than the current maximum

The app must start without errors after the additions and the new projects
must appear in recommendations when the matching inputs are selected.

**Files to look at:**
- `data/projects.json` — follow the existing project structure exactly
- `starter_code/` — add one `.py` or `.html` starter file per project
- `docs/project_overview.md` — update the project count if changed

**Labels:** `good first issue`, `data`, `enhancement`

---

### Issue 4

**Title:** Improve accessibility labels on all form inputs

**Description:**
The form on the homepage is missing `aria-required="true"` attributes on
required inputs and `aria-describedby` links connecting inputs to their hint
and error message elements. Screen readers cannot currently associate the
hint text or error messages with their corresponding inputs.

**Expected Outcome:**
Each required input and select element has `aria-required="true"`. Each input
has an `aria-describedby` value pointing to its hint span and error div IDs.
For example:

```html
<input
  id="skills-input"
  aria-required="true"
  aria-describedby="skills-hint skills-error"
/>
<span id="skills-hint" class="form-hint">...</span>
<div id="skills-error" class="form-error-msg"></div>
```

No visual changes are expected. This is a pure accessibility improvement.

**Files to look at:**
- `templates/index.html` — the `#recommend-form` section

**Labels:** `good first issue`, `accessibility`, `enhancement`

---

### Issue 5

**Title:** Add inline comments to script.js for new contributors

**Description:**
`static/script.js` has some comments but several functions in the skill chip
manager and result card builder have no explanation of what they do or why.
New contributors who are not familiar with DOM manipulation will struggle
to understand `renderSelectedChips()`, `syncSkillsHiddenInput()`, and
`buildProjectCard()` without context.

**Expected Outcome:**
Every function in `script.js` has at least one line comment above it
explaining its purpose in plain language. Complex lines within functions
(such as the `isDuplicate` check and the `truncate` call) have a short
inline comment. No logic should be changed — this is documentation only.

**Files to look at:**
- `static/script.js`

**Labels:** `good first issue`, `documentation`

---

## Intermediate Issues

---

### Issue 6

**Title:** Refactor the scoring weights into a configuration dictionary

**Description:**
The scoring weights in `utils/recommender.py` are currently four separate
module-level constants. As the project grows, it would be cleaner to group
them into a single dictionary that can be imported and used consistently.

**Expected Outcome:**
Replace the four constants with a single `SCORING_WEIGHTS` dictionary:

```python
SCORING_WEIGHTS = {
    "skill":    3,
    "level":    2,
    "interest": 2,
    "time":     1,
}
```

Update `score_single_project()` to read from this dictionary. All 27
existing tests must still pass after the refactor. Add one new test that
verifies the dictionary contains all four expected keys.

**Files to look at:**
- `utils/recommender.py`
- `tests/test_basic.py`

**Labels:** `enhancement`, `refactor`, `intermediate`

---

### Issue 7

**Title:** Improve the roadmap display on the project detail page

**Description:**
The roadmap timeline on `/project/<id>` currently shows plain text steps.
It would be more readable if completed-looking steps were visually distinct
from upcoming steps, and if the connecting line between dots used a dashed
style to imply progress rather than a solid line.

**Expected Outcome:**
- The connector line between roadmap dots is `border-left: 2px dashed`
  instead of solid
- The first roadmap dot uses a filled style (already done)
- All other dots use a hollow style (white fill, coloured border) to
  suggest they are future steps
- No JavaScript is required — this is CSS-only

**Files to look at:**
- `static/style.css` — the roadmap timeline section
- `templates/project.html` — the `.roadmap-step` structure

**Labels:** `enhancement`, `style`, `intermediate`

---

### Issue 8

**Title:** Add a live skill search filter to the results section

**Description:**
After results are displayed, there is no way to filter them further.
Adding a small text input above the results grid would let users type a
keyword and instantly hide cards that do not match the title or description.

**Expected Outcome:**
A search input appears above the results grid when at least one result
is showing. As the user types, project cards are shown or hidden based
on whether their title or description contains the search text
(case-insensitive). Clearing the input restores all cards. This must be
implemented in plain JavaScript — no libraries.

**Files to look at:**
- `templates/index.html` — add the search input above `#results-grid`
- `static/script.js` — add a filter function triggered by the input event
- `static/style.css` — style the search input consistently with the form

**Labels:** `enhancement`, `intermediate`, `help wanted`

---

### Issue 9

**Title:** Make the project cards section fully responsive at 360px

**Description:**
On very small screens (360px, common on budget Android devices), the project
result cards overflow their container. The tag row wraps awkwardly and the
"View Full Project" button text is clipped.

**Expected Outcome:**
At 360px viewport width:
- All cards fit within the viewport without horizontal scrolling
- Tags wrap cleanly to a second line if needed
- The action button text is fully visible
- Card padding is reduced to 20px on each side (from 28px)

Test using Chrome DevTools device emulation set to 360x800.

**Files to look at:**
- `static/style.css` — add a `@media (max-width: 380px)` block

**Labels:** `bug`, `responsive`, `intermediate`

---

## Advanced Issues

---

### Issue 10

**Title:** Add a client-side project bookmarking system

**Description:**
Users often want to save a project they liked and come back to it later.
Adding a bookmark feature using `localStorage` allows this without requiring
a backend database or user accounts.

**Expected Outcome:**
- Each project card on the results page has a bookmark toggle button
  (a simple outline star icon, filled when bookmarked)
- Clicking the button saves the project ID and title to `localStorage`
  under the key `devpath_bookmarks`
- A "Saved Projects" panel is accessible from the navbar (a simple dropdown
  or sidebar listing bookmarked project titles as links)
- Bookmarks persist across page reloads and browser sessions
- Removing a bookmark updates `localStorage` and removes it from the panel
  immediately

**Files to look at:**
- `static/script.js` — add bookmark save/load/render logic
- `templates/index.html` — add bookmark button to card template and a
  panel element to the navbar
- `static/style.css` — style the bookmark button and panel

**Labels:** `enhancement`, `advanced`, `help wanted`

---

### Issue 11

**Title:** Add Flask session-based "recently viewed projects" tracking

**Description:**
When a user visits a project detail page, it would be useful to show them
a "Recently Viewed" section on the homepage that links back to the projects
they explored in the current session.

**Expected Outcome:**
- Flask's built-in session stores a list of up to 5 recently viewed project
  IDs whenever `/project/<id>` is visited
- The homepage checks the session and, if any IDs exist, renders a
  "Recently Viewed" section below the form with links to those projects
- The list is ordered most-recent-first
- The session clears on browser close (use `session.permanent = False`)
- A `SECRET_KEY` is added to `app.py` for session signing (use an
  environment variable, not a hardcoded string)
- The README is updated to document the `SECRET_KEY` requirement

**Files to look at:**
- `app.py` — add `app.secret_key`
- `routes/main_routes.py` — update `project_detail()` to write to session,
  update `index()` to read from session and pass data to the template
- `templates/index.html` — add the "Recently Viewed" section
- `static/style.css` — style the section

**Labels:** `enhancement`, `advanced`

---

### Issue 12

**Title:** Optimise data loading to avoid reading the JSON file on every request

**Description:**
`utils/data_loader.py` currently reads `projects.json` from disk on every
call to `load_all_projects()`. For a small dataset this is fine, but as the
project grows, repeated disk reads will slow down every recommendation
request, detail page load, and test run.

**Expected Outcome:**
Implement a simple in-memory cache: after the first read, store the result in
a module-level variable. Subsequent calls return the cached value instead of
re-reading the file.

```python
_projects_cache = None

def load_all_projects():
    global _projects_cache
    if _projects_cache is None:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            _projects_cache = json.load(f)
    return _projects_cache
```

The cache must be invalidatable — add a `clear_cache()` function used in
tests to reset state between test runs. Update `tests/test_basic.py` to call
`clear_cache()` in a setup step. All 27 existing tests must still pass.

Document the trade-off in a code comment: the cache means changes to
`projects.json` will not be reflected until the app restarts. This is
acceptable for development use but should be noted.

**Files to look at:**
- `utils/data_loader.py`
- `tests/test_basic.py`

**Labels:** `enhancement`, `performance`, `advanced`

---

## Label System

When creating these issues on GitHub, use the following labels:

| Label            | Colour  | Purpose                                              |
|------------------|---------|------------------------------------------------------|
| `good first issue` | Green | Safe entry point for first-time contributors          |
| `bug`            | Red     | Something is broken or behaves incorrectly            |
| `enhancement`    | Blue    | A new feature or improvement to existing functionality |
| `documentation`  | Yellow  | Changes to docs, comments, or README only            |
| `style`          | Purple  | CSS, layout, or visual changes only                  |
| `data`           | Orange  | Adding or updating entries in `projects.json`        |
| `accessibility`  | Teal    | Improvements to screen reader support or ARIA        |
| `responsive`     | Indigo  | Layout fixes for specific screen sizes               |
| `performance`    | Gray    | Speed or efficiency improvements                     |
| `refactor`       | Pink    | Code restructuring without behaviour change           |
| `help wanted`    | Cyan    | Maintainers are actively seeking a contributor       |
| `intermediate`   | Lavender | Requires reading 1-2 modules, some JS/CSS experience |
| `advanced`       | Dark Red | Requires full understanding of the codebase          |
