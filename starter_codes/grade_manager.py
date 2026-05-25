"""
grade_manager.py
================
Project:    Student Grade Manager
Difficulty: Beginner
Skills:     Python, json module, os module, functions, dictionaries
Time:       Medium (a weekend)

What you will build:
    A Python application to store student names and their subject grades,
    calculate individual averages, assign letter grades, generate a class
    report, and save all data to a JSON file so nothing is lost on exit.

How to run:
    python grade_manager.py

Learning goals:
    - Structuring data with nested Python dictionaries
    - Reading from and writing to JSON files
    - Using functions to separate different responsibilities
    - Calculating averages and converting them to letter grades

Roadmap:
    Step 1:  Run the app and explore the menu — the skeleton works already
    Step 2:  Complete add_student() to store a new name in the data dict
    Step 3:  Complete add_grade() to attach a grade to a student's subject
    Step 4:  Complete calculate_average() to return a mean from a dict
    Step 5:  Complete get_letter_grade() to convert a number to A/B/C/D/F
    Step 6:  Complete print_student_report() to display one student's results
    Step 7:  Complete print_class_report() to loop through all students
    Step 8:  Test with at least five students and three subjects each
"""

import json
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# File where student data is saved between runs
DATA_FILE = "students.json"


# ---------------------------------------------------------------------------
# File helpers — already complete
# ---------------------------------------------------------------------------

def load_data():
    """
    Load student records from the JSON file.

    Returns:
        dict: The full student data dictionary.
              Returns an empty dict {} if the file does not exist yet.

    Data structure returned:
        {
            "Alice": {
                "grades": {
                    "Math": [88, 92, 76],
                    "English": [91, 85]
                }
            },
            "Bob": {
                "grades": {}
            }
        }
    """
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(students):
    """
    Save the current student dictionary to the JSON file.

    Args:
        students (dict): The full student data to save.

    This overwrites the existing file on every save, which is fine
    for a small dataset. Larger apps would use a proper database.
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=2)


# ---------------------------------------------------------------------------
# Core functions — complete the TODOs to make each one work
# ---------------------------------------------------------------------------

def add_student(students, name):
    """
    Add a new student entry to the students dictionary.

    Args:
        students (dict): The full student data dictionary (modified in place).
        name (str):      The student's name. Must not be empty.

    TODO:
        1. Check that name is not empty or just whitespace.
           If it is, print an error and return without changing students.
        2. Check whether name already exists as a key in students.
           If it does, print "Student already exists." and return.
        3. Add the new student with this exact structure:
               students[name] = {"grades": {}}
        4. Print a confirmation: f"Student '{name}' added."

    Example after adding "Alice":
        students = {
            "Alice": {"grades": {}}
        }
    """
    # --- Write your code here ---

    pass


def add_grade(students, name, subject, grade):
    """
    Add a numeric grade for one subject under one student.

    Grades are stored as a list so a student can have multiple grades
    per subject (e.g. three test scores for Math).

    Args:
        students (dict): The full student data dictionary.
        name (str):      The student's name.
        subject (str):   The subject name (e.g. "Math", "English").
        grade (float):   The grade value. Must be between 0 and 100.

    TODO:
        1. Check that name exists in students.
           If not, print f"Student '{name}' not found." and return.
        2. Check that grade is between 0 and 100 (inclusive).
           If not, print "Grade must be between 0 and 100." and return.
        3. If subject is not yet in students[name]["grades"], create it
           as an empty list: students[name]["grades"][subject] = []
        4. Append the grade to the subject list.
        5. Print a confirmation:
           f"Grade {grade} added to {name} / {subject}."

    Example after adding Math grade 88 for Alice:
        students["Alice"]["grades"]["Math"] = [88]
    """
    # --- Write your code here ---

    pass


def calculate_average(grades_list):
    """
    Calculate and return the mean of a list of numbers.

    Args:
        grades_list (list[float]): A list of numeric grades. May be empty.

    Returns:
        float: The average, rounded to 2 decimal places.
               Returns 0.0 if the list is empty (no grades yet).

    TODO:
        1. Handle the empty list case: return 0.0 immediately.
        2. Sum all values in grades_list.
        3. Divide by the number of values.
        4. Return the result rounded to 2 decimal places.
           Tip: round(value, 2)

    Examples:
        calculate_average([80, 90, 70])  ->  80.0
        calculate_average([100])         -> 100.0
        calculate_average([])            ->   0.0
    """
    # --- Write your code here ---

    return 0.0


def get_letter_grade(average):
    """
    Convert a numeric average into a letter grade.

    Args:
        average (float): A number between 0 and 100.

    Returns:
        str: One of "A", "B", "C", "D", or "F".

    Grading scale:
        90 and above  ->  A
        80 to 89      ->  B
        70 to 79      ->  C
        60 to 69      ->  D
        Below 60      ->  F

    TODO:
        Write a series of if/elif/else checks using the scale above.
        Return the correct letter for the given average.

    Examples:
        get_letter_grade(95.0)  ->  "A"
        get_letter_grade(82.5)  ->  "B"
        get_letter_grade(55.0)  ->  "F"
    """
    # --- Write your code here ---

    return "F"


def print_student_report(students, name):
    """
    Print a formatted grade report for one student.

    Args:
        students (dict): The full student data dictionary.
        name (str):      The student to print the report for.

    Expected output format:
        ----------------------------------------
        Student: Alice
        ----------------------------------------
        Subject         Grades          Average  Grade
        Math            88, 92, 76       85.33   B
        English         91, 85           88.00   B
        Science         70               70.00   C
        ----------------------------------------
        Overall Average: 81.11   Overall Grade: B

    TODO:
        1. Check that name exists in students. If not, print an error.
        2. Print the header with the student's name.
        3. Get the grades dict: students[name]["grades"]
        4. If the grades dict is empty, print "No grades recorded." and return.
        5. Loop through each subject and its list of grades.
           For each subject:
             a. Format the grades list as a comma-separated string.
             b. Call calculate_average() to get the subject average.
             c. Call get_letter_grade() with the average.
             d. Print the row with consistent column widths.
        6. After the loop, calculate the overall average across all grades
           (flatten all grade lists into one list) and print it.
    """
    # --- Write your code here ---

    pass


def print_class_report(students):
    """
    Print a summary report for every student in the class.

    Args:
        students (dict): The full student data dictionary.

    Expected output format:
        ============================================================
        CLASS REPORT
        ============================================================
        Student         Overall Avg    Grade   Subjects
        Alice              81.11       B       Math, English, Science
        Bob                74.33       C       Math, English
        ...
        ============================================================
        Class average: 77.72

    TODO:
        1. If students is empty, print "No students registered." and return.
        2. Print the header.
        3. Loop through each student.
           For each student:
             a. Collect all their grades into a single flat list.
             b. Calculate the overall average.
             c. Get the letter grade.
             d. Get the list of subject names they have grades for.
             e. Print the summary row.
        4. After the loop, calculate and print the class-wide average
           (average of all individual overall averages).
    """
    # --- Write your code here ---

    pass


def list_students(students):
    """
    Print the names of all registered students.

    Args:
        students (dict): The full student data dictionary.

    TODO:
        1. If students is empty, print "No students registered yet."
        2. Otherwise, print each student's name with a number prefix:
               1. Alice
               2. Bob
    """
    # --- Write your code here ---

    pass


# ---------------------------------------------------------------------------
# Menu and entry point — already complete, no changes needed here
# ---------------------------------------------------------------------------

def show_menu():
    """Print the main menu and return the user's choice."""
    print("\n" + "=" * 40)
    print("        Student Grade Manager")
    print("=" * 40)
    print("  1.  Add student")
    print("  2.  Add grade")
    print("  3.  View student report")
    print("  4.  View class report")
    print("  5.  List all students")
    print("  6.  Quit")
    print("=" * 40)
    return input("  Choose (1-6): ").strip()


def main():
    """Run the grade manager application loop."""
    students = load_data()
    print(f"Loaded {len(students)} student(s) from {DATA_FILE}.")

    while True:
        choice = show_menu()

        if choice == "1":
            name = input("Student name: ").strip()
            add_student(students, name)
            save_data(students)

        elif choice == "2":
            name = input("Student name: ").strip()
            subject = input("Subject (e.g. Math): ").strip()
            try:
                grade = float(input("Grade (0-100): ").strip())
            except ValueError:
                print("Please enter a valid number for the grade.")
                continue
            add_grade(students, name, subject, grade)
            save_data(students)

        elif choice == "3":
            name = input("Student name: ").strip()
            print_student_report(students, name)

        elif choice == "4":
            print_class_report(students)

        elif choice == "5":
            list_students(students)

        elif choice == "6":
            print("\nGoodbye!\n")
            break

        else:
            print("Invalid choice. Enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
