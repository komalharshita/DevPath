# routes/main_routes.py
# All application routes registered as a Flask Blueprint.
# Each route is kept thin: it validates input, calls a utility function,
# and returns a response. No business logic lives here.

import os
from flask import Blueprint, render_template, request, jsonify, send_from_directory, abort

from utils.recommender import get_recommendations, validate_recommendation_inputs
from utils.data_loader import find_project_by_id, get_project_stats
from utils.file_server import read_starter_code, resolve_starter_file, get_starter_code_dir

# New Infrastructure Utilities
from utils.rate_limiter import limit_rate
from utils.kafka_producer import send_activity_event
from utils.redis_service import get_user_cached_suggestions, track_user_history

# Create the Blueprint that app.py will register
main = Blueprint("main", __name__)


@main.route("/")
@limit_rate(limit=60, period=60) # 60 requests per minute limit for homepage
def index():
    """Render the homepage with the skill input form and dynamic stats."""
    stats = get_project_stats()

    # Optional: Mocking an authenticated user ID or tracking by IP
    user_id = request.remote_addr

    # Fetch real-time personalized recommendations from Redis if available
    personalized_suggestions = get_user_cached_suggestions(user_id)

    return render_template(
        "index.html", 
        stats=stats, 
        suggestions=personalized_suggestions
    )


@main.route("/api/recommend", methods=["POST"])
@limit_rate(limit=10, period=60) # Stricter rate-limiting (10 requests/min) on heavy computation endpoint
def recommend():
    """
    Accept a JSON body with user inputs and return matching project recommendations.

    Expected JSON fields:
        skills   (str) - comma-separated list of skills
        level    (str) - Beginner | Intermediate | Advanced
        interest (str) - Web | Data | Education | Automation | Games
        time     (str) - Low | Medium | High
    """
    payload = request.get_json()

    if not payload:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    skills            = payload.get("skills", "").strip()
    level             = payload.get("level", "").strip()
    interest          = payload.get("interest", "").strip()
    time_availability = payload.get("time", "").strip()

    # Validate before running the recommendation engine
    errors = validate_recommendation_inputs(skills, level, interest, time_availability)
    if errors:
        return jsonify({"error": errors[0]}), 400

    results = get_recommendations(skills, level, interest, time_availability)

    if not results:
        return jsonify({
            "projects": [],
            "message": (
                "No projects matched your inputs. "
                "Try different skills or broaden your interest area."
            )
        }), 200

    return jsonify({"projects": results}), 200


@main.route("/project/<int:project_id>")
@limit_rate(limit=30, period=60)
def project_detail(project_id):
    """Render the full detail page for a single project."""
    project = find_project_by_id(project_id)
    if not project:
        abort(404)

    user_id = request.remote_addr  # Replace with actual user identifier if auth is active

    # 1. Asynchronously push to Kafka to register a 'view' action event without blocking UI response
    send_activity_event(user_id=user_id, project_id=project_id, event_type="view")

    # 2. Synchronously write to Redis ZSET for instant 'Recently Viewed' cache updates
    track_user_history(user_id=user_id, project_id=project_id)

    return render_template("project.html", project=project)


@main.route("/project/<int:project_id>/code")
@limit_rate(limit=40, period=60)
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
@limit_rate(limit=5, period=60) # Low rate limit on file downloads to prevent scraping/abuse
def download_code(project_id):
    """Serve the starter code file as a downloadable attachment."""
    project = find_project_by_id(project_id)
    if not project:
        abort(404)

    full_path = resolve_starter_file(project)
    if not full_path:
        abort(404)

    user_id = request.remote_addr
    # Push explicit download metric event into the Kafka stream pipeline
    send_activity_event(user_id=user_id, project_id=project_id, event_type="download")

    filename = os.path.basename(full_path)
    return send_from_directory(get_starter_code_dir(), filename, as_attachment=True)