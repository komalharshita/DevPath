# services/starter_code_service.py
import os
from repositories.starter_code_repository import file_exists, read_file_content

STARTER_CODE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "starter_code")
)


def resolve_starter_file(project):
    """Given a project dict, return the absolute path to its starter code file.

    Supports nested paths within the starter_code directory.
    Path traversal attempts (e.g. ../../etc/passwd) are blocked by verifying the
    resolved path stays inside STARTER_CODE_DIR.
    """
    raw_path = project.get("starter_code", "")
    if not raw_path:
        return None

    # Normalize to the local OS separator and strip any leading "starter_code/" prefix
    relative = raw_path.replace("/", os.sep)
    prefix = "starter_code" + os.sep
    if relative.startswith(prefix):
        relative = relative[len(prefix):]

    # Resolve to an absolute path and confirm it stays within STARTER_CODE_DIR.
    full_path = os.path.abspath(os.path.normpath(os.path.join(STARTER_CODE_DIR, relative)))
    if os.path.commonpath([STARTER_CODE_DIR, full_path]) != STARTER_CODE_DIR:
        return None

    if not file_exists(full_path):
        return None

    return full_path


def read_starter_code(project):
    """Return a dict containing the filename and text content of the starter file.

    Returns None if the file cannot be found.
    """
    full_path = resolve_starter_file(project)
    if not full_path:
        return None

    filename = os.path.basename(full_path)
    code = read_file_content(full_path)

    return {"filename": filename, "code": code}


def get_starter_code_dir():
    """Return the absolute path to the starter_code directory."""
    return STARTER_CODE_DIR
