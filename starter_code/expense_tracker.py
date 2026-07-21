"""
Project:     Personal Expense Tracker
Difficulty: Beginner
Skills:      Python, CSV module, datetime module
Time:        Low (a few hours)

What you will build:
    A command-line tool that lets you log daily expenses, view them in a
    formatted table, see a monthly breakdown by category, and export a
    filtered report to a new CSV file.

How to run:
    python expense_tracker.py
"""

import csv
import os
from datetime import datetime

# ---------------------------------------------------------------------->
# Configuration
# ---------------------------------------------------------------------->

# The file where all expense records are stored
DATA_FILE = "expenses.csv"

# Valid category names — entries outside this list are rejected
CATEGORIES = ["Food", "Transport", "Bills", "Entertainment", "Health", "Other"]

# Column headers written to the CSV on first run
CSV_HEADERS = ["date", "category", "amount", "note"]


# ---------------------------------------------------------------------->
# File initialisation
# ---------------------------------------------------------------------->

def initialize_file():
    """
    Create the CSV file with headers if it does not already exist.
    Called once at startup to ensure the file is ready for appending.
    """
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
        print(f"Created new expense file: {DATA_FILE}")


# ---------------------------------------------------------------------->
# Core functions — fully implemented
# ---------------------------------------------------------------------->

def add_expense(category, amount, note=""):
    """
    Append one expense record to the CSV file with robust input validation.
    """
    # 1. Validation: Check that the category is valid
    if category not in CATEGORIES:
        print(f"Invalid category. Choose from: {CATEGORIES}")
        return

    # 2. Validation: Check that the amount is positive
    if amount <= 0:
        print("Amount must be a positive number.")
        return

    # 3. Save to file
    date = datetime.now().strftime("%Y-%m-%d")
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date, category, round(float(amount), 2), note])

    print(f"Expense of {amount:.2f} added under '{category}'.")


def read_all_expenses():
    """
    Read every row from the CSV file and return them as a list of dicts.
    """
    expenses = []
    if not os.path.exists(DATA_FILE):
        return expenses

    try:
        with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Convert row metrics accurately
                    row["amount"] = float(row["amount"])
                    expenses.append(row)
                except (ValueError, KeyError):
                    continue  # Skip malformed lines safely
    except Exception as e:
        print(f"Error reading file: {e}")

    return expenses


def list_expenses():
    """
    Print every expense record in a clear, formatted readable table layout.
    """
    expenses = read_all_expenses()

    # --- Write your display code here ---
import csv

def list_all_expenses():
    try:
        with open("expenses.csv", "r") as file:
            reader = csv.DictReader(file)
            print("\n=== All Expenses ===")
            has_data = False
            # Print header row
            print(f"{'Date':<12} | {'Category':<12} | {'Amount':<10} | {'Note'}")
            print("-" * 55)
            for row in reader:
                # Normalize category for consistency
                category = row['category'].strip().capitalize()
                print(f"{row['date']:<12} | {category:<12} | {row['amount']:<10} | {row['note']}")
                has_data = True
            if not has_data:
                print("No expenses recorded yet.")
    except FileNotFoundError:
        print("No expense file found. Please add an expense first.")


def monthly_summary():
    """
    Print the total amount spent per category for the current calendar month.
    """
    now = datetime.now()
    current_month = now.strftime("%Y-%m")
    month_label = now.strftime("%B %Y")

    expenses = read_all_expenses()
    
    # Filter for items that belong to the current year-month pattern
    filtered_expenses = [row for row in expenses if row["date"].startswith(current_month)]

    print(f"\nSummary for {month_label}")
    print("-" * 35)


    for row in filtered_expenses:
        if cat in totals:
            totals[cat] += row["amount"]
            totals["Other"] += row["amount"]

    for category, amount in totals.items():
        if amount > 0:  # Only display active categories with entries
            print(f"{category:<20} ${amount:>10.2f}")

    print(f"{'Total':<20} ${grand_total:>10.2f}")

def filter_by_category(category):
    """
    Return only the expenses that match the given category name (case-insensitive).
    expenses = read_all_expenses()
    return [row for row in expenses if row["category"].lower() == category.lower()]

def export_to_csv(output_filename, category=None):
    Write a filtered/unfiltered report data structure to a brand new CSV file.
    """
    if category:
        data_to_export = filter_by_category(category)
        data_to_export = read_all_expenses()

    if not data_to_export:
        print("No data available to export.")
        return
    try:
        with open(output_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(data_to_export)
        
        print(f"Successfully exported {len(data_to_export)} records to '{output_filename}'.")
    except Exception as e:
        print(f"Failed to export file: {e}")


# --------------------------------------------------------------------->
# Menu and entry point — complete execution flow
# --------------------------------------------------------------------->

def show_menu():
    """Print the main menu and return the user's choice as a string."""
    print("\n" + "=" * 35)
    print("        Personal Expense Tracker")
    print("=" * 35)
    print("  1.  Add an expense")
    print("  2.  List all expenses")
    print("  3.  Monthly summary")
    print("  4.  Filter by category")
    print("  6.  Quit")
    print("=" * 35)
    return input("  Choose (1-6): ").strip()


def prompt_category():
    """Show the category list and return the user's selection."""
    print("\nCategories:")
    for i, cat in enumerate(CATEGORIES, start=1):
        print(f"  {i}. {cat}")
    return input("Enter category name: ").strip()


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
                print(f"  {'Date':<12} {'Amount':<10} {'Note'}")
                print("  " + "-" * 40)
                for row in results:
                    print(f"  {row['date']:<12} ${row['amount']:<9.2f} {row['note']}")

        elif choice == "5":
            filename = input("Output filename (e.g. report.csv): ").strip()
            if not filename:
                print("Filename cannot be blank.")
                continue
            cat = input("Filter by category? (press Enter to export all): ").strip() or None
            export_to_csv(filename, category=cat)

        elif choice == "6":
            print("\nGoodbye. Keep tracking those expenses!\n")
            break

        else:
            print("Invalid choice. Enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
