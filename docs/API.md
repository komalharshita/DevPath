# DevPath API Documentation

This document describes the API endpoints exposed by the DevPath backend. The endpoints handle project recommendation queries, starter code retrieval, and file downloads.

## Table of Contents
1. [Authentication and Security (CSRF)](#1-authentication-and-security-csrf)
2. [Caching Policy](#2-caching-policy)
3. [Endpoints Overview](#3-endpoints-overview)
   - [POST /api/recommend](#post-apirecommend)
   - [GET /project/<project_id>/code](#get-projectproject_idcode)
   - [GET /project/<project_id>/download](#get-projectproject_iddownload)
4. [Error Codes and Handling](#4-error-codes-and-handling)

---

## 1. Authentication and Security (CSRF)

All state-mutating requests (such as `POST`, `PUT`, `DELETE`) are protected by a lightweight, zero-dependency, native CSRF protection mechanism.

*   **CSRF Cookie**: Visiting any GET endpoint (e.g., `/`) automatically sets a `csrf_token` cookie in the client's browser.
*   **Header Requirement**: For `POST` requests, the client must retrieve the `csrf_token` cookie value and submit it in the request headers as `X-CSRF-Token`.
*   **Rejection**: Requests without a valid `X-CSRF-Token` header will return a `400 Bad Request` with `{"error": "CSRF token missing or invalid."}`.

---

## 2. Caching Policy

To enhance backend performance and reduce disk I/O, static read-only routes are memoized using **Flask-Caching (SimpleCache)**.

*   **Cached Views**: `/project/<project_id>` and `/project/<project_id>/code`.
*   **Cache Duration**: `600 seconds` (10 minutes).
*   **Eviction**: Cache is automatically cleared when the application restarts.

---

## 3. Endpoints Overview

### POST /api/recommend

Submits developer inputs and returns a list of up to three matching coding projects, sorted by relevance score.

*   **Content-Type**: `application/json`
*   **Headers**: 
    *   `X-CSRF-Token`: `<token_value>` (Required)
*   **Request Body Parameters**:
    *   `skills` (string, required): A comma-separated list of programming skills (e.g., `"Python, JavaScript"`).
    *   `level` (string, required): Experience level, one of: `"Beginner"`, `"Intermediate"`, `"Advanced"`.
    *   `interest` (string, required): Domain of interest, one of: `"Web"`, `"Data"`, `"Education"`, `"Automation"`, `"Games"`.
    *   `time` (string, required): Commitable time limit, one of: `"Low"`, `"Medium"`, `"High"`.

#### Example Request
```http
POST /api/recommend HTTP/1.1
Host: localhost:5000
Content-Type: application/json
X-CSRF-Token: a1b2c3d4e5f6...

{
  "skills": "Python, SQL",
  "level": "Beginner",
  "interest": "Data",
  "time": "Low"
}
```

#### Example Successful Response (`200 OK`)
```json
{
  "projects": [
    {
      "id": 1,
      "title": "Expense Tracker CLI",
      "description": "A terminal application to record daily transactions and analyze monthly spending.",
      "skills": ["Python"],
      "level": "Beginner",
      "interest": "Data",
      "time": "Low",
      "tech_stack": ["Python 3.x", "CSV Module"],
      "features": [
        "Interactive command menu",
        "Add transactions with category and date",
        "Export and parse summary reports in CSV format"
      ]
    }
  ]
}
```

#### Example No-Match Response (`200 OK`)
```json
{
  "projects": [],
  "message": "No projects matched your inputs. Try different skills or broaden your interest area."
}
```

---

### GET /project/\<project_id\>/code

Fetches the starter template file content and filename for inline browser display.

*   **Cache Status**: Cached (600 seconds)
*   **Parameters**:
    *   `project_id` (integer, path parameter): The ID of the requested project.

#### Example Request
```http
GET /project/1/code HTTP/1.1
Host: localhost:5000
```

#### Example Successful Response (`200 OK`)
```json
{
  "filename": "expense_tracker.py",
  "code": "# expense_tracker.py\n# Starter code template\n\nimport csv\n..."
}
```

---

### GET /project/\<project_id\>/download

Serves the starter code file as a downloadable file attachment.

*   **Cache Status**: Not Cached (Dynamic stream download)
*   **Parameters**:
    *   `project_id` (integer, path parameter): The ID of the requested project.

#### Example Request
```http
GET /project/1/download HTTP/1.1
Host: localhost:5000
```

#### Example Successful Response (`200 OK`)
*   **Headers**:
    *   `Content-Type`: `application/octet-stream`
    *   `Content-Disposition`: `attachment; filename=expense_tracker.py`
*   **Body**: Binary/text payload of the starter file template.

---

## 4. Error Codes and Handling

All API endpoints return standard HTTP status codes:

| Status Code | Description | Payload Example |
|---|---|---|
| `200 OK` | The request succeeded and returned requested data. | *Normal response dict* |
| `400 Bad Request` | Invalid inputs, missing fields, or bad JSON body. | `{"error": "Please enter at least one skill."}` |
| `401 Unauthorized` | CSRF token is invalid or expired. | `{"error": "CSRF token missing or invalid."}` |
| `404 Not Found` | Requesting a non-existent project ID. | `{"error": "Project not found."}` |
| `500 Server Error` | Unexpected backend exceptions. | *Standard HTML 500 error page* |
