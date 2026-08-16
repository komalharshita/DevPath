# tests/test_db_schema_consistency.py
# Regression test for issue #1877: every table referenced anywhere in the schema
# (SQLAlchemy foreign keys and any hand-written migration SQL) must be a real table.

import glob
import os
import re

MODEL_TABLENAME_RE = re.compile(r"__tablename__\s*=\s*['\"]([^'\"]+)['\"]")
MODEL_FK_RE = re.compile(r"db\.ForeignKey\(['\"]([^'\"]+)['\"]\)")
SQL_CREATE_TABLE_RE = re.compile(r"CREATE TABLE\s+IF NOT EXISTS\s+(\w+)", re.IGNORECASE)
SQL_REFERENCES_RE = re.compile(r"REFERENCES\s+(\w+)\s*\(", re.IGNORECASE)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _model_source():
    path = os.path.join(ROOT, "src", "models.py")
    with open(path, encoding="utf-8") as f:
        return f.read()


def _model_tables():
    return set(MODEL_TABLENAME_RE.findall(_model_source()))


def test_model_foreign_keys_reference_real_tables():
    """Every db.ForeignKey(...) in src/models.py must target a defined table."""
    tables = _model_tables()
    content = _model_source()
    refs = {m.group(1).split(".")[0] for m in MODEL_FK_RE.finditer(content)}
    missing = sorted(refs - tables)
    assert not missing, (
        "src/models.py declares foreign keys to undefined tables: "
        f"{missing}"
    )


def test_sql_migrations_reference_only_known_tables():
    """Migration SQL may only reference model tables or tables created by
    an earlier migration in the same set — no dangling foreign keys."""
    known = set(_model_tables())
    sql_files = sorted(glob.glob(os.path.join(ROOT, "migrations", "*.sql")))
    for path in sql_files:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        refs = set(SQL_REFERENCES_RE.findall(content))
        missing = sorted(refs - known)
        assert not missing, (
            f"{os.path.relpath(path, ROOT)} references unknown tables: "
            f"{missing}"
        )
        known |= set(SQL_CREATE_TABLE_RE.findall(content))
