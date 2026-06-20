## Issue #747: [Bug]: Duplicate project IDs in projects.json cause ambiguous project lookup
Labels: ['gssoc-2026', 'bug']
Body:
### What happened?

## Bug Description

Several entries in `data/projects.json` use duplicate project IDs.

Current duplicates:

- ID 8 appears twice
- ID 9 appears three times
- ID 10 appears twice

The application uses project IDs for project lookup via `get_project_by_id(...)`.

Because IDs are not unique, only the first matching project is returned during lookup.

## Steps to Reproduce

1. Open `data/projects.json`
2. Observe duplicate IDs:
   - 8
   - 9
   - 10

3. Start the application

4. Navigate to:

   /project/8

## Expected Behavior

Each project should have a unique identifier and be individually accessible.

## Actual Behavior

The first matching project is returned.
Projects sharing the same ID become unreachable.

## Impact

Affected routes may include:

- `/project/<id>`
- `/project/<id>/code`
- `/project/<id>/download`

This can result in:
- Incorrect project detail pages
- Incorrect starter code downloads
- Recommendation links resolving to the wrong project

## Suggested Fix

1. Ensure all project IDs are unique.
2. Add a dataset validation test that fails when duplicate IDs are present.

Example test:

```python
ids = [project["id"] for project in projects]
assert len(ids) == len(set(ids))

### Steps to reproduce


1. Open `data/projects.json`.

2. Search for duplicate IDs:
   - ID 8 appears twice
   - ID 9 appears three times
   - ID 10 appears twice

3. Start the application:

   ```bash
   python app.py

### Expected behaviour

Each project should have a unique ID and be individually accessible through the project detail route.

### Area of the app affected

Project detail page

### Python version

Python 3.12.3

### Operating system

Ubuntu 24.04

### Relevant error output or logs

```shell

```

### Before submitting

- [x] I searched existing issues and this has not been reported before.
- [x] I can reproduce this bug consistently with the steps above.
- [x] I am running the latest version of the main branch.

--------------------------------------------------------------------------------
## Issue #726: [Bug]: "Generate My Projects" Button Sizing and Text Wrap
Labels: ['gssoc-2026', 'bug']
Body:
### What happened?

At the bottom of the filtering form, the "Generate My Projects" primary button has inconsistent sizing compared to the adjacent secondary button. The text inside the button wraps awkwardly to a second line ("Generate My" / "Projects"), which breaks the vertical alignment and makes the button taller than the "Clear Filters" button next to it.
  
I want work on this issue under Gssoc26

<img width="172" height="436" alt="Image" src="https://github.com/user-attachments/assets/e45e1f16-21df-47fd-ab40-8cb9ecb0f9ba" />

### Steps to reproduce

1 Open the project filtering form on a mobile viewport.
2 Scroll to the bottom of the form to view the action buttons.
3 Observe the height, text wrapping, and padding of the yellow "Generate My Projects" button.

### Expected behaviour

Action buttons placed side-by-side should typically maintain a consistent height. The primary button should ideally be wide enough to accommodate its text on a single line, or the button layout should switch to a stacked column structure (one button on top of the other) on very narrow screens to prevent cramped text wrapping.

### Area of the app affected

Homepage form

### Python version

3.11.4

### Operating system

macos

### Relevant error output or logs

```shell

```

### Before submitting

- [x] I searched existing issues and this has not been reported before.
- [x] I can reproduce this bug consistently with the steps above.
- [x] I am running the latest version of the main branch.

--------------------------------------------------------------------------------
## Issue #725: [Bug]: "HTML / CSS " Skill Pill Overflows Container
Labels: ['gssoc-2026', 'bug']
Body:
### What happened?

In the "Supports Skills Including" section, the right-most skill badge ("HTML / CSS") breaks out of its parent card container. The element overflows off the right side of the screen, indicating an issue with how the items are wrapping on smaller viewports.
  
I want to work on this issue under Gssoc26

<img width="172" height="436" alt="Image" src="https://github.com/user-attachments/assets/dbe598a5-459a-48b3-b304-9bacfb829e5a" />

### Steps to reproduce

1.Navigate to the landing page on a mobile device or narrow viewport.
2.Scroll down to the "Supports Skills Including:" card.
3.Observe the layout of the skill pills (Python, JavaScript, HTML / CSS).

### Expected behaviour

The parent container holding the skill badges should safely contain all elements. If the screen is too narrow, the items should automatically wrap to a second line (e.g., using flex-wrap: wrap;) or the container should provide a horizontal scrollbar.
Actual Behavior
The "HTML / CSS" pill overflows the dark blue background container on the right side.

### Area of the app affected

Homepage form

### Python version

3.11.4

### Operating system

macos

### Relevant error output or logs

```shell

```

### Before submitting

- [x] I searched existing issues and this has not been reported before.
- [x] I can reproduce this bug consistently with the steps above.
- [x] I am running the latest version of the main branch.

--------------------------------------------------------------------------------
## Issue #724: [Bug]: Hamburger Menu Unresponsive on Mobile Viewport
Labels: ['gssoc-2026', 'bug']
Body:
### What happened?

Description
When viewing the application on a mobile device, tapping the hamburger menu icon does not open the navigation drawer. The icon registers the click (or appears to), but the state does not change, leaving users unable to access the main navigation links.
Note: The attached screen recording shows the mobile hero section, but the hamburger icon and top navigation bar are out of frame. The clicks shown are on the main body text.
    

I want to work on this issue under Gssoc26

https://github.com/user-attachments/assets/cbc28f9c-7535-40a7-817a-768ce7ead6ce

### Steps to reproduce

Steps to Reproduce
1.Open the application in a mobile browser (or simulate mobile view in Developer Tools).
2.Look at the top navigation bar to locate the hamburger menu icon.
3.Tap/click on the hamburger menu icon.
4.Notice that the menu fails to expand or slide out.

### Expected behaviour

Tapping the hamburger menu icon should toggle the navigation menu's visibility, sliding it smoothly into view or expanding it downward so the user can navigate the site.
Actual Behavior
The hamburger menu icon is completely unresponsive, and the navigation links remain hidden.

### Area of the app affected

Homepage form

### Python version

3.11.4

### Operating system

macos

### Relevant error output or logs

```shell

```

### Before submitting

- [x] I searched existing issues and this has not been reported before.
- [x] I can reproduce this bug consistently with the steps above.
- [x] I am running the latest version of the main branch.

--------------------------------------------------------------------------------
## Issue #712: [Bug]: Clear Filters button does not reset applied filters
Labels: ['gssoc-2026', 'bug']
Body:
### What happened?

**Description**

The "Clear Filters" button is not functioning as expected. After applying one or more filters and clicking "Clear Filters", the selected filters remain active and the filtered results do not return to their default state.
Steps to Reproduce

1. Navigate to the relevant page.
2. Apply one or more filters.
3. Click the "Clear Filters" button.

**Expected Behavior**
All applied filters should be removed and the results should return to the default unfiltered state.

**Actual Behavior**
The filters remain applied (or only partially reset), and the displayed results do not fully return to the default state.

**Additional Information**

<img width="1897" height="981" alt="Image" src="https://github.com/user-attachments/assets/80e9b86c-6510-4875-83fd-320ba0996aab" />

Screenshots or screen recordings can be attached if helpful.


### Steps to reproduce

**Steps to Reproduce**
1. Navigate to the page containing the filter options.
2. Select one or more filters.
3. Verify that the displayed results update according to the selected filters.
4. Click the **"Clear Filters"** button.
5. Observe that the applied filters are not removed and/or the results remain filtered.


### Expected behaviour

All applied filters should be removed and the results should return to the default unfiltered state.


### Area of the app affected

Homepage form

### Python version

3.11.4

### Operating system

windows 11

### Relevant error output or logs

```shell

```

### Before submitting

- [x] I searched existing issues and this has not been reported before.
- [x] I can reproduce this bug consistently with the steps above.
- [x] I am running the latest version of the main branch.

--------------------------------------------------------------------------------
## Issue #710: [Bug]: Duplicate skills inflate recommendation score — parse_skills() doesn't deduplicate
Labels: ['gssoc-2026', 'bug']
Body:
### What happened?

parse_skills() in recommender.py doesn't remove duplicate skills. If a user enters the same skill multiple times (like "python, python, python"), each copy is counted as a separate match in score_single_project, multiplying the skill score. This lets a project's score be inflated just by repeating a skill, which distorts the ranking. Also "py" and "python" both normalize to "python" but are still counted as two separate skills.

### Steps to reproduce

1. Call get_recommendations("python", "Beginner", "Web", "Low") and note the scores
2. Call get_recommendations("python,python,python", "Beginner", "Web", "Low")
3. The repeated skill multiplies the score (a single match gives 8, three copies give 14)
4. parse_skills("python, python, py") returns ["python","python","python"] instead of ["python"]

### Expected behaviour

Duplicate skills should be counted only once. parse_skills() should return a deduplicated list so repeating a skill can't inflate the recommendation score or change the ranking.

### Area of the app affected

Recommendation results

### Python version

3.14

### Operating system

Windows 11

### Relevant error output or logs

```shell
No error thrown — silent ranking bug. parse_skills("python, python, py") returns ['python', 'python', 'python'].
```

### Before submitting

- [x] I searched existing issues and this has not been reported before.
- [x] I can reproduce this bug consistently with the steps above.
- [x] I am running the latest version of the main branch.

--------------------------------------------------------------------------------
## Issue #702: [Bug]: Unhandled ValueError in Recommendation Engine Causes 500 API Crash
Labels: ['gssoc-2026', 'bug']
Body:
### What happened?

The /api/recommend endpoint doesn't strictly validate the time parameter against its allowed values. If an unrecognized value is passed in the JSON payload, the backend attempts to look it up in a list using .index(), which throws an unhandled ValueError.

To make matters worse, because the app has a global 500 error handler that returns an HTML template (500.html), the API returns HTML instead of JSON. This violates the API contract and will instantly crash frontend JSON parsers expecting a structured response.

### Steps to reproduce

1. Start the Flask development server locally.

2. Open a terminal and send a POST request with an invalid time value:

curl -X POST http://localhost:5000/api/recommend \
     -H "Content-Type: application/json" \
     -d '{"skills": "python", "level": "Beginner", "interest": "Web", "time": "unknown_value"}'

3. Check the response—instead of a standard JSON error, you get a 500 status code containing the raw HTML of the 500.html error page.

### Expected behaviour

The application should validate the input in validate_recommendation_inputs() and gracefully return a 400 Bad Request with a JSON payload, such as: {"error": "Please select a valid time availability."}

### Area of the app affected

Recommendation results

### Python version

3.11

### Operating system

Windows 11

### Relevant error output or logs

```shell
ValueError: 'unknown_value' is not in list
  File "utils/recommender.py", in score_single_project
    time_availability_index = TIME_AVAILABILITY.index(time_availability.strip().lower())
```

### Before submitting

- [x] I searched existing issues and this has not been reported before.
- [x] I can reproduce this bug consistently with the steps above.
- [x] I am running the latest version of the main branch.

--------------------------------------------------------------------------------
## Issue #786: [Bug]: Feature Button Text Not Visible on Features Section
Labels: ['gssoc-2026', 'bug']
Body:
### What happened?

The text inside the buttons in the Features section is not visible or has very low contrast against the background. Users cannot clearly read the button labels, which affects usability and accessibility.

### Steps to reproduce

1. Open the application.
2. Navigate to the Features section.
3. Observe the feature buttons.
4. Notice that the button text is not visible or difficult to read.

### Expected behaviour

Button labels should be clearly visible with sufficient contrast and proper styling so users can easily identify and interact with them.

### Area of the app affected

Homepage form

### Python version

N/A

### Operating system

Windows 11 (can also be reproduced on other operating systems)

### Relevant error output or logs

```shell
No console errors observed. This is a UI styling issue.
```

### Before submitting

- [x] I searched existing issues and this has not been reported before.
- [x] I can reproduce this bug consistently with the steps above.
- [x] I am running the latest version of the main branch.

--------------------------------------------------------------------------------
## Issue #475: [Docs]: Duplicate "Starter Code Included" card in the Features section
Labels: ['gssoc-2026', 'documentation']
Body:
### Which document needs improvement?

Other

### What is wrong or missing?

## Description
The "Starter Code Included" feature card appears twice in the Features 
section - once with the full description and once with a slightly 
shorter version.

## Steps to Reproduce
1. Open https://mydevpath-github.vercel.app/
2. Scroll to the "Everything You Need to Start Building" section
3. Observe "Starter Code Included" card appears two times

## Expected Behavior
Each feature card should appear exactly once.

## Suggested Fix
Remove the duplicate card from the HTML template.

### Suggested improvement

## Suggested Fix
In `templates/index.html`, locate the Features section 
("Everything You Need to Start Building") and search for 
"Starter Code Included". You will find two card blocks with 
the same heading - remove the second one entirely, keeping 
only the first which has the complete description and the 
"Get starter code" link intact.

### Before submitting

- [x] I checked whether this documentation issue has already been reported.

--------------------------------------------------------------------------------