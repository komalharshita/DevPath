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
