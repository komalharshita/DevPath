"""
docker_flask_app.py
===================
Project:    Flask Application Prepared for Docker
Difficulty: Beginner
Skills:     Python, Flask, Docker basics
Time:       Low-Medium (2-4 days)

What you will build:
    A simple Flask web application designed to run inside a Docker container.
    The app will have multiple routes (home, API endpoints, health checks),
    configuration management, and logging. You will learn container-friendly
    patterns: respecting environment variables, logging to stdout, binding to
    0.0.0.0 (not localhost), and graceful shutdown.

    This project teaches: Flask fundamentals, application factory pattern,
    Docker basics, containerisation best practices, and deployment readiness.

How to run locally:
    pip install flask
    python docker_flask_app.py

How to run in Docker:
    1. Create a Dockerfile (see TODO section below)
    2. Build image: docker build -t my-flask-app .
    3. Run container: docker run -p 5000:5000 my-flask-app
    4. Open http://localhost:5000

Learning goals:
    - Building a multi-route Flask application
    - Understanding the application factory pattern
    - Configuration management (dev vs production)
    - Containerisation concepts and Docker basics
    - Health checks and readiness probes
    - Environment variable handling
    - Logging best practices for containers
    - Graceful error handling

Key concept — Docker in plain English:
    Docker packages your application and all dependencies into a "container"
    — a lightweight, isolated environment that runs the same way on any
    machine: your laptop, a cloud server, or in production.

    Without Docker:
        Developer: "Works on my machine!"
        Operations: "Doesn't work on mine. Different Python version."

    With Docker:
        Both use the exact same container image → no surprises.

    A Dockerfile is a recipe for building a container image:
        FROM python:3.11-slim          (start with Python 3.11)
        WORKDIR /app                   (set working directory)
        COPY requirements.txt .        (copy dependencies)
        RUN pip install -r requirements.txt (install packages)
        COPY . .                       (copy app code)
        EXPOSE 5000                    (document port)
        CMD ["python", "docker_flask_app.py"]  (start command)

Data flow:
    Request from browser
        |
        v
    create_app()         <- factory function (already done)
        |
        v
    @app.route("/")      <- home page                      [DONE]
        |
        v
    @app.route("/api/data") <- JSON API endpoint            [TODO]
        |
        v
    @app.route("/health") <- health check for orchestrators [TODO]
        |
        v
    Return JSON/HTML
        |
        v
    Response to client

Roadmap:
    Step 1:  Read and understand create_app() — application factory pattern
    Step 2:  Read and understand the home() route (already complete)
    Step 3:  Complete the /api/data route to return JSON
    Step 4:  Complete the /health route for Kubernetes/Docker Compose checks
    Step 5:  Add error handlers for 404 and 500 errors
    Step 6:  Complete the main application entry point
    Step 7:  Create a Dockerfile for containerisation
    Step 8:  Build and test the Docker image locally
"""

import os
import json
import logging
from datetime import datetime

from flask import Flask, jsonify, render_template_string


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Read configuration from environment variables with sensible defaults.
HOST = os.getenv("FLASK_HOST", "0.0.0.0")  # 0.0.0.0 = all interfaces (Docker-friendly)
PORT = int(os.getenv("FLASK_PORT", 5000))
DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("FLASK_ENV", "development")

# Application version.
APP_VERSION = "1.0.0"

# Startup timestamp (useful for tracking when container started).
STARTUP_TIME = datetime.now().isoformat()


# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

def setup_logging():
    """
    Configure logging to output to stdout (container-friendly).

    In containers, logs should go to stdout/stderr, not files.
    Container orchestrators (Docker, Kubernetes) capture these streams.

    This function is already complete — read it to understand how
    Flask logging works and why stdout is preferred in containers.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Suppress overly verbose TensorFlow/urllib3 logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    return logger


logger = setup_logging()


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(config_name=None):
    """
    Create and configure a Flask application instance.

    Args:
        config_name (str): Configuration environment ("development", "testing",
                          "production"). If None, read from FLASK_ENV env var.

    Returns:
        Flask: A Flask application instance ready to use.

    Why application factory?
        The factory pattern allows creating multiple app instances with
        different configurations. Useful for testing (test app) vs
        production (different settings).

    This function is already complete — read it carefully before implementing
    the routes below. Study:
        - Flask() constructor
        - Blueprint registration (if using)
        - Error handler registration
        - Context processor registration
    """
    app = Flask(__name__)

    # Load configuration based on environment
    if config_name is None:
        config_name = ENVIRONMENT

    if config_name == "production":
        app.config["DEBUG"] = False
        app.config["JSON_SORT_KEYS"] = False
    else:
        app.config["DEBUG"] = DEBUG
        app.config["JSON_SORT_KEYS"] = True

    logger.info(f"Creating app in {config_name} mode")

    return app


# Create the app instance
app = create_app()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask Docker App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        .endpoint { margin: 20px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #007bff; }
        .endpoint code { color: #c7254e; }
        p { color: #666; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐳 Flask Docker Application</h1>
        <p>Welcome! This is a Flask app ready to run in Docker.</p>

        <div class="endpoint">
            <strong>GET /health</strong>
            <p>Health check endpoint. Returns 200 if app is running.</p>
            <code>curl http://localhost:5000/health</code>
        </div>

        <div class="endpoint">
            <strong>GET /api/data</strong>
            <p>API endpoint that returns JSON data.</p>
            <code>curl http://localhost:5000/api/data</code>
        </div>

        <div class="endpoint">
            <strong>GET /api/info</strong>
            <p>Application information (version, environment, startup time).</p>
            <code>curl http://localhost:5000/api/info</code>
        </div>

        <p><strong>Next steps:</strong></p>
        <ol>
            <li>Test the endpoints above using curl or your browser.</li>
            <li>Create a <code>Dockerfile</code> in this directory (see TODO).</li>
            <li>Build the image: <code>docker build -t my-flask-app .</code></li>
            <li>Run the container: <code>docker run -p 5000:5000 my-flask-app</code></li>
        </ol>
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():
    """
    Render the home page.

    This route is already complete — it serves an HTML page explaining
    the application and available endpoints. You do not need to modify it.

    Returns:
        str: Rendered HTML template.
    """
    return render_template_string(HOME_TEMPLATE)


@app.route("/api/data", methods=["GET"])
def get_data():
    """
    API endpoint that returns sample JSON data.

    This is a simple data endpoint demonstrating how to return JSON.
    In a real application, this might fetch data from a database.

    Returns:
        dict: JSON response with sample data.

    TODO:
        1. Create a dictionary with sample data, e.g.:
           data = {
               "message": "Hello from Flask!",
               "timestamp": datetime.now().isoformat(),
               "items": [
                   {"id": 1, "name": "Item A", "value": 100},
                   {"id": 2, "name": "Item B", "value": 200},
               ]
           }
        2. Log the request: logger.info("GET /api/data")
        3. Return jsonify(data) to convert the dict to JSON response.

    Example response:
        {
            "message": "Hello from Flask!",
            "timestamp": "2024-01-15T10:30:45.123456",
            "items": [
                {"id": 1, "name": "Item A", "value": 100},
                {"id": 2, "name": "Item B", "value": 200}
            ]
        }
    """
    # --- Write your API endpoint code here ---

    return jsonify({"error": "Not yet implemented"}), 501


@app.route("/api/info", methods=["GET"])
def get_info():
    """
    Return application metadata (version, environment, health status).

    This endpoint is useful for monitoring and debugging. Container
    orchestrators may call this to verify the app is functioning.

    Returns:
        dict: JSON with app info.

    TODO:
        1. Create a dictionary with metadata:
           info = {
               "version": APP_VERSION,
               "environment": ENVIRONMENT,
               "started_at": STARTUP_TIME,
               "uptime_seconds": (datetime.now() - datetime.fromisoformat(STARTUP_TIME)).total_seconds(),
               "status": "healthy"
           }
        2. Log: logger.info("GET /api/info")
        3. Return jsonify(info)

    Example response:
        {
            "version": "1.0.0",
            "environment": "production",
            "started_at": "2024-01-15T10:00:00",
            "uptime_seconds": 3600,
            "status": "healthy"
        }
    """
    # --- Write your info endpoint code here ---

    return jsonify({"error": "Not yet implemented"}), 501


@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for container orchestrators.

    In Docker Compose and Kubernetes, orchestrators periodically call
    /health to verify the container is running and responsive. A quick
    response with HTTP 200 signals the container is healthy.

    This endpoint should:
        - Respond quickly (< 1 second)
        - Not perform expensive operations
        - Return HTTP 200 if healthy, 503 if degraded

    Returns:
        dict: JSON with health status.
        int:  HTTP status code (200 = healthy, 503 = unhealthy).

    TODO:
        1. Create a health check response:
           health = {
               "status": "ok",
               "service": "flask-app",
               "timestamp": datetime.now().isoformat()
           }
        2. Return jsonify(health), 200

    Health checks in Docker:
        In Dockerfile, add:
            HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
                CMD curl -f http://localhost:5000/health || exit 1

    Health checks in Kubernetes:
        In pod spec, add:
            livenessProbe:
              httpGet:
                path: /health
                port: 5000
              initialDelaySeconds: 5
              periodSeconds: 10
    """
    # --- Write your health check code here ---

    return jsonify({"error": "Not yet implemented"}), 501


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    """
    Handle requests to non-existent routes.

    Args:
        error: The exception object.

    Returns:
        dict: JSON error response.
        int:  HTTP status code 404.

    TODO:
        1. Create error response:
           response = {
               "error": "Not found",
               "message": "The requested resource does not exist.",
               "path": request.path
           }
        2. Log the error: logger.warning(f"404 Not Found: {request.path}")
        3. Return jsonify(response), 404
    """
    # --- Write your 404 handler code here ---

    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Handle unexpected server errors.

    Args:
        error: The exception object.

    Returns:
        dict: JSON error response.
        int:  HTTP status code 500.

    In production, never expose internal error details to clients.
    Always log them server-side for debugging.

    TODO:
        1. Create error response (don't expose internal details):
           response = {
               "error": "Internal server error",
               "message": "An unexpected error occurred.",
               "request_id": some_unique_id  (useful for log correlation)
           }
        2. Log the full traceback: logger.error(f"500 Error", exc_info=True)
        3. Return jsonify(response), 500
    """
    # --- Write your 500 handler code here ---

    return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------

def main():
    """
    Start the Flask development server.

    This function is already complete. It demonstrates:
        - Binding to 0.0.0.0 (all interfaces, required for Docker)
        - Reading host/port from environment variables
        - Logging startup information
    """
    logger.info(f"Starting Flask app...")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Listening on {HOST}:{PORT}")

    # Run the Flask development server.
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
        use_reloader=DEBUG,  # Reload on code changes (dev only)
    )


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Dockerfile template (TODO)
# ---------------------------------------------------------------------------
#
# Save this as "Dockerfile" in the same directory as this script:
#
# FROM python:3.11-slim
#
# WORKDIR /app
#
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
#
# COPY docker_flask_app.py .
#
# EXPOSE 5000
#
# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#     CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1
#
# ENV FLASK_ENV=production
# ENV FLASK_DEBUG=False
#
# CMD ["python", "docker_flask_app.py"]
#
#
# Build the image:
#     docker build -t my-flask-app .
#
# Run the container:
#     docker run -p 5000:5000 my-flask-app
#
# Test it:
#     curl http://localhost:5000/health
#     curl http://localhost:5000/api/data
#


# ---------------------------------------------------------------------------
# requirements.txt template (TODO)
# ---------------------------------------------------------------------------
#
# Save this as "requirements.txt" in the same directory:
#
# Flask==2.3.3
# requests==2.31.0
#
# Then install locally:
#     pip install -r requirements.txt
#
# Or in Docker:
#     RUN pip install -r requirements.txt
