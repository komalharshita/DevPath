# utils/file_server.py
# Handles safe resolution and serving of starter code files.

import os

# Absolute path to the starter_code directory
STARTER_CODE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "starter_code")
)


def _starter_relative_path(raw_path):
    """
    Turn a projects.json starter_code value into a path relative to STARTER_CODE_DIR.

    Accepts e.g. "starter_code/task_api.py", "task_api.py", or "realtime_chat/app.py".
    Returns None if the value is empty or clearly unsafe (path traversal).
    """
    if not raw_path or not isinstance(raw_path, str):
        return None

    normalized = raw_path.strip().replace("\\", "/")
    if not normalized or normalized.startswith("/"):
        return None

    prefix = "starter_code/"
    if normalized.lower().startswith(prefix):
        relative = normalized[len(prefix) :]
    else:
        relative = normalized

    if not relative or relative.startswith("/"):
        return None

    parts = relative.split("/")
    if ".." in parts:
        return None

    return "/".join(parts)


def _is_inside_starter_dir(full_path):
    """True if full_path is a file under STARTER_CODE_DIR (prevents path traversal)."""
    try:
        full = os.path.realpath(full_path)
        root = os.path.realpath(STARTER_CODE_DIR)
    except OSError:
        return False
    try:
        common = os.path.commonpath([full, root])
    except ValueError:
        return False
    return common == root and full != root


def resolve_starter_file(project):
    """
    Given a project dict, return the absolute path to its starter code file.
    Supports files in subfolders (e.g. realtime_chat/app.py).
    Returns None if the project has no starter_code field or the file does not exist.
    """
    relative = _starter_relative_path(project.get("starter_code", ""))
    if not relative:
        return None

    full_path = os.path.normpath(os.path.join(STARTER_CODE_DIR, *relative.split("/")))

    if not _is_inside_starter_dir(full_path) or not os.path.isfile(full_path):
        return None

    return full_path


def read_starter_code(project):
    """
    Return a dict containing the filename and text content of the starter file.
    Filename is relative to starter_code/ (e.g. "jwt_auth_api.py" or "realtime_chat/app.py").
    Returns None if the file cannot be found.
    """
    full_path = resolve_starter_file(project)
    if not full_path:
        return None

    display_name = os.path.relpath(full_path, STARTER_CODE_DIR).replace("\\", "/")
    with open(full_path, "r", encoding="utf-8") as f:
        code = f.read()

    return {"filename": display_name, "code": code}


def get_starter_code_dir():
    """Return the absolute path to the starter_code directory for use with send_from_directory."""
    return STARTER_CODE_DIR


def starter_download_relpath(full_path):
    """
    Path segment(s) for send_from_directory(STARTER_CODE_DIR, relpath), using / as separator.
    """
    rel = os.path.relpath(full_path, STARTER_CODE_DIR)
    return rel.replace("\\", "/")
