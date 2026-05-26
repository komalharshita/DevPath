import logging
import json
import time
from flask import Flask, render_template, request, g
from routes.main_routes import main
from utils.logging_config import setup_logging

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

app = Flask(__name__)

# Initialize application-wide JSON logging
setup_logging(app)
logger = logging.getLogger(__name__)

# Register all routes defined in the main Blueprint
app.register_blueprint(main)

@app.before_request
def start_timer():
    """Record start time for computing request latency."""
    g.start_time = time.time()

@app.after_request
def log_request_completed(response):
    """Log completed request with JSON structured metadata."""
    if request.path.startswith("/static/") or request.path == "/favicon.ico":
        return response
        
    duration_ms = 0.0
    if hasattr(g, 'start_time'):
        duration_ms = (time.time() - g.start_time) * 1000.0
        
    logger.info(
        "request_completed",
        extra={
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2)
        }
    )
    return response

@app.after_request
def add_security_headers(response):
    """Add basic security headers to all responses."""
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=()"
    )
    return response

# ---- Error handlers ----

@app.errorhandler(404)
def page_not_found(error):
    """Render a friendly 404 page instead of the raw Flask error."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Render a friendly 500 page for unexpected server errors."""
    return render_template("500.html"), 500

@app.errorhandler(405)
def method_not_allowed(error):
    """Render a friendly 405 page when the wrong HTTP method is used."""
    return render_template("405.html"), 405


if __name__ == "__main__":
    # debug=True is only for local development.
    # Never run with debug=True in a production deployment.
    app.run(debug=True)
