"""
Project:    Course Progress Tracker
Difficulty: Beginner
Skills:     Python, JSON
Time:       Low (a few hours)

What you will build:
    A command-line tool that tracks your progress through a list of
    courses. Each course can be marked as not-started, in-progress, or
    completed, and the tool reports your overall completion percentage.

How to run:
    python course_tracker.py
    python course_tracker.py add "SQL Essentials"
    python course_tracker.py complete "SQL Essentials"

Learning goals:
    - Storing and loading data as JSON
    - Building a simple command-line interface
    - Handling user input and missing files
    - Keeping state consistent across runs

Roadmap:
    Step 1:  Run the project to explore the CLI menu
    Step 2:  Complete load_courses() to read courses from disk
    Step 3:  Complete save_courses() to persist changes
    Step 4:  Complete add_course() and mark_status() to update the list
    Step 5:  Complete show_progress() to print the completion summary
"""

import json
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Where the course list is stored on disk
DATA_FILE = os.path.join(os.path.dirname(__file__), "courses.json")

# Allowed statuses for a course
STATUSES = ("not-started", "in-progress", "completed")


# ---------------------------------------------------------------------------
# Storage helpers — complete each function below
# ---------------------------------------------------------------------------

def load_courses():
    """
    Read the course list from DATA_FILE.

    Returns a list of dicts like:
        [{"title": "SQL Essentials", "status": "in-progress"}]

    Returns an empty list if the file does not exist or is not valid JSON.
    """
    pass


def save_courses(courses):
    """
    Write `courses` to DATA_FILE as pretty-printed JSON.
    """
    pass


# ---------------------------------------------------------------------------
# Commands — complete each function below
# ---------------------------------------------------------------------------

def add_course(courses, title):
    """
    Append a new not-started course to the list and return it.

    If a course with the same title (case-insensitive) already exists,
    print a message and leave the list unchanged.
    """
    pass


def mark_status(courses, title, status):
    """
    Set the status of the matching course to `status`.

    Returns True if the course was found and updated, False otherwise.
    """
    pass


def show_progress(courses):
    """
    Print each course with its status, then a summary line:

        SQL Essentials   [in-progress]
        React Basics     [completed]

        Completed: 1/2 (50.0%)
    """
    pass


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    courses = load_courses()

    print("=" * 40)
    print("    Course Progress Tracker")
    print("=" * 40)

    command = input("\nCommand (list, add, complete, progress, quit): ").strip().lower()

    if command == "list":
        for course in courses:
            print(f"{course['title']}   [{course['status']}]")
    elif command == "add":
        title = input("Course title: ").strip()
        add_course(courses, title)
        save_courses(courses)
    elif command == "complete":
        title = input("Course title: ").strip()
        mark_status(courses, title, "completed")
        save_courses(courses)
    elif command == "progress":
        show_progress(courses)
    elif command == "quit":
        print("Goodbye!")
        return
    else:
        print("Unknown command.")

    save_courses(courses)


if __name__ == "__main__":
    main()
