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

from flask import Flask, render_template, request, jsonify
from routes.main_routes import main
import time
from utils.redis_client import get_redis_client

app = Flask(__name__)

WINDOW_SIZE_IN_SECONDS = 60
MAX_REQUESTS = 100


@app.before_request
def rate_limit():
    if request.path.startswith('/api'):
        r = get_redis_client()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'anonymous'

        redis_key = f"rate_limit:{ip}"
        now = int(time.time() * 1000)
        clear_before = now - (WINDOW_SIZE_IN_SECONDS * 1000)

        try:
            pipe = r.pipeline()
            pipe.zremrangebyscore(redis_key, 0, clear_before)
            pipe.zadd(redis_key, {str(now): now})              # Add current hit
            pipe.zcard(redis_key)                              # Get current window count
            pipe.expire(redis_key, WINDOW_SIZE_IN_SECONDS)     # Slide window TTL
            results = pipe.execute()

            request_count = results[2]
            remaining = max(0, MAX_REQUESTS - request_count)

            # Injecting standards compliance limit attributes into the request context
            request.rate_limit_headers = {
                'X-RateLimit-Limit': str(MAX_REQUESTS),
                'X-RateLimit-Remaining': str(remaining)
            }

            if request_count > MAX_REQUESTS:
                response = jsonify({'error': 'Too Many Requests', 'message': 'Rate limit exceeded.'})
                response.status_code = 429
                response.headers.update(request.rate_limit_headers)
                response.headers['Retry-After'] = str(WINDOW_SIZE_IN_SECONDS)
                return response

        except Exception as e:
            app.logger.error(f"Rate Limiter Error: {e}")
            # Fail-open design option so down-stream clients don't suffer complete outage
            pass


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

@app.errorhandler(405)
def method_not_allowed(error):
    """Render a friendly 405 page when the wrong HTTP method is used."""
    return render_template("405.html"), 405


if __name__ == "__main__":
    # debug=True is only for local development.
    # Never run with debug=True in a production deployment.
    app.run(debug=True)
