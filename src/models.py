from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    level = db.Column(db.String(50), nullable=False)
    interest = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Store arrays as JSON
    skills = db.Column(db.JSON, nullable=False, default=list)
    features = db.Column(db.JSON, nullable=False, default=list)
    tech_stack = db.Column(db.JSON, nullable=False, default=list)
    roadmap = db.Column(db.JSON, nullable=False, default=list)
    resources = db.Column(db.JSON, nullable=True, default=list)
    starter_code = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        """Convert the model to a dictionary matching projects.json format."""
        return {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "interest": self.interest,
            "time": self.time,
            "description": self.description,
            "skills": self.skills if self.skills else [],
            "features": self.features if self.features else [],
            "tech_stack": self.tech_stack if self.tech_stack else [],
            "roadmap": self.roadmap if self.roadmap else [],
            "resources": self.resources if self.resources else [],
            "starter_code": self.starter_code
        }

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    
    # Store arrays of strings as JSON
    saved_skills = db.Column(db.JSON, nullable=False, default=list)
    bookmarked_projects = db.Column(db.JSON, nullable=False, default=list)

    def to_dict(self):
        return {
            "id": self.id,
            "github_id": self.github_id,
            "username": self.username,
            "avatar_url": self.avatar_url,
            "is_admin": self.is_admin,
            "saved_skills": self.saved_skills if self.saved_skills else [],
            "bookmarked_projects": self.bookmarked_projects if self.bookmarked_projects else []
        }

class ProjectProgress(db.Model):
    __tablename__ = 'project_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    completed_steps = db.Column(db.JSON, nullable=False, default=list)

    user = db.relationship('User', backref=db.backref('progress', lazy=True, cascade="all, delete-orphan"))
    project = db.relationship('Project')
