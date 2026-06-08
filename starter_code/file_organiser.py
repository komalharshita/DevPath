# Starter code: File Organiser Script
import shutil
from pathlib import Path

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".odt"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".ogg"},
    "Archives": {".zip", ".tar", ".gz", ".rar", ".7z"},
}


def category_for(extension):
    """Return the category folder name for a given file extension."""
    ext = extension.lower()
    for name, exts in CATEGORIES.items():
        if ext in exts:
            return name
    return "Other"


def organise(folder):
    """Move every file in `folder` into a subfolder named after its category."""
    folder = Path(folder)
    summary = {}

    # TODO: Step 1 — Iterate over files in `folder` (skip subdirectories)
    # for item in folder.iterdir():
    #     if not item.is_file():
    #         continue
    #
    #     TODO: Step 2 — Pick the category and create the subfolder
    #     dest_dir = folder / category_for(item.suffix)
    #     dest_dir.mkdir(exist_ok=True)
    #
    #     TODO: Step 3 — Move the file and update the summary count
    #     shutil.move(str(item), str(dest_dir / item.name))
    #     summary[dest_dir.name] = summary.get(dest_dir.name, 0) + 1

    return summary


if __name__ == "__main__":
    target = input("Enter the folder path to organise: ").strip()
    result = organise(target)
    print("Files moved per category:")
    for category, count in result.items():
        print(f"  {category}: {count}")
