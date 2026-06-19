# repositories/starter_code_repository.py
import os


def file_exists(full_path: str) -> bool:
    """Check if the file at the given absolute path exists and is a file."""
    return os.path.isfile(full_path)


def read_file_content(full_path: str) -> str:
    """Read and return the text content of the file at the given absolute path."""
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()
