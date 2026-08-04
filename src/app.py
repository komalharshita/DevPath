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
from dotenv import load_dotenv

# Ensure the root directory's .env is loaded even if run from a subfolder
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, '.env'))

# Ensure the 'src' directory is in the python path for Vercel and root-level execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from routes.main_routes import main
from routes.github_routes import github_bp
from config import Config
from errors.handlers import register_error_handlers
from models import db
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default-dev-secret-key-replace-in-production")

# Load config settings into Flask's internal config manager properly
app.config.from_object(Config)

# Initialize SQLAlchemy
db.init_app(app)

with app.app_context():
    db.create_all()
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE projects ADD COLUMN estimated_hours FLOAT DEFAULT 0.0"))
            conn.commit()
    except Exception:
        pass

    # Auto-seed project database if empty (required for ephemeral/Vercel serverless runs)
    from models import Project
    try:
        if Project.query.count() == 0:
            import json
            data_file = os.path.join(root_dir, "data", "projects.json")
            if os.path.exists(data_file):
                with open(data_file, "r", encoding="utf-8") as f:
                    projects_data = json.load(f)
                for p_data in projects_data:
                    project = Project(
                        id=p_data.get("id"),
                        title=p_data.get("title", ""),
                        level=p_data.get("level", "Beginner"),
                        interest=p_data.get("interest", ""),
                        time=p_data.get("time", "Low"),
                        description=p_data.get("description", ""),
                        skills=p_data.get("skills", []),
                        features=p_data.get("features", []),
                        tech_stack=p_data.get("tech_stack", []),
                        roadmap=p_data.get("roadmap", []),
                        resources=p_data.get("resources", []),
                        starter_code=p_data.get("starter_code"),
                        estimated_hours=p_data.get("estimated_hours", 0.0)
                    )
                    db.session.add(project)
                db.session.commit()
                print("Database auto-seeded successfully!")
    except Exception as e:
        print(f"Warning: Failed to auto-seed database: {e}")

# Initialize OAuth
oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=app.config.get("GITHUB_CLIENT_ID"),
    client_secret=app.config.get("GITHUB_CLIENT_SECRET"),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'read:user'},
)

# Register blueprints
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')

# Enable CSRF protection for all state-changing requests
csrf = CSRFProtect(app)

# Register all routes defined in the main Blueprint (This handles your '/' route!)
app.register_blueprint(main)
app.register_blueprint(github_bp)

# Register the global error boundary (handles 400, 403, 404, 405, 429, 500,
# and any unhandled Exception).  Must be called after Blueprint registration
# so Blueprint-level error handlers take precedence where defined.
register_error_handlers(app)

@app.context_processor
def inject_user():
    """Make current_user available to all templates."""
    user_id = session.get('user_id')
    current_user = None
    if user_id:
        from models import User
        current_user = db.session.get(User, user_id)
    return dict(current_user=current_user)


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
        "connect-src 'self'; "
        "form-action 'self' https://formspree.io https://api.web3forms.com; "
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
