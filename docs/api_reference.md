# DevPath REST API Reference

This document provides complete documentation for the DevPath HTTP APIs.

All JSON endpoints accept and return `application/json; charset=utf-8` unless specified otherwise.

---

## Table of Contents

- [1. Recommendation & Discovery API](#1-recommendation--discovery-api)
  - [POST /api/recommend](#post-apirecommend)
  - [GET /api/search](#get-apisearch)
- [2. Roadmap & Comparison API](#2-roadmap--comparison-api)
  - [GET /api/roadmaps](#get-apiroadmaps)
  - [GET /api/compare](#get-apicompare)
- [3. Starter Code & Project API](#3-starter-code--project-api)
  - [GET /project/{id}/code](#get-projectidcode)
  - [GET /project/{id}/download](#get-projectiddownload)
- [4. Portfolio & Progress API](#4-portfolio--progress-api)
  - [POST /api/portfolio-analysis](#post-apiportfolio-analysis)
  - [POST /api/progress/project](#post-apiprogressproject)
- [5. GitHub Integration API](#5-github-integration-api)
  - [POST /api/github/export](#post-apigithubexport)
- [6. System & Utility Endpoints](#6-system--utility-endpoints)
  - [GET /healthz](#get-healthz)
  - [GET /sitemap.xml](#get-sitemapxml)
  - [GET /robots.txt](#get-robotstxt)

---

## 1. Recommendation & Discovery API

### `POST /api/recommend`

Generates personalized project recommendations based on submitted developer profile.

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
| `skills` | `Array<string>` or `string` | Yes | List of user skills or comma-separated string |
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
      "resources": [{"title": "MDN Fetch API", "url": "https://developer.mozilla.org"}],
      "starter_code": "weather_app.html",
      "score": 12.0
    }
  ]
}
```

#### Error Responses
- `400 Bad Request`: Missing or invalid fields.

---

### `GET /api/search`

Real-time search across all catalog projects.

- **Query Parameters**:
  - `q` (string, required): Search query string matching title, description, skills, or tech stack.

#### Example Request
```http
GET /api/search?q=flask HTTP/1.1
```

#### Response `200 OK`
```json
{
  "results": [
    {
      "id": 4,
      "title": "REST API with Flask",
      "level": "Intermediate",
      "interest": "Backend",
      "description": "Build a structured CRUD REST API using Flask and SQLite."
    }
  ]
}
```

---

## 2. Roadmap & Comparison API

### `GET /api/roadmaps`

Returns available structured career tracks and roadmap titles.

#### Response `200 OK`
```json
{
  "roadmaps": [
    {"id": "frontend", "title": "Frontend Developer"},
    {"id": "backend", "title": "Backend Developer"},
    {"id": "fullstack", "title": "Full Stack Developer"},
    {"id": "ai-ml", "title": "AI & Machine Learning Engineer"}
  ]
}
```

---

### `GET /api/compare`

Compares two roadmap paths and computes overlapping skills and milestone differences.

- **Query Parameters**:
  - `role1` (string, required): First roadmap identifier.
  - `role2` (string, required): Second roadmap identifier.

#### Response `200 OK`
```json
{
  "role1": "frontend",
  "role2": "backend",
  "shared_skills": ["Git", "HTTP/REST", "Command Line"],
  "unique_to_role1": ["CSS/SCSS", "DOM Manipulation", "React"],
  "unique_to_role2": ["SQL", "Databases", "Server Architecture"],
  "overlap_percentage": 35
}
```

---

## 3. Starter Code & Project API

### `GET /project/{id}/code`

Fetches starter code file contents for rendering in the code preview modal.

#### Response `200 OK`
```json
{
  "filename": "weather_app.html",
  "code": "<!DOCTYPE html>\n<html>\n<head>...",
  "language": "html"
}
```

#### Error Responses
- `404 Not Found`: Project or starter code template not found.

---

### `GET /project/{id}/download`

Downloads the project starter boilerplate as a file attachment.

- **Response Header**: `Content-Disposition: attachment; filename="starter_code.zip"`

---

## 4. Portfolio & Progress API

### `POST /api/portfolio-analysis`

Analyzes user-completed projects and provides a skill diversity score and suggestions.

#### Request Body
```json
{
  "completed_projects": [1, 3, 7]
}
```

#### Response `200 OK`
```json
{
  "score": 78,
  "level": "Good progress, room to grow",
  "covered_domains": ["Web Development", "Backend"],
  "recommendations": ["Explore a Data or Cloud project to round out your skills."]
}
```

---

## 5. GitHub Integration API

### `POST /api/github/export`

Exports a project roadmap and starter code directly into a new GitHub repository on the authenticated user's account.

- **Authentication**: Required (User session with GitHub OAuth token)
- **Request Body**:
```json
{
  "project_id": 1,
  "repo_name": "my-weather-dashboard",
  "is_private": true
}
```

#### Response `200 OK`
```json
{
  "success": true,
  "repo_url": "https://github.com/username/my-weather-dashboard",
  "message": "Repository created successfully!"
}
```

---

## 6. System & Utility Endpoints

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/healthz` | System health and database connectivity check | `200 OK` |
| `GET` | `/sitemap.xml` | Dynamic XML sitemap for SEO crawlers | `200 OK` (`application/xml`) |
| `GET` | `/robots.txt` | Crawler policy and sitemap pointer | `200 OK` (`text/plain`) |
