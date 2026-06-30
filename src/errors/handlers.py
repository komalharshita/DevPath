# errors/handlers.py
# Global error handling for DevPath.
#
# All Flask error handlers live here so app.py stays lean.
# Each handler:
#   1. Logs the exception via utils/error_logger.py (server-side only).
#   2. Renders the matching HTML template with a safe, user-friendly message.
#   3. Never leaks stack traces, file paths, or internal state to the client.
#
# Register by calling register_error_handlers(app) from app.py.
from flask import make_response
from flask import Flask, render_template, request, jsonify
from config import Config
from utils.error_logger import log_exception

from flask import has_request_context, request

from flask import has_request_context

def _wants_json():
    if not has_request_context():
        return False

    if request.path.startswith("/api/"):
        return True

    # No explicit Accept header (e.g. a bare test_request_context call) —
    # default to HTML rather than relying on accept_mimetypes comparison,
    # which can resolve differently across Werkzeug versions when the
    # header is absent.
    accept_header = request.headers.get("Accept", "")
    if not accept_header or accept_header == "*/*":
        return False

    return (
        request.accept_mimetypes["application/json"]
        >
        request.accept_mimetypes["text/html"]
    )


def _json_error(status_code: int, message: str, correlation_id: str = ""):
    """Build a consistent JSON error envelope."""
    body = {"error": message}
    if correlation_id:
        body["reference"] = correlation_id
    return jsonify(body), status_code


# ---------------------------------------------------------------------------
# Standalone handler functions — importable directly for testing
# ---------------------------------------------------------------------------

def bad_request(error):
    """Handle 400 Bad Request."""
    correlation_id = log_exception(error, status_code=400, context="bad_request")
    if _wants_json():
        return _json_error(400, "Bad request.", correlation_id)
    return render_template("400.html", config=Config, reference=correlation_id), 400


def forbidden(error):
    correlation_id = log_exception(error, status_code=403, context="forbidden")
    if _wants_json():
        return _json_error(403, "Access denied.", correlation_id)
    return render_template(
        "403.html",
        config=Config,
        reference=correlation_id,
    ), 403

def page_not_found(error):
    """Handle 404 Not Found."""
    correlation_id = log_exception(error, status_code=404, context="page_not_found")
    if _wants_json():
        return _json_error(404, "The requested resource was not found.", correlation_id)
    return render_template("404.html", config=Config, reference=correlation_id), 404


def method_not_allowed(error):
    """Handle 405 Method Not Allowed."""
    correlation_id = log_exception(error, status_code=405, context="method_not_allowed")
    if _wants_json():
        return _json_error(405, "HTTP method not allowed.", correlation_id)
    return render_template("405.html", config=Config, reference=correlation_id), 405


def too_many_requests(error):
    """Handle 429 Too Many Requests."""
    correlation_id = log_exception(error, status_code=429, context="too_many_requests")
    if _wants_json():
        return _json_error(429, "Too many requests. Please slow down.", correlation_id)
    return render_template("429.html", config=Config, reference=correlation_id), 429


def internal_server_error(error):
    correlation_id = log_exception(
        error,
        status_code=500,
        context="internal_server_error",
    )

    if _wants_json():
        return _json_error(
            500,
            "An unexpected error occurred.",
            correlation_id,
        )

    rendered = render_template(
        "500.html",
        config=Config,
        reference=correlation_id,
    )

    return rendered, 500


def unhandled_exception(error):
    """Catch-all for any Exception not matched by a specific handler."""
    correlation_id = log_exception(error, status_code=500, context="unhandled_exception")
    if _wants_json():
        return _json_error(500, "An unexpected error occurred.", correlation_id)
    rendered = render_template(
        "500.html",
        config=Config,
        reference=correlation_id,
    )

    return rendered, 500


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_error_handlers(app: Flask) -> None:
    """Attach all global error handlers to the Flask application.

    Call once during application initialisation:

        from errors.handlers import register_error_handlers
        register_error_handlers(app)
    """
    app.register_error_handler(400, bad_request)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(429, too_many_requests)
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(Exception, unhandled_exception)
