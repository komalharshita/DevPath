"""
Project:    Password Strength Checker
Difficulty: Beginner
Skills:     Python, Regex
Time:       Low (a few hours)

What you will build:
    A command-line tool that checks the strength of a password based on
    length, use of uppercase/lowercase letters, numbers, and special symbols.
    The tool rates each password as Weak, Medium, or Strong.

How to run:
    python password_checker.py

Learning goals:
    - Working with Python strings and character classes
    - Using the re module for pattern matching
    - Building a simple scoring algorithm
    - Writing clear user-facing feedback

Roadmap:
    Step 1:  Project is already set up — run it and explore the menu
    Step 2:  Complete check_length() to score based on password length
    Step 3:  Complete check_uppercase() to detect uppercase letters
    Step 4:  Complete check_lowercase() to detect lowercase letters
    Step 5:  Complete check_digits() to detect numeric characters
    Step 6:  Complete check_symbols() to detect special characters
    Step 7:  Complete evaluate_strength() to combine all scores
"""

import re


# ---------------------------------------------------------------------------
# Scoring configuration
# ---------------------------------------------------------------------------

# Each criterion contributes points toward the final strength score
WEIGHTS = {
    "length":    2,
    "uppercase": 2,
    "lowercase": 1,
    "digits":    2,
    "symbols":   3,
}

# Thresholds for strength labels
WEAK_THRESHOLD = 4
STRONG_THRESHOLD = 8


# ---------------------------------------------------------------------------
# Individual checks — complete each function below
# ---------------------------------------------------------------------------

def check_length(password):
    """
    Score based on password length.

    Rules:
        < 8 characters  -> 0 points
        8-11 characters -> 1 point
        12+ characters  -> 2 points
    """
    pass


def check_uppercase(password):
    """
    Return WEIGHTS["uppercase"] if the password contains at least one
    uppercase letter (A-Z), otherwise return 0.
    """
    pass


def check_lowercase(password):
    """
    Return WEIGHTS["lowercase"] if the password contains at least one
    lowercase letter (a-z), otherwise return 0.
    """
    pass


def check_digits(password):
    """
    Return WEIGHTS["digits"] if the password contains at least one
    digit (0-9), otherwise return 0.
    """
    pass


def check_symbols(password):
    """
    Return WEIGHTS["symbols"] if the password contains at least one
    non-alphanumeric character (e.g. !, @, #, $, %), otherwise return 0.
    """
    pass


# ---------------------------------------------------------------------------
# Combined scoring
# ---------------------------------------------------------------------------

def evaluate_strength(password):
    """
    Run all checks, sum the score, and return a tuple:
        (total_score, label)

    Label is one of: "Weak", "Medium", "Strong"

    Scoring:
        0-4  -> Weak
        5-7  -> Medium
        8-10 -> Strong
    """
    pass


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    """Prompt the user for a password and display its strength."""
    print("=" * 40)
    print("    Password Strength Checker")
    print("=" * 40)

    password = input("\nEnter a password to check: ")

    score, label = evaluate_strength(password)

    print(f"\nScore: {score}/10")
    print(f"Strength: {label}")

    if label == "Weak":
        print("Tip: Use at least 12 characters with uppercase, lowercase, digits, and symbols.")
    elif label == "Medium":
        print("Tip: Add more variety — try mixing in symbols and making it longer.")
    else:
        print("Great password! It meets all security recommendations.")


if __name__ == "__main__":
    main()
