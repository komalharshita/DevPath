# routes/main_routes.py
# All application routes registered as a Flask Blueprint.
# Each route is kept thin: it validates input, calls a utility function,
# and returns a response. No business logic lives here.

from flask import Blueprint, render_template, request, jsonify, send_from_directory, abort, make_response, session

from utils.recommender import get_recommendations, validate_recommendation_inputs
from utils.data_loader import find_project_by_id, load_all_projects, get_project_stats
from utils.file_server import read_starter_code, resolve_starter_file, get_starter_code_dir
import os

# Create the Blueprint that app.py will register
main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Render the homepage with the skill input form and dynamic stats."""
    stats = get_project_stats()
    
    # Load recently viewed projects from Flask session
    recently_viewed_ids = session.get("recently_viewed", [])
    recently_viewed_projects = []
    for pid in recently_viewed_ids:
        proj = find_project_by_id(pid)
        if proj:
            recently_viewed_projects.append(proj)
            
    return render_template("index.html", stats=stats, recently_viewed_projects=recently_viewed_projects)

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


@main.route("/project/<int:project_id>")
def project_detail(project_id):
    """Render the full detail page for a single project."""
    project = find_project_by_id(project_id)
    if not project:
        abort(404)
        
    # Track recently viewed projects (limit to 5 unique IDs, most-recent-first)
    recently_viewed = session.get("recently_viewed", [])
    
    # Defensively convert and filter valid integer IDs to avoid ValueError or mixed types
    clean_ids = []
    for x in recently_viewed:
        try:
            clean_ids.append(int(x))
        except (ValueError, TypeError):
            continue
            
    try:
        pid = int(project_id)
    except (ValueError, TypeError):
        pid = None
        
    if pid is not None:
        if pid in clean_ids:
            clean_ids.remove(pid)
        clean_ids.insert(0, pid)
        session["recently_viewed"] = clean_ids[:5]
    
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


@main.route("/sitemap.xml")
def sitemap():
    """
    Generate and return a sitemap.xml for search engine indexing.
    Includes the homepage and all individual project detail pages.
    """
    base = request.host_url.rstrip("/")
    projects = load_all_projects()

    urls = [f"<url><loc>{base}/</loc></url>"]
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
