"""Tests for seed_db.py.

Verifies idempotent seeding, user preservation, reset flag, and validation.
"""

import json
import sys
import pytest
from app import app
from models import db, Project, User, ProjectProgress, UserGameProgress
from seed_db import seed_database, main


def test_seed_database_is_idempotent_and_preserves_users():
    """Seeding on an existing database must preserve all user data and progress."""
    with app.app_context():
        # Ensure initial seeded state
        seed_database()

        # Insert a test user with progress and game data
        user = User(
            id=999,
            github_id="seed_test_github_user",
            username="seed_test_user",
            avatar_url="https://example.com/avatar.png",
            is_admin=True,
            saved_skills=["Python", "Flask"],
            bookmarked_projects=[1, 2]
        )
        db.session.add(user)
        db.session.flush()

        progress = ProjectProgress(
            user_id=user.id,
            project_id=1,
            completed_steps=[1, 2]
        )
        db.session.add(progress)

        game = UserGameProgress(
            user_id=user.id,
            data={"score": 100, "level": 3}
        )
        db.session.add(game)
        db.session.commit()

        initial_project_count = Project.query.count()

        # Re-run seed_database() without reset (idempotent upsert)
        seed_database()

        # Verify user, progress, and game progress are completely preserved
        preserved_user = db.session.get(User, 999)
        assert preserved_user is not None
        assert preserved_user.username == "seed_test_user"
        assert preserved_user.is_admin is True
        assert preserved_user.saved_skills == ["Python", "Flask"]
        assert preserved_user.bookmarked_projects == [1, 2]

        preserved_progress = ProjectProgress.query.filter_by(
            user_id=999, project_id=1
        ).first()
        assert preserved_progress is not None
        assert preserved_progress.completed_steps == [1, 2]

        preserved_game = UserGameProgress.query.filter_by(user_id=999).first()
        assert preserved_game is not None
        assert preserved_game.data == {"score": 100, "level": 3}

        # Project count should remain unchanged
        assert Project.query.count() == initial_project_count


def test_seed_database_updates_existing_project_fields():
    """Seeding must update existing projects with new data without duplicate rows."""
    with app.app_context():
        seed_database()

        # Modify project 1 in DB
        p1 = db.session.get(Project, 1)
        original_title = p1.title
        p1.title = "Temporary Altered Title"
        db.session.commit()

        assert db.session.get(Project, 1).title == "Temporary Altered Title"

        # Re-seed
        seed_database()

        # Project 1 should be restored to its canonical data
        p1_restored = db.session.get(Project, 1)
        assert p1_restored.title == original_title


def test_seed_database_reset_drops_tables_and_data():
    """Passing reset=True must drop all tables and recreate them cleanly."""
    with app.app_context():
        user = User(
            id=888,
            github_id="reset_test_user",
            username="reset_user"
        )
        db.session.add(user)
        db.session.commit()
        assert db.session.get(User, 888) is not None

        # Seed with destructive reset
        seed_database(reset=True)

        # User table was dropped and recreated, so user is gone
        assert db.session.get(User, 888) is None
        assert Project.query.count() > 0


def test_seed_database_validation_failure_rolls_back(tmp_path):
    """Corrupted project data must fail validation and roll back cleanly."""
    invalid_data = [
        {
            "id": 9999,
            "title": "",  # Empty string violates validation
            "level": "Beginner",
            "interest": "Web",
            "time": "Low",
            "description": "test",
            "skills": ["python"],
            "features": ["feat"],
            "tech_stack": ["flask"],
            "roadmap": ["step1"],
            "resources": [],
            "starter_code": None
        }
    ]
    invalid_file = tmp_path / "invalid_projects.json"
    invalid_file.write_text(json.dumps(invalid_data), encoding="utf-8")

    with app.app_context():
        seed_database()
        count_before = Project.query.count()

        with pytest.raises(
            ValueError, match="Empty value for field 'title'"
        ):
            seed_database(data_file=str(invalid_file))

        # Ensure no invalid project was inserted and count is unchanged
        assert Project.query.count() == count_before
        assert db.session.get(Project, 9999) is None


def test_seed_database_missing_file_raises_error():
    """Passing a nonexistent file path must raise FileNotFoundError."""
    with app.app_context():
        with pytest.raises(FileNotFoundError):
            seed_database(data_file="/nonexistent/path/to/projects.json")


def test_cli_main_aborts_on_negative_confirmation(monkeypatch):
    """CLI --reset must abort and exit 0 when user declines confirmation."""
    monkeypatch.setattr(sys, "argv", ["seed_db.py", "--reset"])
    monkeypatch.setattr("builtins.input", lambda prompt: "no")

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_cli_main_proceeds_on_positive_confirmation(monkeypatch):
    """CLI --reset must proceed when user confirms with 'yes'."""
    monkeypatch.setattr(sys, "argv", ["seed_db.py", "--reset"])
    monkeypatch.setattr("builtins.input", lambda prompt: "yes")

    with app.app_context():
        main()
        assert Project.query.count() > 0


def test_cli_main_force_flag_bypasses_prompt(monkeypatch):
    """CLI --reset --yes must proceed without prompting."""
    monkeypatch.setattr(sys, "argv", ["seed_db.py", "--reset", "--yes"])

    with app.app_context():
        main()
        assert Project.query.count() > 0


def test_cli_main_default_idempotent(monkeypatch):
    """CLI without flags runs idempotent seed without prompt."""
    monkeypatch.setattr(sys, "argv", ["seed_db.py"])

    with app.app_context():
        main()
        assert Project.query.count() > 0
