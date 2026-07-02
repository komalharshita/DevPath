# scripts/validate_projects.py
#
# Validates that every entry in data/projects.json has all required fields.
#
# Run manually:
#   python scripts/validate_projects.py
#
# Run in CI:
#   python scripts/validate_projects.py
#   (exits with code 1 if any project is missing a required field)
#
# If this script fails, a PR should not be merged.
# Contributors who add projects to data/projects.json must ensure
# all required fields are present before opening a PR.

import json
import sys
import os

# These are the fields every project in data/projects.json MUST have.
# If a project is missing any of these, the script will report it and fail.
REQUIRED_FIELDS = {
    "id",
    "title",
    "skills",
    "level",
    "interest",
    "time",
    "description",
    "roadmap",
    "resources",
}


def validate_projects(path: str = "data/projects.json") -> list:
    """
    Load projects.json and check every entry for missing required fields.

    Args:
        path: Path to the projects JSON file.

    Returns:
        A list of error strings. Empty list means all projects are valid.
    """
    # If path is an absolute path (from tests), use it directly
    # If it's relative, build from project root
    if os.path.isabs(path):
        abs_path = path
    else:
        abs_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            path
        )

    if not os.path.exists(abs_path):
        return [f"File not found: {abs_path}"]

    with open(abs_path, "r", encoding="utf-8") as f:
        try:
            projects = json.load(f)
        except json.JSONDecodeError as e:
            return [f"JSON parse error in {path}: {e}"]

    if not isinstance(projects, list):
        return ["projects.json must be a JSON array at the top level"]

    errors = []
    for project in projects:
        project_id = project.get("id", "unknown")
        project_title = project.get("title", "(no title)")

        # Find which required fields are missing from this project
        missing = REQUIRED_FIELDS - set(project.keys())

        if missing:
            errors.append(
                f"Project id={project_id} ('{project_title}'): "
                f"missing required fields: {sorted(missing)}"
            )

        # Also check that list fields are actually lists (not empty strings)
        for list_field in ("skills", "roadmap", "resources"):
            if list_field in project and not isinstance(project[list_field], list):
                errors.append(
                    f"Project id={project_id} ('{project_title}'): "
                    f"'{list_field}' must be a list, got {type(project[list_field]).__name__}"
                )

        # Check that level is a valid value
        valid_levels = {"Beginner", "Intermediate", "Advanced"}
        if "level" in project and project["level"] not in valid_levels:
            errors.append(
                f"Project id={project_id} ('{project_title}'): "
                f"'level' is '{project['level']}', must be one of {sorted(valid_levels)}"
            )

        # Check that time is a valid value
        valid_times = {"Low", "Medium", "High"}
        if "time" in project and project["time"] not in valid_times:
            errors.append(
                f"Project id={project_id} ('{project_title}'): "
                f"'time' is '{project['time']}', must be one of {sorted(valid_times)}"
            )

    return errors


if __name__ == "__main__":
    print("Validating data/projects.json...")
    errors = validate_projects()

    if errors:
        print(f"\n[FAIL] Found {len(errors)} error(s):\n")
        for error in errors:
            print(f"  * {error}")
        print("\nFix these before merging.")
        sys.exit(1)      # Exit code 1 = failure (CI will catch this)
    else:
        print(f"[SUCCESS] All projects are valid.")
        sys.exit(0)      # Exit code 0 = success
