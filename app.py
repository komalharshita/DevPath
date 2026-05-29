import os
from flask import Flask, render_template
from routes.main_routes import main

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())

app.register_blueprint(main)

@app.after_request
def add_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' https://api.github.com; "
        "frame-ancestors 'none';"
    )
    return response

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return render_template("405.html"), 405

@app.errorhandler(403)
def forbidden(error):
    return render_template("403.html"), 403

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug_mode)
