# Frequently Asked Questions (FAQ)

## 1. What is DevPath and who is it for?
DevPath is an open‑source web app that helps beginner and intermediate developers discover small, self‑contained coding projects they can start building in minutes. It’s aimed at learners, bootcamp students, and open‑source program participants who want concrete project ideas.

## 2. How does the recommendation engine work?
The engine scores each project using a rule‑based weighting of matching skills, experience level, interest area, and available time. It also adds a small similarity boost based on TF‑IDF cosine similarity of textual fields. The top three highest‑scoring projects are returned.

## 3. How can I add a new project to the dataset?
Add a JSON object to `data/projects.json` following the existing schema (id, title, skills, level, interest, time, description, features, tech_stack, roadmap, resources, starter_code). Use a unique integer `id` that is one higher than the current maximum.

## 4. Why am I not getting any recommendations?
Possible reasons:
- Your skill list does not overlap with any project's required skills.
- The selected time availability is lower than the project's required time.
- The level or interest you chose does not match any project.
Adjust your inputs or add more projects to the dataset.

## 5. How do I run the project locally?
1. Clone the repo.
2. Create a virtual environment and activate it.
3. Install dependencies with `pip install -r requirements.txt`.
4. Run `python app.py` and open `http://127.0.0.1:5000` in a browser.

## 6. How can I contribute as a first‑time open‑source contributor?
Start with issues labeled `good first issue`. Follow the steps in `CONTRIBUTING.md`: fork, create a branch (`type/short‑description`), make your change, run the test suite, and open a PR using the provided template.

## 7. How do I run the test suite?
Execute:
```
python tests/test_basic.py
```
All tests must pass before submitting a PR.

## 8. Where can I report bugs or request new features?
Use the GitHub **Issues** tab. Choose an appropriate label (bug, enhancement) and provide a clear description. For discussion, use the **Discussions** section.
