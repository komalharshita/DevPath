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

from flask import Flask, render_template
from routes.main_routes import main

app = Flask(__name__)

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