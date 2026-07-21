import json
import os
from app import app
from models import db, Project

def seed_database():
    with app.app_context():
        # Create all tables
        db.drop_all()
        db.create_all()

        # Path to projects.json
        data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "projects.json")
        
        if not os.path.exists(data_file):
            print(f"Error: Could not find {data_file}")
            return
            
        print(f"Loading data from {data_file}...")
        
        with open(data_file, "r", encoding="utf-8") as f:
            projects_data = json.load(f)
            
        print(f"Found {len(projects_data)} projects. Inserting into database...")
        
        for p_data in projects_data:
            # We enforce JSON arrays for features, skills, etc
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
                starter_code=p_data.get("starter_code")
            )
            db.session.add(project)
            
        db.session.commit()
        print("Successfully seeded the database!")

if __name__ == "__main__":
    seed_database()
