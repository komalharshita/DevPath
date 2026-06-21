import json
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

JSON_FILE = os.path.join(BASE_DIR, "data", "projects.json")
DB_FILE = os.path.join(BASE_DIR, "data", "projects.db")


def create_schema(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            skills TEXT NOT NULL,
            level TEXT NOT NULL,
            interest TEXT NOT NULL,
            time TEXT NOT NULL,
            description TEXT NOT NULL,
            features TEXT NOT NULL,
            tech_stack TEXT NOT NULL,
            roadmap TEXT NOT NULL,
            resources TEXT NOT NULL,
            starter_code TEXT NOT NULL
        )
        """
    )


def migrate():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        projects = json.load(f)

    conn = sqlite3.connect(DB_FILE)

    try:
        cursor = conn.cursor()

        create_schema(cursor)

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_projects_level ON projects(level)"
        )

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_projects_interest ON projects(interest)"
        )

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_projects_title ON projects(title)"
        )
        
        cursor.execute("DELETE FROM projects")

        for p in projects:
            cursor.execute(
                """
                INSERT INTO projects (
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
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    p["id"],
                    p["title"],
                    json.dumps(p["skills"]),
                    p["level"],
                    p["interest"],
                    p["time"],
                    p["description"],
                    json.dumps(p["features"]),
                    json.dumps(p["tech_stack"]),
                    json.dumps(p["roadmap"]),
                    json.dumps(p["resources"]),
                    p["starter_code"],
                ),
            )

        conn.commit()

        print(f"Migrated {len(projects)} projects successfully.")

    finally:
        conn.close()


if __name__ == "__main__":
    migrate()