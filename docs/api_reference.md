# DevPath REST API Reference

This document provides verified, complete technical documentation for the DevPath HTTP APIs.

All JSON endpoints accept and return `application/json; charset=utf-8` unless specified otherwise.

---

## Table of Contents

- [1. Recommendation & Project Discovery API](#1-recommendation--project-discovery-api)
  - [POST /api/recommend](#post-apirecommend)
  - [GET /api/search](#get-apisearch)
  - [GET /api/project/{id}/resources](#get-apiprojectidresources)
  - [GET /project/{id}/code](#get-projectidcode)
  - [GET /project/{id}/download](#get-projectiddownload)
- [2. Career Roadmaps & Comparison API](#2-career-roadmaps--comparison-api)
  - [GET /api/roadmaps](#get-apiroadmaps)
  - [GET /api/compare](#get-apicompare)
- [3. User Progress & Portfolio Analytics API](#3-user-progress--portfolio-analytics-api)
  - [GET /api/project/{id}/progress](#get-apiprojectidprogress)
  - [POST /api/project/{id}/progress](#post-apiprojectidprogress)
  - [GET /api/user-progress](#get-apiuser-progress)
  - [POST /api/user-progress](#post-apiuser-progress)
  - [POST /api/portfolio-analysis](#post-apiportfolio-analysis)
  - [GET /api/leaderboard](#get-apileaderboard)
- [4. Skill Progression Engine API](#4-skill-progression-engine-api)
  - [POST /api/skill-progression/validate](#post-apiskill-progressionvalidate)
  - [POST /api/skill-progression/record](#post-apiskill-progressionrecord)
  - [GET /api/skill-progression/user/{user_id}](#get-apiskill-progressionuseruser_id)
  - [GET /api/skill-progression/next/{user_id}/{skill}](#get-apiskill-progressionnextuser_idskill)
- [5. Code Review & Mentorship API](#5-code-review--mentorship-api)
  - [POST /api/code-review/submit](#post-apicode-reviewsubmit)
  - [GET /api/code-review/submission/{submission_id}](#get-apicode-reviewsubmissionsubmission_id)
  - [GET /api/code-review/user/{user_id}/submissions](#get-apicode-reviewuseruser_idsubmissions)
  - [GET /api/code-review/project/{project_id}/submissions](#get-apicode-reviewprojectproject_idsubmissions)
  - [POST /api/code-review/start](#post-apicode-reviewstart)
  - [POST /api/code-review/{review_id}/comment](#post-apicode-reviewreview_idcomment)
  - [POST /api/code-review/{review_id}/score](#post-apicode-reviewreview_idscore)
  - [POST /api/code-review/{review_id}/complete](#post-apicode-reviewreview_idcomplete)
- [6. Personalized Learning Path API](#6-personalized-learning-path-api)
  - [POST /api/learning-path/{path_id}](#post-apilearning-pathpath_id)
  - [GET /api/learning-path/{path_id}](#get-apilearning-pathpath_id)
  - [PUT /api/learning-path/{path_id}](#put-apilearning-pathpath_id)
  - [GET /api/learning-path/{path_id}/analytics](#get-apilearning-pathpath_idanalytics)
- [7. GitHub Integration & Repository Export](#7-github-integration--repository-export)
  - [POST /project/{id}/export_github](#post-projectidexport_github)
  - [GET /api/github/login](#get-apigithublogin)
  - [GET /api/github/callback](#get-apigithubcallback)
- [8. System Health & SEO Endpoints](#8-system-health--seo-endpoints)
  - [GET /health](#get-health)
  - [GET /sitemap.xml](#get-sitemapxml)
  - [GET /robots.txt](#get-robotstxt)

---

## 1. Recommendation & Project Discovery API

### `POST /api/recommend`

Generates weighted, personalized project recommendations based on the user's skill set, experience level, domain interests, and time availability.

- **Authentication**: None
- **Content-Type**: `application/json`

#### Request Body
```json
{
  "skills": ["Python", "Flask"],
  "level": "Beginner",
  "interest": "Web Development",
  "time": "Low"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `skills` | `Array<string>` or `string` | Yes | List of user skills or comma-separated string (e.g. `"Python, Flask"`) |
| `level` | `string` | Yes | Experience level: `"Beginner"`, `"Intermediate"`, or `"Advanced"` |
| `interest` | `string` or `Array<string>` | Yes | Domain of interest (e.g. `"Web Development"`, `"Data Science"`, `"AI"`) |
| `time` | `string` | Yes | Time commitment: `"Low"` (<5 hrs), `"Medium"` (5-15 hrs), `"High"` (>15 hrs) |

#### Response `200 OK`
```json
{
  "projects": [
    {
      "id": 1,
      "title": "Weather Dashboard",
      "level": "Beginner",
      "interest": "Web Development",
      "time": "Low",
      "description": "Build a clean weather forecasting web app using OpenWeather API.",
      "skills": ["HTML", "CSS", "JavaScript", "Fetch API"],
      "features": ["Live city search", "5-day forecast cards"],
      "tech_stack": ["HTML5", "CSS3", "JavaScript"],
      "roadmap": ["1. Set up basic HTML structure", "2. Fetch weather data"],
      "resources": [
        {"title": "MDN Fetch API", "url": "https://developer.mozilla.org"}
      ],
      "starter_code": "weather_app.html",
      "score": 12.0
    }
  ]
}
```

#### Error Responses
- `400 Bad Request`: `{ "error": "All fields (skills, level, interest, time) are required." }`

---

### `GET /api/search`

Performs instant case-insensitive search across projects by title, description, skills, and tech stack.

- **Query Parameters**:
  - `q` (string, required): Search query string (e.g. `flask`).

#### Response `200 OK`
```json
[
  {
    "id": 4,
    "title": "REST API with Flask",
    "description": "Build a structured CRUD REST API using Flask and SQLite.",
    "skills": ["Python", "Flask", "SQLite"],
    "level": "Intermediate",
    "interest": "Backend",
    "time": "Medium"
  }
]
```

---

### `GET /api/project/{id}/resources`

Returns curated learning resources and external reference tutorials for a project.

#### Response `200 OK`
```json
{
  "project_id": 1,
  "resources": [
    {
      "title": "MDN Fetch API Guide",
      "url": "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API"
    }
  ]
}
```

---

### `GET /project/{id}/code`

Fetches starter code file contents for rendering in the client-side code preview modal.

#### Response `200 OK`
```json
{
  "filename": "weather_app.html",
  "code": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>...\n</html>"
}
```

#### Error Responses
- `404 Not Found`: `{ "error": "Project or starter code not found" }`

---

### `GET /project/{id}/download`

Downloads the project starter boilerplate as a file attachment.

- **Response Header**: `Content-Disposition: attachment; filename="<filename>"`
- **Response Content**: Raw file stream.

---

## 2. Career Roadmaps & Comparison API

### `GET /api/roadmaps`

Returns all structured career roadmaps as a direct JSON array.

#### Response `200 OK`
```json
[
  {
    "id": "frontend",
    "title": "Frontend Developer",
    "description": "Master building responsive, accessible web interfaces.",
    "duration_weeks": 12,
    "difficulty_score": 3,
    "skills": ["HTML", "CSS", "JavaScript", "Git", "React"],
    "topics": ["Responsive Design", "DOM Manipulation", "State Management"],
    "career_opportunities": ["Junior Frontend Developer", "UI Engineer"]
  },
  {
    "id": "backend",
    "title": "Backend Developer",
    "description": "Design secure APIs, business logic, and databases.",
    "duration_weeks": 14,
    "difficulty_score": 4,
    "skills": ["Python", "SQL", "Git", "REST APIs", "Docker"],
    "topics": ["Database Design", "Authentication", "Server Architecture"],
    "career_opportunities": ["Backend Engineer", "API Developer"]
  }
]
```

---

### `GET /api/compare`

Compares two career roadmaps side-by-side and computes overlapping vs. unique skills, topics, and duration metrics.

- **Query Parameters**:
  - `a` (string, required): First roadmap ID (e.g. `frontend`).
  - `b` (string, required): Second roadmap ID (e.g. `backend`).

#### Response `200 OK`
```json
{
  "roadmap_a": {
    "id": "frontend",
    "title": "Frontend Developer",
    "duration_weeks": 12,
    "difficulty_score": 3,
    "skills": ["HTML", "CSS", "JavaScript", "Git"],
    "topics": ["Responsive Design", "DOM Manipulation"]
  },
  "roadmap_b": {
    "id": "backend",
    "title": "Backend Developer",
    "duration_weeks": 14,
    "difficulty_score": 4,
    "skills": ["Python", "SQL", "Git"],
    "topics": ["Database Design", "Authentication"]
  },
  "overlapping_skills": ["Git"],
  "unique_skills_a": ["HTML", "CSS", "JavaScript"],
  "unique_skills_b": ["Python", "SQL"],
  "overlapping_topics": [],
  "unique_topics_a": ["Responsive Design", "DOM Manipulation"],
  "unique_topics_b": ["Database Design", "Authentication"],
  "overlapping_careers": [],
  "unique_careers_a": ["Junior Frontend Developer"],
  "unique_careers_b": ["Backend Engineer"],
  "summary": {
    "shared_skills_count": 1,
    "shared_topics_count": 0,
    "total_unique_skills": 5
  },
  "metrics": {
    "duration_weeks": { "a": 12, "b": 14, "max": 14 },
    "difficulty_score": { "a": 3, "b": 4, "max": 5 },
    "topics_count": { "a": 2, "b": 2 },
    "skills_count": { "a": 4, "b": 3 },
    "career_count": { "a": 1, "b": 1 }
  }
}
```

#### Error Responses
- `400 Bad Request`: `{ "error": "Both 'a' and 'b' query parameters are required." }`
- `404 Not Found`: `{ "error": "One or both roadmap IDs were not found." }`

---

## 3. User Progress & Portfolio Analytics API

### `GET /api/project/{id}/progress`

Returns the authenticated user's completed roadmap step indexes for a project.

- **Authentication**: Required (`session['user_id']`)

#### Response `200 OK`
```json
{
  "completed_steps": [0, 1, 2]
}
```

#### Error Responses
- `401 Unauthorized`: `{ "error": "Unauthorized" }`

---

### `POST /api/project/{id}/progress`

Saves or updates completed roadmap steps for a project.

- **Authentication**: Required (`session['user_id']`)
- **Content-Type**: `application/json`

#### Request Body
```json
{
  "completed_steps": [0, 1, 2, 3]
}
```

#### Response `200 OK`
```json
{
  "message": "Progress saved successfully"
}
```

---

### `GET /api/user-progress`

Fetches user gamification progress, challenge badges, and quiz scores.

- **Authentication**: Required (`session['user_id']`)

#### Response `200 OK`
```json
{
  "data": {
    "quiz_scores": { "python": 90 },
    "completed_challenges": ["challenge-1"]
  }
}
```

---

### `POST /api/user-progress`

Saves user gamification progress payload.

- **Authentication**: Required (`session['user_id']`)
- **Request Body**:
```json
{
  "data": {
    "quiz_scores": { "python": 90 },
    "completed_challenges": ["challenge-1", "challenge-2"]
  }
}
```

#### Response `200 OK`
```json
{
  "message": "Progress updated successfully"
}
```

---

### `POST /api/portfolio-analysis`

Evaluates completed project diversity and provides portfolio health scoring.

- **Content-Type**: `application/json`

#### Request Body
```json
{
  "completed_projects": [1, 3]
}
```

#### Response `200 OK`
```json
{
  "score": 75,
  "tier": "good",
  "label": "Good progress, room to grow",
  "categories": [
    { "name": "Frontend", "percentage": 50 },
    { "name": "Backend", "percentage": 50 }
  ],
  "recommendations": [
    "Consider building a project using databases or data visualization to round out your skills."
  ]
}
```

---

### `GET /api/leaderboard`

Retrieves public leaderboard ranking of active community contributors.

#### Response `200 OK`
```json
{
  "leaderboard": [
    { "username": "developer1", "projects_completed": 8, "badge": "Master" }
  ]
}
```

---

## 4. Skill Progression Engine API

### `POST /api/skill-progression/validate`

Validates whether a user satisfies prerequisites before attempting a higher skill tier.

- **Authentication**: Required
- **Request Body**:
```json
{
  "skill": "Python",
  "difficulty": "intermediate"
}
```

#### Response `200 OK`
```json
{
  "allowed": true,
  "skill": "Python",
  "target_difficulty": "INTERMEDIATE",
  "reason": "Prerequisites satisfied."
}
```

---

### `POST /api/skill-progression/record`

Records successful completion of a skill difficulty level with optional score.

- **Authentication**: Required
- **Request Body**:
```json
{
  "skill": "Python",
  "difficulty": "beginner",
  "assessment_score": 85.0
}
```

#### Response `201 Created`
```json
{
  "success": true,
  "user_id": 1,
  "skill": "Python",
  "difficulty": "beginner",
  "skill_data": {
    "level": "BEGINNER",
    "score": 85.0,
    "completed_at": "2026-09-05T12:00:00"
  }
}
```

---

### `GET /api/skill-progression/user/{user_id}`

Fetches overall skill progression profile and proficiency score for a user.

- **Authentication**: Required (Matches `{user_id}`)

#### Response `200 OK`
```json
{
  "user_id": "1",
  "skills": {
    "Python": { "level": "BEGINNER", "score": 85.0 }
  },
  "proficiency": 65.0
}
```

---

### `GET /api/skill-progression/next/{user_id}/{skill}`

Returns the recommended next difficulty level to pursue for a given skill.

- **Authentication**: Required (Matches `{user_id}`)

#### Response `200 OK`
```json
{
  "user_id": "1",
  "skill": "Python",
  "next_skill": {
    "skill": "Python",
    "difficulty": "INTERMEDIATE"
  }
}
```

---

## 5. Code Review & Mentorship API

### `POST /api/code-review/submit`

Submits project code for structured peer and automated review.

- **Authentication**: Required
- **Request Body**:
```json
{
  "submission_id": "sub_101",
  "project_id": 1,
  "code": "def fetch_weather(): pass",
  "language": "python",
  "description": "Initial working prototype"
}
```

#### Response `201 Created`
```json
{
  "success": true,
  "submission": {
    "submission_id": "sub_101",
    "user_id": 1,
    "project_id": 1,
    "language": "python",
    "status": "pending_review"
  }
}
```

---

### `GET /api/code-review/submission/{submission_id}`

Fetches code submission status and review comments.

- **Authentication**: Required

#### Response `200 OK`
```json
{
  "success": true,
  "submission": {
    "submission_id": "sub_101",
    "status": "in_review",
    "code": "def fetch_weather(): pass"
  }
}
```

---

### `GET /api/code-review/user/{user_id}/submissions`

Returns all code submissions submitted by a specific user.

- **Authentication**: Required (Matches `{user_id}`)

#### Response `200 OK`
```json
{
  "user_id": "1",
  "submissions": [ ... ],
  "count": 1
}
```

---

### `GET /api/code-review/project/{project_id}/submissions`

Retrieves all code review submissions tied to a specific catalog project.

- **Authentication**: Required

#### Response `200 OK`
```json
{
  "project_id": 1,
  "submissions": [ ... ],
  "count": 2
}
```

---

### `POST /api/code-review/start`

Initiates an active review session for a pending submission.

- **Authentication**: Required
- **Request Body**:
```json
{
  "submission_id": "sub_101",
  "reviewer_id": "reviewer_5"
}
```

#### Response `200 OK` / `201 Created`
```json
{
  "success": true,
  "review": {
    "review_id": "rev_201",
    "submission_id": "sub_101",
    "status": "in_progress"
  }
}
```

---

### `POST /api/code-review/{review_id}/comment`

Adds line-level or general feedback to a review session.

- **Request Body**:
```json
{
  "comment": "Consider handling network timeout errors gracefully.",
  "line_number": 14
}
```

---

### `POST /api/code-review/{review_id}/score`

Submits numerical evaluation metrics for code quality, readability, and performance.

- **Request Body**:
```json
{
  "quality_score": 88,
  "readability_score": 92
}
```

---

### `POST /api/code-review/{review_id}/complete`

Marks a code review as finalized.

#### Response `200 OK`
```json
{
  "success": true,
  "message": "Review marked as complete."
}
```

---

## 6. Personalized Learning Path API

| Endpoint | Method | Description | Auth Required |
|---|---|---|---|
| `/api/learning-path/{path_id}` | `POST` | Create a new custom adaptive learning path | Yes |
| `/api/learning-path/{path_id}` | `GET` | Fetch details, milestones, and status of a learning path | No |
| `/api/learning-path/{path_id}` | `PUT` | Update active milestone progress | Yes |
| `/api/learning-path/{path_id}/analytics` | `GET` | Retrieve completion rates and velocity metrics | No |

---

## 7. GitHub Integration & Repository Export

### `POST /project/{id}/export_github`

Exports project starter code directly into a new GitHub repository on the authenticated user's GitHub profile.

- **Authentication**: Required (`session['github_token']` from OAuth login)
- **Content-Type**: `application/json`

#### Request Body
```json
{
  "repo_name": "my-weather-dashboard",
  "description": "Starter code project built with DevPath",
  "private": false
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `repo_name` | `string` | Yes | Target repository name |
| `description` | `string` | No | Optional repository description |
| `private` | `boolean` | No | Visibility flag (defaults to `false` for public repo) |

#### Response `200 OK`
```json
{
  "success": true,
  "repo_url": "https://github.com/octocat/my-weather-dashboard",
  "message": "Repository created and starter code exported successfully!"
}
```

#### Error Responses
- `401 Unauthorized`: GitHub OAuth authorization missing or expired.
- `404 Not Found`: Project template not found.
- `500 Internal Server Error`: GitHub API failure during repository creation.

---

### `GET /api/github/login`

Initiates GitHub OAuth 2.0 web application authorization flow. Redirects user to GitHub with `public_repo` scope and CSRF `state` parameter.

---

### `GET /api/github/callback`

Handles the OAuth 2.0 authorization code exchange with GitHub and persists access token in user session.

---

## 8. System Health & SEO Endpoints

### `GET /health`

Checks system status and uptime.

#### Response `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2026-09-05T12:35:00.000000"
}
```

---

### `GET /sitemap.xml`

Generates dynamic XML sitemap indexing all active projects, comparison routes, and static landing pages.

- **Response Header**: `Content-Type: application/xml`

---

### `GET /robots.txt`

Serves standard crawler permissions and sitemap pointer.

- **Response Header**: `Content-Type: text/plain`
