"""
file_organiser.py
=================
Project:    File Organiser Script
Difficulty: Beginner
Skills:     Python, os module, shutil module
Time:       Low (a few hours)

What you will build:
    A script that scans a chosen folder and automatically moves files into
    subfolders grouped by type. For example, all .jpg and .png files move
    into an Images/ subfolder, .pdf files go into Documents/, and so on.
    Any extension not recognised goes into an Other/ folder.

How to run:
    python file_organiser.py

    When prompted, enter the path to the folder you want to organise, or
    press Enter to organise the current working directory.

Learning goals:
    - Listing files in a directory with os.listdir()
    - Moving files safely with shutil.move()
    - Creating directories with os.makedirs()
    - Handling name conflicts so no file is ever overwritten
    - Building a lookup table that maps file extensions to folder names

Roadmap:
    Step 1:  Run the script — it will prompt for a folder path
    Step 2:  Complete get_destination_folder() to map extensions to folders
    Step 3:  Complete list_files() to return only files (not sub-folders)
    Step 4:  Complete resolve_conflict() to produce a unique destination path
    Step 5:  Complete move_file() to safely move one file to its subfolder
    Step 6:  Complete organise_folder() to process every file in the folder
    Step 7:  Test on a folder with mixed file types and verify the summary
"""

import os
import shutil


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Maps destination folder name -> list of file extensions that belong there.
# Extensions are lowercase. Files not listed here go to DEFAULT_FOLDER.
FOLDER_MAP = {
    "Images":       [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents":    [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".md"],
    "Videos":       [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"],
    "Music":        [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "Archives":     [".zip", ".tar", ".gz", ".rar", ".7z", ".bz2"],
    "Code":         [".py", ".js", ".html", ".css", ".java", ".cpp", ".ts"],
    "Spreadsheets": [".xls", ".xlsx", ".csv"],
}

DEFAULT_FOLDER = "Other"


# ---------------------------------------------------------------------------
# Core functions — complete the TODOs to make each one work
# ---------------------------------------------------------------------------

def get_destination_folder(extension):
    """
    Return the name of the destination subfolder for a given file extension.

    Args:
        extension (str): The file extension including the dot, e.g. ".jpg".
                         Should already be lowercased before calling.

    Returns:
        str: A folder name from FOLDER_MAP, or DEFAULT_FOLDER if not found.

    Examples:
        get_destination_folder(".jpg")  -> "Images"
        get_destination_folder(".pdf")  -> "Documents"
        get_destination_folder(".xyz")  -> "Other"

    TODO:
        1. Loop through FOLDER_MAP.items() to get each (folder_name, ext_list).
        2. If extension is in ext_list, return folder_name immediately.
        3. If no match is found after the loop, return DEFAULT_FOLDER.
    """
    # --- Write your code here ---

    return DEFAULT_FOLDER


def list_files(folder_path):
    """
    Return a list of filenames for every FILE in folder_path.
    Sub-directories are excluded from the result.

    Args:
        folder_path (str): Absolute path to the folder to scan.

    Returns:
        list[str]: Filenames only (not full paths), e.g. ["photo.jpg", "doc.pdf"].
                   Returns an empty list if the folder is empty or has no files.

    TODO:
        1. Use os.listdir(folder_path) to get all entries in the folder.
        2. For each entry, build its full path with os.path.join(folder_path, entry).
        3. Use os.path.isfile() to check it is a file and not a directory.
        4. Collect and return only the filenames (not full paths) that pass the check.
    """
    # --- Write your code here ---

    return []


def resolve_conflict(dest_dir, filename):
    """
    Return a unique file path inside dest_dir that does not already exist.

    If dest_dir/filename is free, return it unchanged.
    If it already exists, append a counter before the extension:
        photo.jpg -> photo_1.jpg -> photo_2.jpg -> ...

    Args:
        dest_dir (str):  Absolute path to the destination subfolder.
        filename (str):  The original filename, e.g. "photo.jpg".

    Returns:
        str: A full absolute path where no file currently exists.

    Example:
        If dest_dir already contains "photo.jpg" and "photo_1.jpg",
        resolve_conflict(dest_dir, "photo.jpg") returns the full path for
        "photo_2.jpg".

    TODO:
        1. Build the candidate path: os.path.join(dest_dir, filename).
        2. If the candidate does not exist, return it immediately.
        3. Otherwise split the filename into name and extension:
               name, ext = os.path.splitext(filename)
        4. Loop with a counter starting at 1, building new names like
               f"{name}_{counter}{ext}"
           and incrementing counter until a free path is found.
        5. Return the free path.
    """
    # --- Write your code here ---

    return os.path.join(dest_dir, filename)


def move_file(source_folder, filename, dest_folder_name):
    """
    Move a single file from source_folder into the correct subfolder.

    Creates the destination subfolder inside source_folder if it does not
    already exist. Uses resolve_conflict() so no existing file is overwritten.

    Args:
        source_folder (str):    The folder being organised.
        filename (str):         The filename to move (not a full path).
        dest_folder_name (str): The name of the destination subfolder
                                (e.g. "Images", "Documents").

    Returns:
        str: dest_folder_name — returned so the caller can build a summary.

    TODO:
        1. Build the source path:
               source_path = os.path.join(source_folder, filename)
        2. Build the destination directory:
               dest_dir = os.path.join(source_folder, dest_folder_name)
        3. Create the destination directory if it does not exist:
               os.makedirs(dest_dir, exist_ok=True)
        4. Resolve any name conflict:
               destination_path = resolve_conflict(dest_dir, filename)
        5. Move the file:
               shutil.move(source_path, destination_path)
        6. Return dest_folder_name.
    """
    # --- Write your code here ---

    return dest_folder_name


def organise_folder(folder_path):
    """
    Organise all files in folder_path by moving them into typed subfolders.

    Args:
        folder_path (str): Absolute path to the folder to organise.

    Returns:
        dict: A summary mapping folder name -> count of files moved there.
              Example: {"Images": 5, "Documents": 2, "Other": 1}
              Returns {} if there are no files to move.

    TODO:
        1. Call list_files(folder_path) to get all filenames.
        2. If the list is empty, print "No files found to organise." and return {}.
        3. For each filename:
               a. Extract the extension:
                      ext = os.path.splitext(filename)[1].lower()
               b. Find the destination folder:
                      dest = get_destination_folder(ext)
               c. Move the file:
                      move_file(folder_path, filename, dest)
               d. Increment summary[dest] by 1 (use summary.get(dest, 0) + 1).
        4. Return the summary dict.
    """
    summary = {}

    # --- Write your code here ---

    return summary


# ---------------------------------------------------------------------------
# Display helper and entry point — already complete, no changes needed here
# ---------------------------------------------------------------------------

def print_summary(summary):
    """Print a formatted table of the organise results."""
    if not summary:
        return
    total = sum(summary.values())
    print("\n" + "=" * 35)
    print("  Organise complete")
    print("=" * 35)
    for folder, count in sorted(summary.items()):
        print(f"  {folder:<15}  {count:>4} file(s)")
    print("=" * 35)
    print(f"  Total moved     {total:>4} file(s)")
    print("=" * 35 + "\n")


def main():
    """Prompt for a target folder and run the organiser."""
    print("\n== File Organiser ==")
    raw = input("Folder to organise (press Enter for current directory): ").strip()
    folder = raw if raw else os.getcwd()

    if not os.path.isdir(folder):
        print(f"Error: '{folder}' is not a valid directory.")
        return

    print(f"\nOrganising: {folder}")
    summary = organise_folder(folder)
    print_summary(summary)


if __name__ == "__main__":
    main()
