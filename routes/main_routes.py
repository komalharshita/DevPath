# routes/main_routes.py
# All application routes registered as a Flask Blueprint.
# Each route is kept thin: it validates input, calls a utility function,
# and returns a response. No business logic lives here.

from flask import Blueprint, render_template, request, jsonify, send_from_directory, abort, make_response , redirect , session  , current_app
from dotenv import load_dotenv
import requests

from utils.recommender import get_recommendations, validate_recommendation_inputs
from utils.data_loader import find_project_by_id, load_all_projects, get_project_stats
from utils.file_server import read_starter_code, resolve_starter_file, get_starter_code_dir
import os
# Point explicitly to the parent directory where the .env file actually lives
base_dir = os.path.abspath(os.path.dirname(__file__))
# Moving up one directory level to DevPath
root_dir = os.path.dirname(base_dir) 
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)


# 3. Add this debug print right here to verify it during startup



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

    if interest_has_no_projects(interest):
        return jsonify({
            "projects": [],
            "message": "No projects are currently available for this interest area. Please check back later."
        }), 200

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

@main.route("/api/auth/github")
def github_auth():
    github_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={os.getenv('GITHUB_CLIENT_ID')}"
        "&scope=repo read:user"
        f"&redirect_uri={os.getenv('GITHUB_REDIRECT_URI')}"
    )
    return redirect(github_url)
@main.route("/auth/github/callback")
def github_callback():
    code = request.args.get("code")

    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": os.getenv("GITHUB_CLIENT_ID"),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
            "code": code,
        },
    )

    token_data = token_res.json()
    access_token = token_data.get("access_token")
    print(access_token)
    if not access_token:
        return redirect("http://localhost:5000/dashboard?github=failed")

    # This will now succeed because app.secret_key is set correctly at boot time
    session["github_token"] = access_token

    return redirect("/?github=success")
@main.route("/api/github/repos")
def github_repos():
    token = session.get("github_token")
    if not token:
        return {"error": "GitHub not connected"}, 401

    headers = {"Authorization": f"Bearer {token}"}

    # Fetch all repos
    repos_res = requests.get("https://api.github.com/user/repos", headers=headers)
    repos = repos_res.json()

    # Collect languages from each repo
    skills = set()
    for repo in repos:
        # Primary language
        if repo.get("language"):
            skills.add(repo["language"])

        # Fetch detailed languages breakdown per repo
        lang_res = requests.get(repo["languages_url"], headers=headers)
        if lang_res.status_code == 200:
            skills.update(lang_res.json().keys())

        # Fetch topics/tags on the repo
        topics_res = requests.get(
            f"https://api.github.com/repos/{repo['full_name']}/topics",
            headers={**headers, "Accept": "application/vnd.github.mercy-preview+json"}
        )
        if topics_res.status_code == 200:
            skills.update(topics_res.json().get("names", []))

    return jsonify({"skills": list(skills)}), 200

@main.route("/api/github/import", methods=["POST"])
def import_repo():
    token = session.get("github_token")
    repo_full_name = request.json.get("repo")  # example: "username/project"

    if not token:
        return {"error": "GitHub not connected"}, 401

    repo_res = requests.get(
        f"https://api.github.com/repos/{repo_full_name}",
        headers={"Authorization": f"Bearer {token}"}
    )

    return {
        "message": "Repository imported successfully",
        "repo": repo_res.json()
    }