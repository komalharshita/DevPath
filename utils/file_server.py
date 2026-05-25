import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STARTER_CODE_DIR = os.path.join(BASE_DIR, "starter_codes")


def get_starter_code_dir():
    return STARTER_CODE_DIR


def resolve_starter_file(project):
  filename = project.get("starter_code_file") or project.get("starter_code")
  if filename:
    filename = filename.replace("starter_code/", "").replace("starter_codes/", "")

    if not filename:
        return None

    full_path = os.path.join(STARTER_CODE_DIR, filename)

    if not os.path.isfile(full_path):
        return None

    return full_path


def read_starter_code(project):
    full_path = resolve_starter_file(project)

    if not full_path:
        return None

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            code = f.read()

        return {
            "filename": os.path.basename(full_path),
            "code": code
        }

    except Exception:
        return None
