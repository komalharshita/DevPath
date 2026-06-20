# app.py
# Application entry point for DevPath.
#
# Responsibilities:
#   - Create the Flask app instance
#   - Register the main Blueprint from routes/
#   - Register the global error boundary via errors/handlers.py
#   - Start the development server when run directly
#
# Business logic, recommendation scoring, and data loading all live in
# the utils/ and routes/ packages, not here.

import sys
import os

# Ensure the 'src' directory is in the python path for Vercel and root-level execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from routes.main_routes import main
from config import Config
from errors.handlers import register_error_handlers

app = Flask(__name__)

# Load config settings into Flask's internal config manager properly
app.config.from_object(Config)

# Register all routes defined in the main Blueprint (This handles your '/' route!)
app.register_blueprint(main)

# Register the global error boundary (handles 400, 403, 404, 405, 429, 500,
# and any unhandled Exception).  Must be called after Blueprint registration
# so Blueprint-level error handlers take precedence where defined.
register_error_handlers(app)


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
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self' https://api.github.com; "
        "frame-ancestors 'none'"
    )
    return response


# Expose the 500 handler at module level so existing tests can import it
# directly:  from app import app, internal_server_error
def internal_server_error(error):
    """Proxy kept for backward compatibility with test_basic.py."""
    from errors.handlers import internal_server_error as _handler
    return _handler(error)


if __name__ == "__main__":

    import os
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1")
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=debug_mode,
    )
