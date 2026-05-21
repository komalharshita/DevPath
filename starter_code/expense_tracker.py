#Project:    Personal Expense Tracker
#Difficulty: Beginner
#Skills:     Python, CSV module, datetime module
#Time:       Low (a few hours)

# What you will build:
#     A command-line tool that lets you log daily expenses, view them in a
#     formatted table, see a monthly breakdown by category, and export a
#     filtered report to a new CSV file.

# How to run:
#     python expense_tracker.py

# Learning goals:
#     - Reading and writing CSV files
#     - Working with Python's datetime module
#     - Organising code into small, focused functions
#     - Building a simple interactive text menu

# Roadmap:
#     Step 1:  Project is already set up — run it and explore the menu
#     Step 2:  Complete add_expense() with category and amount validation
#     Step 3:  Complete list_expenses() to print a formatted table
#     Step 4:  Complete monthly_summary() to group totals by category
#     Step 5:  Complete filter_by_category() to search by category name
#     Step 6:  Complete export_to_csv() to save a filtered report
#     Step 7:  Test with at least 10 sample entries across different months
"""

import csv
import os
import shutil
from datetime import datetime


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# The file where all expense records are stored
DATA_FILE = "expenses.csv"

# Valid category names — entries outside this list are rejected
CATEGORIES = ["Food", "Transport", "Bills", "Entertainment", "Health", "Other"]

# Column headers written to the CSV on first run
CSV_HEADERS = ["date", "category", "amount", "note"]


# ---------------------------------------------------------------------------
# File initialisation
# ---------------------------------------------------------------------------

def initialize_file():
    """
    # Create the CSV file with headers if it does not already exist.
    # Called once at startup to ensure the file is ready for appending.
"""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
        print(f"Created new expense file: {DATA_FILE}")


# ---------------------------------------------------------------------------
# Core functions — complete the TODOs to make each one work
# ---------------------------------------------------------------------------
"""
from unicodedata import category


def add_expense(category, amount, note=""):
     
    # Validate and use the parameters
   if category not in CATEGORIES:
        print(f"Invalid category. Choose from: {CATEGORIES}")
        return
   if float(amount) <= 0:
        print("Amount must be a positive number.")
        return
        date = datetime.datetime.now().strftime("%Y-%m-%d")
   with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date, category, round(float(amount), 2), note])
        print("Expense added successfully.")

  
"""
    # Append one expense record to the CSV file.

from unicodedata import category


Args:
    category (str): Must be one of the strings in CATEGORIES.
    amount (float): The expense amount. Must be greater than zero.
    note (str):     Optional description (e.g. "lunch at work").

TODO:
    #     1. Check that category is in CATEGORIES.
    #        If not, print an error message and return without writing.
    #        Example: print(f"Invalid category. Choose from: {CATEGORIES}")

    #     2. Check that amount is greater than zero.
    #        If not, print an error message and return without writing.
    #        Example: print("Amount must be a positive number.")

    #     3. The date and file-write logic below is already complete.
    #        Once your validation passes, the row is saved automatically.
"""
#    --- Write your validation code above this line ---

pass

    # Get today's date in YYYY-MM-DD format
import csv
from datetime import datetime
date= datetime.now().strftime("%Y-%m-%d")

# General default values for demonstration/testing
amount = 0.0
note = ""

DATA_FILE = "expenses.csv"
CATEGORIES = ["Food", "Transport", "Utilities", "Entertainment", "Other"]
date = datetime.now().strftime("%Y-%m-%d")

    # Append the new row to the CSV file

with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date, category, round(float(amount), 2), note])

print(f"Expense of {amount:.2f} added under '{category}'.")


def read_all_expenses():
    """
    # Read every row from the CSV file and return them as a list of dicts

Returns:
        # list[dict]: Each dict has keys: date, category, amount, note.
        #             Amount is converted to float.
        #             Returns an empty list if the file has no data rows.

    # This function is used by list_expenses(), monthly_summary(), and
    # filter_by_category() — complete it once and it powers all three.

TODO:
        # 1. Open DATA_FILE for reading with csv.DictReader.
        # 2. Loop through each row and convert row["amount"] to float.
        # 3. Append each row dict to a results list.
        # 4. Return the list.

    # Example output:
[
          
            {"date": "2024-03-01", "category": "Food",
             "amount": 12.50, "note": "lunch"},
            ...
        ]
"""
    expenses = []


    return expenses


def list_expenses():
    """
    # Print every expense record in a readable table format.

    # Expected output:
    #     Date         Category       Amount    Note
    #     ----------   ------------   -------   --------------------
    #     2024-03-01   Food            12.50    lunch
    #     2024-03-02   Transport        3.20    bus ticket
    #     ...
    #     Total: 15.70 across 2 entries.

TODO:
        # 1. Call read_all_expenses() to get the data.
        # 2. If the list is empty, print "No expenses recorded yet." and return.
        # 3. Print the header row and a separator line.
        #    Tip: use Python's f-string padding: f"{'Date':<12}" left-aligns
        #    'Date' in a field 12 characters wide.
        # 4. Loop through expenses and print each row with consistent padding.
        # 5. After the table, print the total count and total amount.
"""
    expenses = read_all_expenses()

    # --- Write your display code here ---

    pass


def monthly_summary():
    """
    # Print the total amount spent per category for the current calendar month.

    # Expected output:
    #     Summary for March 2024
    #     ----------------------
    #     Food            45.20
    #     Transport       18.00
    #     Bills          120.00
    #     ----------------------
    #     Total          183.20

TODO:
         # 1. Get the current month and year with datetime.now().
         # 2. Call read_all_expenses() and filter rows where the date starts
         #    with the current year-month string (e.g. "2024-03").
         #    Tip: row["date"].startswith("2024-03")
         # 3. Build a dictionary mapping category -> total amount.
         #    Example: totals = {"Food": 0.0, "Transport": 0.0, ...}
         # 4. Loop through the filtered expenses and add each amount to
         #    the right category key.
         # 5. Print the month heading, each category with its total,
         #    and the grand total at the bottom.
"""
    now = datetime.now()
    current_month = now.strftime("%Y-%m")
    month_label = now.strftime("%B %Y")

    # --- Write your summary code here ---


pass


def filter_by_category(category):
    """
  # Return only the expenses that match the given category.

Args:
        # category (str): The category to search for (case-insensitive).

Returns:
        # list[dict]: Matching expense rows.

TODO:
        # 1. Call read_all_expenses() to get all rows.
        # 2. Filter rows where row["category"].lower() == category.lower().
        # 3. Return the filtered list.
"""
    # --- Write your filter code here ---

pass


def export_to_csv(output_filename, category=None):
    """
    # Write a report to a new CSV file.

Args:
        # output_filename (str): The name of the file to create.
        #                        Example: "march_food_report.csv"
        # category (str|None):  If provided, export only rows in that category.
        #                        If None, export everything.

TODO:
        #  1. If category is given, call filter_by_category(category) to get rows.
        #    Otherwise, call read_all_expenses() for all rows.
        # 2. If there are no rows, print a message and return.
        # 3. Open output_filename for writing with csv.DictWriter.
        # 4. Write the header row using writeheader().
        # 5. Write all data rows using writerows().
        # 6. Print a confirmation message with the number of rows exported.
    
 --- Write your export code here ---
  """
pass

  # ---------------------------------------------------------------------------
  # Menu and entry point — already complete, no changes needed here
  # ---------------------------------------------------------------------------

def show_menu():
    """Print the main menu and return the user's choice as a string."""
    print("\n" + "=" * 35)
    print("       Personal Expense Tracker")
    print("=" * 35)
    print("  1.  Add an expense")
    print("  2.  List all expenses")
    print("  3.  Monthly summary")
    print("  4.  Filter by category")
    print("  5.  Export to CSV")
    print("  6.  Quit")
    print("=" * 35)
    return input("  Choose (1-6): ").strip()


def prompt_category():
    # Show the category list and return the user's selection.
    print("\nCategories:")
    for i, cat in enumerate(CATEGORIES, start=1):
        print(f"  {i}. {cat}")
    return input("Enter category name: ").strip()

def initialize_file():
    pass

def add_expense():
    pass

def list_expenses():
    pass

def monthly_summary():
    pass

def main():
    """Run the expense tracker — the main application loop."""
    initialize_file()

    while True:
        choice = show_menu()

        if choice == "1":
            cat = prompt_category()
            try:
                amt = float(input("Amount (e.g. 12.50): ").strip())
            except ValueError:
                print("Please enter a valid number for the amount.")
                continue
            note = input("Note (optional, press Enter to skip): ").strip()
            add_expense(cat, amt, note)

        elif choice == "2":
            list_expenses()

        elif choice == "3":
            monthly_summary()

        elif choice == "4":
            cat = prompt_category()
            results = filter_by_category(cat)
            if not results:
                print(f"No expenses found for category '{cat}'.")
            else:
                print(f"\nFound {len(results)} expense(s) in '{cat}':")
                for row in results:
                    print(
                        f"  {row['date']}  {row['amount']:>8.2f}  {row['note']}"
                    )

        elif choice == "5":
            filename = input(
                "Output filename (e.g. report.csv): "
            ).strip()
            cat = input(
                "Filter by category? (press Enter to export all): "
            ).strip() or None
            export_to_csv(filename, category=cat)

        elif choice == "6":
            print("\nGoodbye. Keep tracking those expenses!\n")
            break

        else:
            print("Invalid choice. Enter a number between 1 and 6.")


if __name__ == "__main__":
    main()