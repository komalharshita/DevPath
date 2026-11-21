"""Database seeding utility for DevPath.

Provides idempotent upsert of project catalog data from data/projects.json,
safeguarding existing user data and progress from accidental deletion.
"""

import json
import os
import sys
from flask import has_app_context
from models import db, Project
from utils.data_loader import validate_projects, clear_cache


def _run_seed(reset=False, data_file=None):
    """Internal helper to execute dataset validation and upsert."""
    if data_file is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_file = os.path.join(root_dir, "data", "projects.json")

    if not os.path.exists(data_file):
        print(f"Error: Could not find {data_file}")
        raise FileNotFoundError(f"Projects data file not found: {data_file}")

    print(f"Loading data from {data_file}...")
    with open(data_file, "r", encoding="utf-8") as f:
        projects_data = json.load(f)

    # Validate dataset before any database writes to prevent partial commits
    validate_projects(projects_data)

    if reset:
        print("Reset requested. Dropping all tables and recreating...")
        db.drop_all()
        db.create_all()
    else:
        # Idempotent: ensures tables exist without dropping existing user data
        db.create_all()

    print(f"Found {len(projects_data)} projects. Upserting into database...")

    try:
        for p_data in projects_data:
            project_id = p_data.get("id")
            project = db.session.get(Project, project_id)
            if project is None:
                project = Project(id=project_id)
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
            est_hours = p_data.get("estimated_hours")
            project.estimated_hours = 0.0 if est_hours is None else est_hours

        db.session.commit()
        clear_cache()
        print("Successfully seeded the database!")
        return len(projects_data)
    except Exception:
        db.session.rollback()
        raise


def seed_database(reset=False, data_file=None):
    """Seed the project catalog from data/projects.json.

    Idempotent by default: upserts projects by id (matching the app.py
    auto-seed behavior) and preserves existing tables, users, progress,
    and admin flags. Pass reset=True to drop and recreate all tables.
    """
    if has_app_context():
        return _run_seed(reset=reset, data_file=data_file)
    else:
        from app import app
        with app.app_context():
            return _run_seed(reset=reset, data_file=data_file)


def __getattr__(name):
    """Lazy module attribute access for backwards-compatible 'app' import."""
    if name == "app":
        from app import app
        return app
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def main():
    """Command-line entry point with interactive confirmation for --reset."""
    reset = "--reset" in sys.argv[1:]
    force = "--yes" in sys.argv[1:] or "-y" in sys.argv[1:]

    if reset and not force:
        confirm = input(
            "WARNING: --reset will DROP ALL TABLES and destroy all user data, "
            "progress, and settings.\nAre you sure you want to proceed? (yes/no): "
        )
        if confirm.strip().lower() not in ("yes", "y"):
            print("Operation cancelled. Database was not reset.")
            sys.exit(0)

    seed_database(reset=reset)


if __name__ == "__main__":
    main()
