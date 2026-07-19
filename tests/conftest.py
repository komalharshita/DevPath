# tests/conftest.py
# Pytest configuration and shared fixtures for DevPath tests.

import sys
import os

# Allow imports from the project root and src/ when running tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from app import app
from utils.rate_limiter import reset_rate_limits

# Disable CSRF globally for testing
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

@pytest.fixture(autouse=True)
def app_context():
    """Push Flask application context and setup/seed DB for testing."""
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_db_path = os.path.join(basedir, "data", "test_devpath.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + test_db_path
    
    with app.app_context():
        from models import db
        db.drop_all()
        db.create_all()
        
        # Seed projects
        from models import Project
        if True:
            import json
            data_file = os.path.join(basedir, "data", "projects.json")
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
                    starter_code=p_data.get("starter_code")
                )
                db.session.add(project)
            db.session.commit()
            
        yield


@pytest.fixture
def client():
    """Provide a Flask test client for testing the application."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def _reset_rate_limiter_state():
    """Clear rate-limit counters before every test.
 
    Without this, tests across different files that hit the same rate-limited route 
    would exhaust each other's request budget depending on test execution order, causing
    order-dependent 429 failures unrelated to what each test is actually checking.
    """
    reset_rate_limits()
    yield