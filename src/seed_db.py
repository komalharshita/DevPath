import json
import os
import sys
from app import app
from models import db, Project
from utils.data_loader import validate_projects

def seed_database(reset=False):
    """Seed the project catalog from data/projects.json.

    Idempotent by default: it upserts projects by id (matching the app.py
    auto-seed behavior) and never drops tables, so existing user data,
    progress and admin flags are preserved. Pass ``reset=True`` to drop all
    tables first — this is destructive.
    """
    with app.app_context():
        db.create_all()

        # Path to projects.json
        data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "projects.json")

        if not os.path.exists(data_file):
            print(f"Error: Could not find {data_file}")
            return

        print(f"Loading data from {data_file}...")

        with open(data_file, "r", encoding="utf-8") as f:
            projects_data = json.load(f)

        validate_projects(projects_data)

        if reset:
            db.drop_all()
            db.create_all()

        print(f"Found {len(projects_data)} projects. Upserting into database...")

        for p_data in projects_data:
            project = db.session.get(Project, p_data.get("id"))
            if project is None:
                project = Project(id=p_data.get("id"))
                db.session.add(project)
            project.title = p_data.get("title", "")
            project.level = p_data.get("level", "Beginner")
            project.interest = p_data.get("interest", "")
            project.time = p_data.get("time", "Low")
            project.description = p_data.get("description", "")
            project.skills = p_data.get("skills", [])
            project.features = p_data.get("features", [])
            project.tech_stack = p_data.get("tech_stack", [])
            project.roadmap = p_data.get("roadmap", [])
            project.resources = p_data.get("resources", [])
            project.starter_code = p_data.get("starter_code")

        db.session.commit()
        print("Successfully seeded the database!")

if __name__ == "__main__":
    reset = "--reset" in sys.argv[1:]
    if reset:
        confirm = input(
            "WARNING: --reset will DROP ALL TABLES and destroy all user data. "
            "Type 'yes' to continue: "
        )
        if confirm.strip().lower() != "yes":
            print("Aborted.")
            sys.exit(0)
    seed_database(reset=reset)
