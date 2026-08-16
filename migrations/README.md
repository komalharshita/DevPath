# Migrations

DevPath does not use SQL migration files. The database schema is defined exclusively by
the SQLAlchemy models in `src/models.py` and is created with `db.create_all()` at startup
(see `src/app.py`, `src/seed_db.py`, and `tests/conftest.py`).

## Intended data model (source of truth: `src/models.py`)

- `projects` — the `Project` model
- `users` — the `User` model
- `project_progress` — the `ProjectProgress` model
- `user_game_progress` — the `UserGameProgress` model

Learning paths are kept in memory (`src/utils/learning_path.py`), not in the database, so
no `paths` table exists.

Hand-written SQL files previously placed in this directory referenced tables that no model
defines (including a dangling `FOREIGN KEY ... REFERENCES paths(id)` on a nonexistent
`paths` table) and could not be applied by any workflow. They were removed. If a real
migration workflow is ever needed, use Flask-Migrate/Alembic so the schema stays in sync
with `src/models.py`.
