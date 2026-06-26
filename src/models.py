from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    
    # Store arrays of strings as JSON
    saved_skills = db.Column(db.JSON, nullable=False, default=list)
    bookmarked_projects = db.Column(db.JSON, nullable=False, default=list)

    def to_dict(self):
        return {
            "id": self.id,
            "github_id": self.github_id,
            "username": self.username,
            "avatar_url": self.avatar_url,
            "saved_skills": self.saved_skills if self.saved_skills else [],
            "bookmarked_projects": self.bookmarked_projects if self.bookmarked_projects else []
        }
