# routes/main_routes.py
# All application routes registered as a Flask Blueprint.
# Each route is kept thin: it validates input, calls a utility function,
# and returns a response. No business logic lives here.

from flask import Blueprint, render_template, request, jsonify, send_from_directory, abort

from utils.recommender import get_recommendations, validate_recommendation_inputs
from utils.data_loader import find_project_by_id, get_project_stats
from utils.file_server import read_starter_code, resolve_starter_file, get_starter_code_dir
from utils.search_engine import search_projects
from utils.analytics import log_search_query, get_trending_searches
import os

# Create the Blueprint that app.py will register
main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Render the homepage with the skill input form and dynamic stats."""
    stats = get_project_stats()
    return render_template("index.html", stats=stats)

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
        # Return only the first error to keep the UI message clean
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


@main.route("/api/search", methods=["GET"])
def search():
    """
    Advanced search route (GET).
    Accepts query params: q, skills, level, interest, time, tech_stack,
                         prerequisite_skills, min_hours, max_hours, sort_by
    Returns matching projects list as JSON, and logs the search query in analytics.
    """
    query_params = {
        "q": request.args.get("q", ""),
        "skills": request.args.get("skills", ""),
        "level": request.args.get("level", ""),
        "interest": request.args.get("interest", ""),
        "time": request.args.get("time", ""),
        "tech_stack": request.args.get("tech_stack", ""),
        "prerequisite_skills": request.args.get("prerequisite_skills", ""),
        "min_hours": request.args.get("min_hours", ""),
        "max_hours": request.args.get("max_hours", ""),
        "sort_by": request.args.get("sort_by", "relevance")
    }

    results = search_projects(query_params)
    
    # Log to search analytics
    q_text = query_params["q"].strip()
    log_search_query(q_text, query_params, len(results))

    return jsonify({
        "projects": results,
        "count": len(results)
    }), 200


@main.route("/api/trending", methods=["GET"])
def trending_searches():
    """
    Trending searches endpoint (GET).
    Returns a list of popular search keywords based on search history.
    """
    limit = request.args.get("limit", 5, type=int)
    trending = get_trending_searches(limit=limit)
    return jsonify({
        "trending": trending
    }), 200


@main.route("/project/<int:project_id>")
def project_detail(project_id):
    """Render the full detail page for a single project."""
    project = find_project_by_id(project_id)
    if not project:
        abort(404)
    return render_template("project.html", project=project)


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

    import os
    filename = os.path.basename(full_path)
    return send_from_directory(get_starter_code_dir(), filename, as_attachment=True)
