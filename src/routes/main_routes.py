# routes/main_routes.py
# All application routes registered as a Flask Blueprint.
# Each route is kept thin: it validates input, calls a utility function,
# and returns a response. No business logic lives here.

from flask import Blueprint, render_template, request, jsonify, send_from_directory, abort, make_response, redirect, url_for, session

from utils.recommender import get_recommendations, validate_recommendation_inputs, diagnose_empty_state
from utils.data_loader import find_project_by_id, load_all_projects, get_available_levels, get_project_stats, get_available_interests
from utils.roadmap_comparer import load_all_career_roadmaps, compare_roadmaps
from utils.file_server import read_starter_code, resolve_starter_file, get_starter_code_dir
from utils.rate_limiter import rate_limit
from utils.learning_path import (
    create_learning_path,
    get_learning_path,
    update_learning_path,
    PathNotFoundError,
    PathAlreadyExistsError,
    AuthorizationError,
)
from utils.skill_progression import (
    SkillProgressionValidator,
    SkillDifficulty,
    validate_skill_progression,
)
from utils.code_review import CodeReviewManager
from config import Config
from flask import jsonify
from utils.portfolio_analyzer import analyze_portfolio
import os
from models import db, ProjectProgress

_skill_validator = SkillProgressionValidator()
_code_review_manager = CodeReviewManager()

# Interest categories that currently have no project recommendations available
NO_PROJECT_INTERESTS = {
    "machine learning/ai",
    "devops",
    "mobile",
    "artificial intelligence",
    "cloud computing",
    "mobile app development",
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
        available_interests = get_available_interests()
    except Exception as e:
        # In development, we prefer rendering a fallback homepage rather than
        # aborting entirely. Log the error and use safe defaults so UI/layout
        # checks can proceed.
        print("Warning: failed to load project stats:", e)
        stats = {"total_projects": 0, "unique_skills": 0, "beginner_friendly": 0}
        available_levels = ["Beginner", "Intermediate", "Advanced"]
        available_interests = []

    return render_template("index.html", stats=stats, available_levels=available_levels, available_interests=available_interests, config=Config)

@main.route("/contact")
def contact():
    return render_template("contact.html", config=Config)


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
@rate_limit(max_requests=10, window_seconds=60)
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
    string_fields = ("skills", "level", "interest", "time", "tech_stack")
    for field in string_fields:
        value = payload.get(field)
        if value is not None and not isinstance(value, str):
            return jsonify({"error": f"'{field}' must be a string value."}), 400

    skills            = (payload.get("skills") or "").strip()
    level             = (payload.get("level") or "").strip()
    interest          = (payload.get("interest") or "").strip()
    time_availability = (payload.get("time") or "").strip()
    tech_stack        = (payload.get("tech_stack") or "").strip()

    # Explicitly check if skills string field is empty to prevent underlying scoring engine crashes
    if not skills:
        return jsonify({"error": "Please enter at least one skill to get recommendations."}), 400

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

    recommendations_data = get_recommendations(
        skills,
        level,
        interest,
        time_availability,
        tech_stack,
        max_results=None,
    )
    results = recommendations_data.get("recommendations", [])

    if not results:
        diagnostic_message = diagnose_empty_state(skills, level, interest, time_availability)
        return jsonify({
            "projects": [],
            "message": diagnostic_message
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
        
    return render_template("project.html", project=project, config=Config, og_url=Config.get_base_url() + "/project/" + str(project_id))

@main.route("/profile")
def profile():
    from flask import session
    from models import db, User
    from utils.data_loader import find_project_by_id
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
        
    user = db.session.get(User, user_id)
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
        
    # Hydrate bookmarked projects
    bookmarked_projects = []
    for pid in user.bookmarked_projects:
        p = find_project_by_id(pid)
        if p:
            bookmarked_projects.append(p)
            
    return render_template("profile.html", user=user, bookmarked_projects=bookmarked_projects)

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
@rate_limit(max_requests=20, window_seconds=60)
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
@rate_limit(max_requests=30, window_seconds=60)
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


@main.route("/api/skill-progression/validate", methods=["POST"])
def validate_skill():
    """Validate if user can learn a skill at target difficulty level."""
    payload = request.get_json(silent=True)

    if not payload:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    user_id = (payload.get("user_id") or "").strip()
    skill_name = (payload.get("skill") or "").strip()
    target_difficulty = (payload.get("difficulty") or "").strip()

    if not user_id or not skill_name or not target_difficulty:
        return jsonify({
            "error": "user_id, skill, and difficulty are required"
        }), 400

    result = validate_skill_progression(
        user_id,
        skill_name,
        target_difficulty,
        _skill_validator
    )

    return jsonify(result), 200 if result["allowed"] else 400


@main.route("/api/skill-progression/record", methods=["POST"])
def record_skill_completion():
    """Record user completion of a skill at given difficulty level."""
    payload = request.get_json(silent=True)

    if not payload:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    user_id = (payload.get("user_id") or "").strip()
    skill_name = (payload.get("skill") or "").strip()
    difficulty = (payload.get("difficulty") or "").strip()
    assessment_score = payload.get("assessment_score")

    if not user_id or not skill_name or not difficulty:
        return jsonify({
            "error": "user_id, skill, and difficulty are required"
        }), 400

    try:
        diff_enum = SkillDifficulty[difficulty.upper()]
    except KeyError:
        return jsonify({"error": f"Invalid difficulty: {difficulty}"}), 400

    if assessment_score is not None:
        try:
            assessment_score = float(assessment_score)
            if not (0 <= assessment_score <= 100):
                return jsonify({
                    "error": "assessment_score must be between 0 and 100"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "error": "assessment_score must be a number"
            }), 400

    skill_data = _skill_validator.record_skill_completion(
        user_id,
        skill_name,
        diff_enum,
        assessment_score
    )

    return jsonify({
        "success": True,
        "user_id": user_id,
        "skill": skill_name,
        "difficulty": difficulty,
        "skill_data": skill_data
    }), 201


@main.route("/api/skill-progression/user/<user_id>")
def get_user_progression(user_id):
    """Get skill progression data for a user."""
    user_id = user_id.strip()

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    skills = _skill_validator.get_user_skills(user_id)
    proficiency = _skill_validator.calculate_overall_proficiency(user_id)

    return jsonify({
        "user_id": user_id,
        "skills": skills,
        "proficiency": proficiency
    }), 200


@main.route("/api/skill-progression/next/<user_id>/<skill>")
def get_next_skill(user_id, skill):
    """Get recommended next skill level for user to pursue."""
    user_id = user_id.strip()
    skill = skill.strip()

    if not user_id or not skill:
        return jsonify({"error": "user_id and skill are required"}), 400

    next_skill = _skill_validator.get_recommended_next_skill(user_id, skill)

    if not next_skill:
        return jsonify({
            "user_id": user_id,
            "skill": skill,
            "next_skill": None,
            "message": "No next skill level available or skill not started"
        }), 200

    return jsonify({
        "user_id": user_id,
        "skill": skill,
        "next_skill": {
            "skill": next_skill[0],
            "difficulty": next_skill[1].name
        }
    }), 200


@main.route("/api/code-review/submit", methods=["POST"])
def submit_code_for_review():
    """Submit code for expert review."""
    payload = request.get_json(silent=True)

    if not payload:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    submission_id = (payload.get("submission_id") or "").strip()
    user_id = (payload.get("user_id") or "").strip()
    project_id = payload.get("project_id")
    code = (payload.get("code") or "").strip()
    language = (payload.get("language") or "").strip()
    description = (payload.get("description") or "").strip()

    if not all([submission_id, user_id, project_id, code, language]):
        return jsonify({
            "error": "submission_id, user_id, project_id, code, and language are required"
        }), 400

    try:
        submission = _code_review_manager.submit_code(
            submission_id=submission_id,
            user_id=user_id,
            project_id=int(project_id),
            code=code,
            language=language,
            description=description or None,
        )
        return jsonify({
            "success": True,
            "submission": submission
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@main.route("/api/code-review/submission/<submission_id>")
def get_submission(submission_id):
    """Get submission details."""
    submission_id = submission_id.strip()

    submission = _code_review_manager.get_submission(submission_id)
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    return jsonify({
        "success": True,
        "submission": submission
    }), 200


@main.route("/api/code-review/user/<user_id>/submissions")
def get_user_code_submissions(user_id):
    """Get all code submissions from a user."""
    user_id = user_id.strip()

    submissions = _code_review_manager.get_user_submissions(user_id)
    return jsonify({
        "user_id": user_id,
        "submissions": submissions,
        "count": len(submissions)
    }), 200


@main.route("/api/code-review/project/<int:project_id>/submissions")
def get_project_code_submissions(project_id):
    """Get all code submissions for a project."""
    submissions = _code_review_manager.get_project_submissions(project_id)
    return jsonify({
        "project_id": project_id,
        "submissions": submissions,
        "count": len(submissions)
    }), 200


@main.route("/api/code-review/start", methods=["POST"])
def start_code_review():
    """Start a code review session."""
    payload = request.get_json(silent=True)

    if not payload:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    submission_id = (payload.get("submission_id") or "").strip()
    reviewer_id = (payload.get("reviewer_id") or "").strip()

    if not submission_id or not reviewer_id:
        return jsonify({
            "error": "submission_id and reviewer_id are required"
        }), 400

    try:
        review = _code_review_manager.start_review(
            submission_id=submission_id,
            reviewer_id=reviewer_id,
        )
        return jsonify({
            "success": True,
            "review": review
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@main.route("/api/code-review/<review_id>/comment", methods=["POST"])
def add_review_comment(review_id):
    """Add feedback comment to a review."""
    payload = request.get_json(silent=True)

    if not payload:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    line_number = payload.get("line_number")
    code_snippet = (payload.get("code_snippet") or "").strip()
    feedback = (payload.get("feedback") or "").strip()
    severity = (payload.get("severity") or "info").strip()

    if line_number is None or not code_snippet or not feedback:
        return jsonify({
            "error": "line_number, code_snippet, and feedback are required"
        }), 400

    try:
        comment = _code_review_manager.add_feedback_comment(
            review_id=review_id,
            line_number=int(line_number),
            code_snippet=code_snippet,
            feedback=feedback,
            severity=severity,
        )
        return jsonify({
            "success": True,
            "comment": comment
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@main.route("/api/code-review/<review_id>/score", methods=["POST"])
def score_review_category(review_id):
    """Score a code quality category in a review."""
    payload = request.get_json(silent=True)

    if not payload:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    category = (payload.get("category") or "").strip()
    score = payload.get("score")
    feedback = (payload.get("feedback") or "").strip()

    if not category or score is None:
        return jsonify({
            "error": "category and score are required"
        }), 400

    try:
        score = float(score)
        category_score = _code_review_manager.score_category(
            review_id=review_id,
            category=category,
            score=score,
            feedback=feedback or "",
        )
        return jsonify({
            "success": True,
            "category_score": category_score
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@main.route("/api/code-review/<review_id>/complete", methods=["POST"])
def complete_code_review(review_id):
    """Complete a code review."""
    payload = request.get_json(silent=True)

    if not payload:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    summary = (payload.get("summary") or "").strip()
    recommend_changes = payload.get("recommend_changes", False)

    if not summary:
        return jsonify({"error": "summary is required"}), 400

    try:
        completed = _code_review_manager.complete_review(
            review_id=review_id,
            summary=summary,
            recommend_changes=bool(recommend_changes),
        )
        return jsonify({
            "success": True,
            "review": completed
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@main.route("/api/code-review/<review_id>/comments")
def get_review_feedback(review_id):
    """Get all feedback comments for a review."""
    review_id = review_id.strip()

    comments = _code_review_manager.get_review_comments(review_id)
    return jsonify({
        "review_id": review_id,
        "comments": comments,
        "count": len(comments)
    }), 200


@main.route("/api/code-review/submission/<submission_id>/quality")
def get_code_quality_score(submission_id):
    """Get code quality score for a submission."""
    submission_id = submission_id.strip()

    score_data = _code_review_manager.get_code_quality_score(submission_id)
    return jsonify(score_data), 200


@main.route("/api/code-review/submission/<submission_id>/recommendations")
def get_code_recommendations(submission_id):
    """Get improvement recommendations for a submission."""
    submission_id = submission_id.strip()

    recommendations = _code_review_manager.get_improvement_recommendations(
        submission_id
    )
    return jsonify({
        "submission_id": submission_id,
        "recommendations": recommendations,
        "count": len(recommendations)
    }), 200


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
@rate_limit(max_requests=10, window_seconds=60)
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

    if len(request.data) > _MAX_DATA_BYTES:
        return jsonify({
            "error": f"Payload too large. Maximum allowed size is {_MAX_DATA_BYTES // 1024} KB."
        }), 400

    try:
        create_learning_path(path_id, token, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except PathAlreadyExistsError:
        return jsonify({"error": "A learning path with this ID already exists."}), 409

    return jsonify({"path_id": path_id, "message": "Learning path created."}), 201


@main.route("/api/learning-path/<path_id>", methods=["GET"])
@rate_limit(max_requests=20, window_seconds=60)
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
@rate_limit(max_requests=10, window_seconds=60)
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

    if len(request.data) > _MAX_DATA_BYTES:
        return jsonify({
            "error": f"Payload too large. Maximum allowed size is {_MAX_DATA_BYTES // 1024} KB."
        }), 400

    try:
        update_learning_path(path_id, token, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except PathNotFoundError:
        return jsonify({"error": "Learning path not found."}), 404
    except AuthorizationError:
        return jsonify({"error": "Forbidden: invalid token for this path."}), 403

    return jsonify({"path_id": path_id, "message": "Learning path updated."}), 200

@main.route("/api/project/<int:project_id>/progress", methods=["GET"])
def get_project_progress(project_id):
    """Return the user's roadmap progress for a specific project."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    progress = ProjectProgress.query.filter_by(user_id=user_id, project_id=project_id).first()
    completed_steps = progress.completed_steps if progress else []
    return jsonify({"completed_steps": completed_steps}), 200

@main.route("/api/project/<int:project_id>/progress", methods=["POST"])
def update_project_progress(project_id):
    """Update the user's roadmap progress for a specific project."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload.get("completed_steps"), list):
        return jsonify({"error": "Invalid payload. Expected 'completed_steps' array."}), 400

    completed_steps = payload["completed_steps"]

    progress = ProjectProgress.query.filter_by(user_id=user_id, project_id=project_id).first()
    if progress:
        progress.completed_steps = completed_steps
    else:
        progress = ProjectProgress(
            user_id=user_id,
            project_id=project_id,
            completed_steps=completed_steps
        )
        db.session.add(progress)

    db.session.commit()
    return jsonify({"message": "Progress saved successfully"}), 200
@main.route("/api/portfolio-analysis", methods=["POST"])
def portfolio_analysis():
    """
    Analyze the user's completed projects and return
    portfolio diversity information.
    """

    payload = request.get_json(silent=True)

    if payload is None:
        return jsonify({"error": "Invalid JSON payload"}), 400

    print(payload)

    completed_ids = payload.get("completed_projects", [])

    if not isinstance(completed_ids, list):
        return jsonify({"error": "'completed_projects' must be a list"}), 400

    all_projects = load_all_projects()

    completed_projects = [
        project
        for project in all_projects
        if project["id"] in completed_ids
    ]

    result = analyze_portfolio(completed_projects)

    return jsonify(result), 200

# Constants for learning velocity recommendations
VELOCITY_SLOW_THRESHOLD = 1.2
VELOCITY_FAST_THRESHOLD = 0.8


@main.route("/api/learning-path/<path_id>/analytics", methods=["GET"])
def get_path_analytics(path_id):
    """
    Calculate time analytics and velocity for a specific learning path.
    
    Requires X-Learning-Path-Token header for authorization.
    Expected data structure in path['progress']:
    {
        "project_id": {"completed": bool, "actual_hours": float}
    }
    """
    token = _extract_token(request)
    if not token:
        return jsonify({"error": f"'{_TOKEN_HEADER}' header is required."}), 400

    try:
        path_data = get_learning_path(path_id, token)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except PathNotFoundError:
        return jsonify({"error": "Learning path not found."}), 404
    except AuthorizationError:
        return jsonify({"error": "Forbidden: invalid token for this path."}), 403

    # Analytics Calculation
    progress = path_data.get("progress", {})
    total_est = 0
    total_act = 0
    comp_est = 0
    comp_act = 0

    for pid_str, stats in progress.items():
        try:
            project = find_project_by_id(int(pid_str))
            if not project:
                continue
            
            est = project.get("estimated_hours", 0)
            act = stats.get("actual_hours", 0)
            
            total_est += est
            total_act += act
            
            if stats.get("completed"):
                comp_est += est
                comp_act += act
        except (ValueError, TypeError):
            continue

    # Learning Velocity: ratio of Actual Time / Estimated Time
    # > 1.0 means slower than estimate, < 1.0 means faster than estimate
    velocity = round(comp_act / comp_est, 2) if comp_est > 0 else 1.0
    
    remaining_est = total_est - comp_est
    predicted_remaining = round(remaining_est * velocity, 1)
    
    # Recommendations based on velocity
    recommendation = "You're matching the estimates perfectly!" # Default recommendation
    if velocity > VELOCITY_SLOW_THRESHOLD:
        recommendation = "You're taking more time than estimated. Consider breaking tasks into smaller chunks."
    elif velocity < VELOCITY_FAST_THRESHOLD:
        recommendation = "You're moving fast! You might want to try a higher difficulty level next."

    return jsonify({
        "path_id": path_id,
        "total_estimated_hours": total_est,
        "total_actual_hours_spent": total_act,
        "learning_velocity": velocity,
        "completion_percentage": round((comp_est / total_est * 100), 1) if total_est > 0 else 0,
        "predicted_hours_remaining": predicted_remaining,
        "recommendation": recommendation
    }), 200
