# Project Overview — DevPath

## What Is DevPath?

DevPath is an open-source web application that helps developers — especially
beginners — find meaningful coding projects to build. Instead of searching
through generic lists, a developer describes their situation in four inputs
and DevPath returns the three best-matched projects, complete with everything
needed to start immediately.

---

## The Problem It Solves

Many beginner and intermediate developers know they should be building projects
to grow their skills, but they face two blockers:

1. **"What should I build?"** — Choosing a project that is too easy wastes
   time; too hard and they give up.
2. **"Where do I start?"** — Even a well-chosen project idea is overwhelming
   without a clear first step.

DevPath addresses both problems in a single tool.

---

## How It Works (User Perspective)

1. The user opens DevPath and enters the skills they already know (e.g. Python,
   HTML, JavaScript).
2. They select three preferences: experience level, area of interest, and
   how much time they can commit.
3. DevPath scores every project in its dataset against those inputs and returns
   the top three matches.
4. Each match links to a full detail page showing: description, feature list,
   tech stack, a visual roadmap, learning resources, and a downloadable starter
   code template.

---

## Target Audience

- Beginner programmers who have learned the basics and want to apply them
- Intermediate developers exploring a new language or interest area
- Open-source program participants (GSSoC, Hacktoberfest) looking for a
  contribution-ready project to work on
- Coding bootcamp students who need portfolio projects

---

## Design Philosophy

**Simple over clever.** The recommendation engine is intentionally rule-based
rather than ML-based. This keeps the code readable, testable, and accessible
to contributors of all experience levels.

**Modular over monolithic.** Logic is split into `utils/` modules so each
concern (data loading, scoring, file serving) can be understood and tested
independently.

**Documented over assumed.** Every function has a docstring explaining its
inputs, outputs, and purpose.

---

## Dataset

All project data lives in `data/projects.json`. Each project is a self-contained
JSON object describing everything a developer needs: skills required, level,
interest area, time commitment, a description, features, tech stack, roadmap
steps, learning resources, and the path to its starter code file.

The dataset is deliberately small (7 projects) to keep it easy for contributors
to add their own entries without needing to understand the full codebase.

---

## Starter Code

Each project has a corresponding starter template in `starter_code/`. These
files are intentionally incomplete — they scaffold the structure and define
the function signatures, but leave the implementation as a learning exercise.
This is the "blank page problem" solution: the developer has a working skeleton
to read, modify, and extend.

---

## Open-Source Structure

DevPath is designed to be a learning ground for open-source contribution. The
codebase is deliberately kept simple, the issues are labelled by difficulty, and
the documentation walks through everything from setup to pull requests. It is
suitable as a mentored project for programs like GSSoC, MLH, or Hacktoberfest.
