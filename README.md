<div align="center">

<br/>

```text
 ____            ____       _   _
|  _ \  _____  _|  _ \ __ _| |_| |__
| | | |/ _ \ \/ / |_) / _` | __| '_ \
| |_| |  __/>  <|  __/ (_| | |_| | | |
|____/ \___/_/\_\_|   \__,_|\__|_| |_|
```

# Skill to Project Recommender

Beginner-friendly open-source project recommendation platform built with Flask.

<br/>

[![Python](https://img.shields.io/badge/Python-3.8%2B-2335c2?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-2335c2?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-fbbf24?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-7c3aed?style=flat-square&logo=git&logoColor=white)](CONTRIBUTING.md)
[![GSSoC](https://img.shields.io/badge/GSSoC-2026-fbbf24?style=flat-square&logo=opensourceinitiative&logoColor=0f1560)](https://gssoc.girlscript.tech/)

<br/>

[![Open Issues](https://img.shields.io/github/issues/komalharshita/devpath?color=2335c2&style=flat-square&logo=github)](https://github.com/komalharshita/devpath/issues)
[![Forks](https://img.shields.io/github/forks/komalharshita/devpath?color=7c3aed&style=flat-square&logo=github)](https://github.com/komalharshita/devpath/network/members)
[![Stars](https://img.shields.io/github/stars/komalharshita/devpath?color=fbbf24&style=flat-square&logo=github)](https://github.com/komalharshita/devpath/stargazers)
[![Contributors](https://img.shields.io/github/contributors/komalharshita/devpath?color=22c55e&style=flat-square&logo=github)](https://github.com/komalharshita/devpath/graphs/contributors)

[Quick Start](#quick-start) •
[How It Works](#how-it-works) •
[Contributing](#contributing) •
[Documentation](#documentation)

<br/>

</div>

---

# Overview

DevPath is an open-source Flask application that helps developers discover project ideas based on their skills, interests, experience level, and available time.

Users provide their preferences through a simple form interface, and the application recommends matching projects from a curated dataset along with:
- learning roadmaps
- resources
- starter templates
- project details

The project is intentionally beginner-friendly and structured for open-source contributions.

---

# Quick Start

## Clone the Repository

```bash
git clone https://github.com/komalharshita/devpath.git
cd devpath
```

## Create Virtual Environment

```bash
python -m venv venv
```

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python app.py
```

Open in browser:

```text
http://127.0.0.1:5000
```

---

# Project Structure

```text
devpath/
├── app.py
├── routes/
│   └── main_routes.py
├── utils/
│   ├── data_loader.py
│   ├── recommender.py
│   └── file_server.py
├── data/
│   └── projects.json
├── templates/
├── static/
├── starter_code/
├── tests/
│   └── test_basic.py
├── docs/
├── requirements.txt
└── README.md
```

---

# How It Works

```text
User Input
   ↓
Skill & Interest Matching
   ↓
Project Scoring
   ↓
Top Project Recommendations
```

The recommendation logic is implemented inside:

```text
utils/recommender.py
```

Projects are loaded from:

```text
data/projects.json
```

---

# Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Homepage |
| POST | `/api/recommend` | Returns recommended projects |
| GET | `/project/<id>` | Project details page |
| GET | `/project/<id>/code` | Starter code content |
| GET | `/project/<id>/download` | Download starter code |

---

# Extending the Dataset

Projects are stored in:

```text
data/projects.json
```

Example project entry:

```json
{
  "id": 8,
  "title": "Todo CLI App",
  "skills": ["Python"],
  "level": "Beginner",
  "interest": "Automation",
  "time": "Low"
}
```

Add a new object to the JSON array to include more projects.

---

# Running Tests

```bash
python tests/test_basic.py
```

---

# Contributing

Contributions are welcome.

## Contribution Workflow

```text
1. Fork the repository
2. Create a new branch
3. Make your changes
4. Run tests
5. Commit changes
6. Push branch
7. Open a Pull Request
```

## Branch Naming

```text
feat/description
fix/description
docs/description
test/description
```

Please read:
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md

before contributing.

---

# GSSoC 2026

DevPath welcomes contributions from participants of GirlScript Summer of Code 2026.

Before working on an issue:
1. Comment on the issue
2. Wait for assignment/confirmation
3. Fork the repository
4. Create a feature branch

---

# Documentation

| File | Purpose |
|------|---------|
| README.md | Project overview |
| CONTRIBUTING.md | Contribution guidelines |
| CODE_OF_CONDUCT.md | Community guidelines |
| docs/architecture.md | System architecture |
| docs/project_overview.md | Project details |

---

# License

This project is licensed under the MIT License.

See:

```text
LICENSE
```

for more information.

---

<div align="center">

Built for learning and open-source collaboration.

</div>
