import json
import sqlite3
import logging

from config import Config

logger = logging.getLogger("devpath.db_loader")


def load_projects_from_db():
    """
    Load all projects from SQLite.

    Returns:
        list[dict]
    """
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title,
                skills,
                level,
                interest,
                time,
                description,
                features,
                tech_stack,
                roadmap,
                resources,
                starter_code
            FROM projects
            """
        )

        projects = []

        for row in cursor.fetchall():
            projects.append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "skills": json.loads(row["skills"]),
                    "level": row["level"],
                    "interest": row["interest"],
                    "time": row["time"],
                    "description": row["description"],
                    "features": json.loads(row["features"]),
                    "tech_stack": json.loads(row["tech_stack"]),
                    "roadmap": json.loads(row["roadmap"]),
                    "resources": json.loads(row["resources"]),
                    "starter_code": row["starter_code"],
                }
            )

        return projects

    finally:
        conn.close()