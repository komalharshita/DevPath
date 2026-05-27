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

from flask import Flask, render_template, jsonify
from routes.main_routes import main
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())

# Register all routes defined in the main Blueprint
app.register_blueprint(main)

@app.after_request
def add_security_headers(response):
    """Add basic security headers to all responses."""
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' https://fonts.googleapis.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' https://api.github.com; "
        "frame-ancestors 'none'"
    )
    return response

# ---- Error handlers ----

@app.errorhandler(404)
def page_not_found(error):
    """Render a friendly 404 page instead of the raw Flask error."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Render a friendly 500 page for unexpected server errors.
    Never expose the original exception or file paths.
    """
    return render_template("500.html"), 500

@app.errorhandler(405)
def method_not_allowed(error):
    """Render a friendly 405 page when the wrong HTTP method is used."""
    return render_template("405.html"), 405

@app.errorhandler(403)
def forbidden(error):
    """Render a friendly 403 page when access is denied."""
    return render_template("403.html"), 403


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
