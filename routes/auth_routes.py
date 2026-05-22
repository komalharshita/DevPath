from flask import Blueprint, request, render_template, redirect, session, flash,current_app
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
import bcrypt

# Create Blueprint
auth = Blueprint("auth", __name__)

# Initialize Database
db = SQLAlchemy()

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # Password Check Method
    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password.encode("utf-8")
        )

#Signup route
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists.", "error")
            return render_template('signup.html')
        # Hash password
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        # Create user
        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please login.", "success")
        return redirect('/login')

    return render_template('signup.html')

#Login Route
@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        # Validate user
        if user and user.check_password(password):
            # Store session
            session['email'] = user.email
            session.permanent=True
            flash("Logged in successfully!", "success")
            return redirect('/dashboard')
        else:
            flash("Invalid email or password.", "error")
            return render_template('login.html')

    return render_template('login.html')

#DashBoard Route
@auth.route('/dashboard')
def dashboard():
    # Check if logged in
    if 'email' in session:
        user = User.query.filter_by(
            email=session['email']
        ).first()
        return render_template(
            'dashboard.html',
            user=user
        )
    flash("Please login first.", "error")    
    return redirect('/login')

#Logout Route
@auth.route('/logout')
def logout():

    session.pop('email', None)
    flash("Logged out successfully.", "success")
    return redirect('/login')

#Google Login Route
@auth.route('/login/google')
def login_google():
    google = current_app.extensions['google_auth']
    return google.authorize_redirect(
        'http://127.0.0.1:5000/login/google/authorized',
        prompt="consent select_account"#ensure account selection during google login
    )


@auth.route('/login/google/authorized')
def google_authorized():
    google = current_app.extensions['google_auth']

    token = google.authorize_access_token()

    user_info = token.get("userinfo")
    if not user_info:
        user_info = google.parse_id_token(token)

    email = user_info["email"]
    name = user_info["name"]

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            name=name,
            email=email,
            password="google-user"
        )
        db.session.add(user)
        db.session.commit()

    session["email"] = email

    flash("Google login successful!", "success")
    return redirect("/dashboard")