# utils/file_server.py
# Handles safe resolution and serving of starter code files.

import os

# Absolute path to the starter_code directory
STARTER_CODE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "starter_code")
)


def resolve_starter_file(project):
    """
    Given a project dict, return the absolute path to its starter code file.
    Supports nested paths within the starter_code directory (e.g. survey_form/index.html).
    Returns None if the project has no starter_code field or the file does not exist.
    Path traversal attempts (e.g. ../../etc/passwd) are blocked by verifying the
    resolved path stays inside STARTER_CODE_DIR.
    """
    raw_path = project.get("starter_code", "")
    if not raw_path:
        return None

    # Normalize to the local OS separator and strip any leading "starter_code/" prefix
    # so values like "starter_code/survey_form/index.html" and "survey_form/index.html"
    # are both handled correctly.
    relative = raw_path.replace("/", os.sep)
    prefix = "starter_code" + os.sep
    if relative.startswith(prefix):
        relative = relative[len(prefix):]

    # Resolve to an absolute path and confirm it stays within STARTER_CODE_DIR
    full_path = os.path.normpath(os.path.join(STARTER_CODE_DIR, relative))
    if not full_path.startswith(STARTER_CODE_DIR + os.sep):
        return None

    if not os.path.exists(full_path):
        return None

    return full_path


def read_starter_code(project):
    """
    Return a dict containing the filename and text content of the starter file.
    Returns None if the file cannot be found.
    """
    full_path = resolve_starter_file(project)
    if not full_path:
        return None

    filename = os.path.basename(full_path)
    with open(full_path, "r", encoding="utf-8") as f:
        code = f.read()

    return {"filename": filename, "code": code}


def get_starter_code_dir():
    """Return the absolute path to the starter_code directory for use with send_from_directory."""
    return STARTER_CODE_DIR
