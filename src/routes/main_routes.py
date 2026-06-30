# routes/main_routes.py
# All application routes registered as a Flask Blueprint.
# Each route is kept thin: it validates input, calls a utility function,
# and returns a response. No business logic lives here.

from flask import Blueprint, render_template, request, jsonify, send_from_directory, abort, make_response

from utils.recommender import get_recommendations, validate_recommendation_inputs
from utils.data_loader import find_project_by_id, load_all_projects, get_available_levels, get_project_stats
from utils.roadmap_comparer import load_all_career_roadmaps, compare_roadmaps
from utils.file_server import read_starter_code, resolve_starter_file, get_starter_code_dir
from utils.learning_path import (
    create_learning_path,
    get_learning_path,
    update_learning_path,
    PathNotFoundError,
    PathAlreadyExistsError,
    AuthorizationError,
)
from config import Config
import os
import urllib.request
import urllib.error
import json as _json
import re as _re

# Interest categories that currently have no project recommendations available
NO_PROJECT_INTERESTS = {
    "machine learning/ai",
    "devops",
    "artificial intelligence",
    "cloud computing",
}

def interest_has_no_projects(interest):
    return interest and interest.strip().lower() in NO_PROJECT_INTERESTS

# Create the Blueprint that app.py will register
main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Render the homepage with the skill input form and dynamic stats."""
    try:
        stats = get_project_stats()
        available_levels = get_available_levels()
    except Exception as e:
        # In development, we prefer rendering a fallback homepage rather than
        # aborting entirely. Log the error and use safe defaults so UI/layout
        # checks can proceed.
        print("Warning: failed to load project stats:", e)
        stats = {"total_projects": 0, "unique_skills": 0, "beginner_friendly": 0}
        available_levels = ["Beginner", "Intermediate", "Advanced"]

    return render_template("index.html", stats=stats, available_levels=available_levels, config=Config)

@main.route("/contact")
def contact():
    return render_template("contact.html")


@main.route("/compare")
def compare_page():
    """Render the career roadmap comparison page."""
    roadmaps = load_all_career_roadmaps()
    return render_template("compare.html", roadmaps=roadmaps, config=Config)


@main.route("/api/roadmaps")
def list_roadmaps():
    """Return all career roadmaps as JSON."""
    return jsonify(load_all_career_roadmaps()), 200


@main.route("/api/compare")
def compare_roadmaps_api():
    """Return a side-by-side comparison of two career roadmaps."""
    roadmap_a = (request.args.get("a") or "").strip()
    roadmap_b = (request.args.get("b") or "").strip()

    if not roadmap_a or not roadmap_b:
        return jsonify({"error": "Both 'a' and 'b' query parameters are required."}), 400

    result = compare_roadmaps(roadmap_a, roadmap_b)

    if result is None:
        return jsonify({"error": "One or both roadmap IDs were not found."}), 404

    if result.get("error"):
        return jsonify(result), 400

    return jsonify(result), 200

@main.route("/health")
def health_check():
    """
    Returns server status. Useful for uptime monitors and Docker health checks.
    """
    return jsonify({
        "status": "ok",
        "version": os.getenv("APP_VERSION", "1.0.0")
    }), 200


@main.route("/api/recommend", methods=["POST"])
def recommend():
    """
    Accept a JSON body with user inputs and return matching project recommendations.

    Expected JSON fields:
        skills   (str) - comma-separated list of skills
        level    (str) - Beginner | Intermediate | Advanced
        interest (str) - Web | Data | Education | Automation | Games
        time     (str) - Low | Medium | High
    """
    payload = request.get_json(silent=True)

    if not payload:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    # Reject non-string values (e.g. null, lists, numbers) before calling .strip()
    string_fields = ("skills", "level", "interest", "time")
    for field in string_fields:
        value = payload.get(field)
        if value is not None and not isinstance(value, str):
            return jsonify({"error": f"'{field}' must be a string value."}), 400

    skills            = (payload.get("skills") or "").strip()
    level             = (payload.get("level") or "").strip()
    interest          = (payload.get("interest") or "").strip()
    time_availability = (payload.get("time") or "").strip()

    # Validate before running the recommendation engine
    errors = validate_recommendation_inputs(skills, level, interest, time_availability)
    if errors:
        # Return only the first error to keep the UI message clean
        return jsonify({"error": errors[0]}), 400

    if interest_has_no_projects(interest):
        return jsonify({
            "projects": [],
            "message": "No projects are currently available for this interest area. Please check back later."
        }), 200

    recommendations_data = get_recommendations(skills, level, interest, time_availability)
    results = recommendations_data.get("recommendations", [])

    if not results:
        return jsonify({
            "projects": [],
            "message": (
                "No projects matched your inputs. "
                "Try different skills or broaden your interest area."
            )
        }), 200

    # Ensure all projects have IDs in the response
    projects_data = []
    for project in results:
        project_dict = dict(project)  # Convert to dict if needed
        # Make sure ID is included
        if 'id' not in project_dict:
            project_dict['id'] = project.get('id', 0)
        projects_data.append(project_dict)

    # Return main recommendations, related, and progression
    response_data = {
        "projects": projects_data,
        "related": [dict(p) for p in recommendations_data.get("related", [])],
        "progression": [
            {"project": dict(item["project"]), "gap_score": item["gap_score"]}
            for item in recommendations_data.get("progression", [])
        ]
    }

    return jsonify(response_data), 200

@main.route("/api/project/<int:project_id>/resources")
def project_resources(project_id):
    """Return the validated resource list for a project.

    Each resource is parsed from its raw "Label: URL" string format and
    returned as a structured object so the frontend can render broken
    links differently from valid ones.

    Response shape:
        {
            "project_id": 1,
            "resources": [
                {"label": "Python official docs", "url": "https://docs.python.org", "valid": true},
                {"label": "Broken link", "url": "not-a-url", "valid": false}
            ]
        }
    """
    from utils.url_validator import validate_resources

    project = find_project_by_id(project_id)
    if not project:
        return jsonify({"error": "Project not found."}), 404

    validated = validate_resources(project.get("resources", []))
    return jsonify({
        "project_id": project_id,
        "resources": validated
    }), 200

@main.route("/project/<int:project_id>")
def project_detail(project_id):
    """Render the full detail page for a single project."""
    project = find_project_by_id(project_id)
    if not project:
        abort(404)
    return render_template("project.html", project=project, config=Config)


@main.route("/project/<int:project_id>/code")
def view_code(project_id):
    """Return the starter code file contents as JSON for inline display."""
    project = find_project_by_id(project_id)
    if not project:
        return jsonify({"error": "Project not found."}), 404

    code_data = read_starter_code(project)
    if not code_data:
        return jsonify({"error": "Starter code not available for this project."}), 404

    return jsonify(code_data), 200


@main.route("/project/<int:project_id>/download")
def download_code(project_id):
    """Serve the starter code file as a downloadable attachment."""
    project = find_project_by_id(project_id)
    if not project:
        abort(404)

    full_path = resolve_starter_file(project)
    if not full_path:
        abort(404)

    filename = os.path.basename(full_path)
    file_dir = os.path.dirname(full_path)
    return send_from_directory(file_dir, filename, as_attachment=True)


@main.route("/sitemap.xml")
def sitemap():
    """
    Generate and return a sitemap.xml for search engine indexing.
    Includes the homepage and all individual project detail pages.
    """
    base = request.host_url.rstrip("/")
    projects = load_all_projects()

    urls = [f"<url><loc>{base}/</loc></url>", f"<url><loc>{base}/compare</loc></url>"]
    for p in projects:
        urls.append(f"<url><loc>{base}/project/{p['id']}</loc></url>")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(urls)}
</urlset>"""

    response = make_response(xml)
    response.headers["Content-Type"] = "application/xml"
    return response


@main.route("/robots.txt")
def robots():
    """Serve robots.txt from the static folder."""
    return send_from_directory("static", "robots.txt", mimetype="text/plain")

@main.route("/api/search")
def search_projects():
    """Return projects matching the user's search query."""

    query = request.args.get("q", "").strip().lower()

    if not query:
        return jsonify([])

    projects = load_all_projects()
    filtered_projects = []

    for project in projects:

        # Combine searchable project fields into one lowercase string
        searchable_text = " ".join([
            project.get("title", ""),
            project.get("description", ""),
            project.get("interest", ""),
            " ".join(project.get("skills", [])),
            " ".join(project.get("tech_stack", [])),
            " ".join(project.get("features", []))
        ]).lower()

        if query in searchable_text:
            filtered_projects.append(project)

    return jsonify(filtered_projects)


# ---------------------------------------------------------------------------
# Learning path API
#
# Endpoints for reading and writing a user's learning path data.  Every
# request must supply the owner token that was returned when the path was
# first created.  Requests with a missing or wrong token are rejected with
# 403 Forbidden before any data is read or modified, closing the
# cross-user exposure described in issue #736.
#
# Token transport: the X-Learning-Path-Token request header.
# Path identity:   the <path_id> URL segment (opaque, UUID-like string).
# ---------------------------------------------------------------------------

_TOKEN_HEADER = "X-Learning-Path-Token"
_MAX_DATA_BYTES = 64 * 1024  # 64 KB — guard against oversized payloads


def _extract_token(req):
    """Return the bearer token from the request header, or None if absent."""
    return req.headers.get(_TOKEN_HEADER, "").strip() or None


@main.route("/api/learning-path/<path_id>", methods=["POST"])
def create_path(path_id):
    """Create a new learning path and bind it to the supplied token.

    Request headers:
        X-Learning-Path-Token  (required) - the secret token chosen by the
                               client (should be a random UUID or similar).

    Request body (JSON):
        Any JSON object representing the initial learning-path state.

    Response 201:  {"path_id": "<path_id>", "message": "Learning path created."}
    Response 400:  malformed request body or invalid path_id / token format.
    Response 409:  a learning path with this path_id already exists.
    """
    token = _extract_token(request)
    if not token:
        return jsonify({"error": f"'{_TOKEN_HEADER}' header is required."}), 400

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    try:
        create_learning_path(path_id, token, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except PathAlreadyExistsError:
        return jsonify({"error": "A learning path with this ID already exists."}), 409

    return jsonify({"path_id": path_id, "message": "Learning path created."}), 201


@main.route("/api/learning-path/<path_id>", methods=["GET"])
def read_path(path_id):
    """Return the data payload for a learning path.

    Request headers:
        X-Learning-Path-Token  (required) - the token associated with this
                               path when it was created.

    Response 200:  {"path_id": "<path_id>", "data": { ... }}
    Response 400:  token header missing or path_id format invalid.
    Response 403:  token does not match the owner token.
    Response 404:  no learning path found for this path_id.
    """
    token = _extract_token(request)
    if not token:
        return jsonify({"error": f"'{_TOKEN_HEADER}' header is required."}), 400

    try:
        data = get_learning_path(path_id, token)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except PathNotFoundError:
        return jsonify({"error": "Learning path not found."}), 404
    except AuthorizationError:
        return jsonify({"error": "Forbidden: invalid token for this path."}), 403

    return jsonify({"path_id": path_id, "data": data}), 200


@main.route("/api/learning-path/<path_id>", methods=["PUT"])
def update_path(path_id):
    """Overwrite the data payload for an existing learning path.

    Request headers:
        X-Learning-Path-Token  (required) - the token associated with this
                               path when it was created.

    Request body (JSON):
        Any JSON object representing the new learning-path state.

    Response 200:  {"path_id": "<path_id>", "message": "Learning path updated."}
    Response 400:  malformed request body, missing token, or invalid format.
    Response 403:  token does not match the owner token.
    Response 404:  no learning path found for this path_id.
    """
    token = _extract_token(request)
    if not token:
        return jsonify({"error": f"'{_TOKEN_HEADER}' header is required."}), 400

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    try:
        update_learning_path(path_id, token, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except PathNotFoundError:
        return jsonify({"error": "Learning path not found."}), 404
    except AuthorizationError:
        return jsonify({"error": "Forbidden: invalid token for this path."}), 403

    return jsonify({"path_id": path_id, "message": "Learning path updated."}), 200


# ---------------------------------------------------------------------------
# GitHub Skills Proxy
#
# The browser cannot call api.github.com directly because our Content-Security
# Policy restricts connect-src to 'self'. This server-side proxy fetches the
# user's public repositories and returns the unique languages found, so the
# frontend only ever talks to our own origin.
# ---------------------------------------------------------------------------

_GITHUB_USERNAME_RE = _re.compile(r'^[A-Za-z0-9][A-Za-z0-9-]{0,38}$')


@main.route("/api/github-skills/<username>", methods=["GET"])
def github_skills_proxy(username):
    """Fetch public repository languages for a GitHub user and return them.

    Acts as a server-side proxy so the browser never calls api.github.com
    directly (which our own CSP would block).

    Response 200: {"languages": ["Python", "JavaScript", ...]}
    Response 400: invalid username format.
    Response 404: GitHub user not found.
    Response 502: upstream GitHub API error.
    """
    # Validate username format to prevent SSRF / abusive calls
    if not _GITHUB_USERNAME_RE.match(username):
        return jsonify({"error": "Invalid GitHub username format."}), 400

    url = (
        f"https://api.github.com/users/{username}/repos"
        "?sort=pushed&per_page=100"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "DevPath-App/1.0",
    }
    # Use a GitHub token when available to raise the rate limit from
    # 60 req/hour (unauthenticated) to 5,000 req/hour (authenticated).
    # Set the GITHUB_TOKEN environment variable to enable this.
    gh_token = os.environ.get("GITHUB_TOKEN", "")
    if gh_token:
        headers["Authorization"] = f"Bearer {gh_token}"

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            repos = _json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return jsonify({"error": "GitHub user not found."}), 404
        if exc.code == 403:
            return jsonify({
                "error": (
                    "GitHub rate limit reached. Please try again in a minute, "
                    "or ask the site admin to configure a GITHUB_TOKEN."
                )
            }), 429
        return jsonify({"error": "GitHub API error."}), 502
    except Exception:
        return jsonify({"error": "Could not reach GitHub. Please try again."}), 502

    # Collect unique non-null languages
    seen = set()
    languages = []
    for repo in repos:
        lang = repo.get("language")
        if lang and lang not in seen:
            seen.add(lang)
            languages.append(lang)

    return jsonify({"languages": languages}), 200
