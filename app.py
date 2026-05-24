# app.py
# Application entry point for DevPath.
#
# Responsibilities:
#   - Create the Flask app instance
#   - Register the main Blueprint from routes/
#   - Register error handlers
#   - Start the development server when run directly
#
# Business logic, recommendation scoring, and data loading all live in
# the utils/ and routes/ packages, not here.

import os
import secrets
from flask import Flask, render_template, request, session, jsonify
from routes.main_routes import main
from extensions import cache

app = Flask(__name__)

# Enforce secure configuration parameters
app.secret_key = os.environ.get("SECRET_KEY", "devpath-insecure-flask-secret-key-12345")

# Initialize Flask-Caching using local in-memory SimpleCache
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300
cache.init_app(app)

# ---- CSRF Protection Middleware ----

@app.before_request
def csrf_protect():
    """Lightweight, zero-dependency CSRF token verification middleware."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    
    # Bypass CSRF checks in test client environment
    if app.config.get("TESTING"):
        return

    if request.method == "POST":
        token = request.headers.get("X-CSRF-Token")
        session_token = session.get("csrf_token")
        if not session_token or not token or not secrets.compare_digest(session_token, token):
            return jsonify({"error": "CSRF token missing or invalid."}), 400

@app.after_request
def set_csrf_cookie(response):
    """Automatically append CSRF token value in the cookie headers."""
    if "csrf_token" in session:
        response.set_cookie("csrf_token", session["csrf_token"], samesite="Lax")
    return response

# Register all routes defined in the main Blueprint
app.register_blueprint(main)


# ---- Error handlers ----

@app.errorhandler(404)
def page_not_found(error):
    """Render a friendly 404 page instead of the raw Flask error."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Render a friendly 500 page for unexpected server errors."""
    return render_template("500.html"), 500


if __name__ == "__main__":
    # Control debug mode dynamically from the environment, defaulting to False in production
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)
