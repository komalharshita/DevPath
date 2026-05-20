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
from routes.auth_routes import auth, db
from datetime import timedelta
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")
import os

app = Flask(__name__)

#Session secret key
app.secret_key =os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#automatic logout after 7 days
app.permanent_session_lifetime = timedelta(days=7)

#Initialize db
db.init_app(app)
#Initialize OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)
app.extensions['google_auth'] = google
# Register all routes defined in the main Blueprint
app.register_blueprint(main)
app.register_blueprint(auth)

# ---- Error handlers ----

@app.errorhandler(404)
def page_not_found(error):
    """Render a friendly 404 page instead of the raw Flask error."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Render a friendly 500 page for unexpected server errors."""
    return render_template("500.html"), 500

auth-feature
with app.app_context():
    db.create_all()
@app.errorhandler(405)
def method_not_allowed(error):
    """Render a friendly 405 page when the wrong HTTP method is used."""
    return render_template("405.html"), 405
main
if __name__ == "__main__":
    # debug=True is only for local development.
    # Never run with debug=True in a production deployment.
    app.run(debug=True)
