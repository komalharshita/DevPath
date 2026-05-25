"""
data_report.py
==============
Project:    Data Analysis Report Generator
Difficulty: Intermediate
Skills:     Python, pandas, matplotlib, os module
Time:       High (a week or more)

What you will build:
    Upload any CSV file and automatically generate a summary report:
    dataset shape, column types, missing value counts, descriptive
    statistics for numeric columns, and bar charts for categorical columns.
    The final report is exported as a formatted text file.

How to run:
    pip install pandas matplotlib
    python data_report.py

When prompted, enter the path to any CSV file on your machine.
A sample CSV is included at the bottom of this file as a string —
save it to sample_data.csv to test without needing your own file.

Learning goals:
    - Loading and inspecting CSV files with pandas DataFrames
    - Understanding DataFrame structure: shape, dtypes, isnull
    - Computing descriptive statistics: mean, median, std, min, max
    - Generating bar charts with matplotlib
    - Writing formatted reports to text files

Roadmap:
    Step 1:  Run the script with sample_data.csv and read the output
    Step 2:  Complete load_csv() to load a file with error handling
    Step 3:  Complete print_overview() to display shape and column types
    Step 4:  Complete print_null_summary() to count missing values
    Step 5:  Complete print_statistics() for numeric column stats
    Step 6:  Complete generate_bar_chart() to save a chart as PNG
    Step 7:  Complete export_report() to write all results to a text file
    Step 8:  Test on at least two different CSV files
"""

import os
import sys

# pandas and matplotlib must be installed: pip install pandas matplotlib
try:
    import pandas as pd
    import matplotlib
    matplotlib.use("Agg")   # Use non-interactive backend (no display required)
    import matplotlib.pyplot as plt
except ImportError:
    print("Required packages not installed.")
    print("Run: pip install pandas matplotlib")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Directory where generated chart images are saved
CHARTS_DIR = "charts"

# Directory where the text report is saved
REPORTS_DIR = "reports"


# ---------------------------------------------------------------------------
# Setup helpers — already complete
# ---------------------------------------------------------------------------

def ensure_directories():
    """Create output directories if they do not already exist."""
    os.makedirs(CHARTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Core functions — complete the TODOs below
# ---------------------------------------------------------------------------

def load_csv(filepath):
    """
    Load a CSV file into a pandas DataFrame with error handling.

    Args:
        filepath (str): The path to the CSV file to load.

    Returns:
        pd.DataFrame | None: The loaded DataFrame, or None if loading fails.

    TODO:
        1. Check whether the file exists using os.path.exists(filepath).
           If it does not, print a clear error message and return None.
        2. Check whether the file ends with ".csv" (case-insensitive).
           If it does not, print an error and return None.
        3. Use pd.read_csv(filepath) inside a try/except block.
           If any exception occurs, print the error and return None.
        4. After loading, print a success message showing the filepath,
           number of rows, and number of columns.
           Example: print(f"Loaded {len(df)} rows, {len(df.columns)} columns.")
        5. Return the DataFrame.

    Example usage:
        df = load_csv("sales_data.csv")
        if df is None:
            return  # Stop if loading failed
    """
    # --- Write your code here ---

    return None


def print_overview(df):
    """
    Print a high-level overview of the DataFrame.

    Args:
        df (pd.DataFrame): The loaded dataset.

    Expected output format:
        DATASET OVERVIEW
        ================
        Rows:     1000
        Columns:  8

        Column Name        Data Type
        -----------------  ----------
        name               object
        age                int64
        salary             float64
        department         object
        ...

    TODO:
        1. Print the number of rows with df.shape[0].
        2. Print the number of columns with df.shape[1].
        3. Print a two-column table of column names and their dtypes.
           Access column names with df.columns.
           Access data types with df.dtypes[col_name].
           Use consistent column widths for alignment.
    """
    print("\n" + "=" * 50)
    print("DATASET OVERVIEW")
    print("=" * 50)

    # --- Write your code here ---

    pass


def print_null_summary(df):
    """
    Print the count of missing (null) values for each column.

    Args:
        df (pd.DataFrame): The loaded dataset.

    Expected output format:
        MISSING VALUES
        ==============
        Column Name        Missing    Percent
        -----------------  -------    -------
        name                     0      0.00%
        age                     12      1.20%
        salary                  34      3.40%

        Total missing values: 46

    TODO:
        1. Use df.isnull().sum() to get the count of nulls per column.
        2. Calculate the percentage of nulls per column:
               percent = (null_count / len(df)) * 100
        3. Print the header row and separator.
        4. Loop through each column. Print the column name, null count,
           and percentage. Use f-string formatting for alignment.
        5. After the table, print the total number of missing values:
               df.isnull().sum().sum()
        6. If there are no missing values at all, print a positive message:
               "No missing values found."
    """
    print("\n" + "=" * 50)
    print("MISSING VALUES")
    print("=" * 50)

    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()

    # --- Write your code here ---

    pass


def print_statistics(df):
    """
    Print descriptive statistics for every numeric column.

    Args:
        df (pd.DataFrame): The loaded dataset.

    Expected output format:
        NUMERIC COLUMN STATISTICS
        =========================
        Column: age
          Count :     988
          Mean  :   35.42
          Median:   34.00
          Std   :   10.23
          Min   :   18.00
          Max   :   65.00

        Column: salary
          ...

    TODO:
        1. Select only numeric columns: df.select_dtypes(include="number")
        2. If there are no numeric columns, print a message and return.
        3. For each numeric column:
             a. Use df[col].count()           for the count of non-null values
             b. Use df[col].mean()            for the mean
             c. Use df[col].median()          for the median
             d. Use df[col].std()             for standard deviation
             e. Use df[col].min()             for the minimum
             f. Use df[col].max()             for the maximum
        4. Print each stat on its own line with consistent formatting.
           Round all values to 2 decimal places.
    """
    print("\n" + "=" * 50)
    print("NUMERIC COLUMN STATISTICS")
    print("=" * 50)

    # --- Write your code here ---

    pass


def generate_bar_chart(df, column):
    """
    Generate and save a bar chart of value counts for one column.

    Args:
        df (pd.DataFrame): The loaded dataset.
        column (str):      The column to chart.

    Returns:
        str | None: The filepath of the saved chart image, or None on failure.

    Expected behaviour:
        - Counts the occurrences of each unique value in the column.
        - Plots a bar chart with value labels on each bar.
        - Saves the chart as a PNG to CHARTS_DIR/<column>_chart.png.
        - Returns the filepath.

    TODO:
        1. Validate that column exists in df.columns.
           Return None with an error message if not.
        2. Use df[column].value_counts() to count each unique value.
           Store this as a pandas Series — index = values, data = counts.
        3. Create a matplotlib figure: fig, ax = plt.subplots(figsize=(10, 5))
        4. Plot the bar chart:
               value_counts.plot(kind="bar", ax=ax, color="#4f6ef7", edgecolor="white")
        5. Set chart labels:
               ax.set_title(f"Distribution of {column}")
               ax.set_xlabel(column)
               ax.set_ylabel("Count")
               plt.xticks(rotation=45, ha="right")
        6. Add count labels on top of each bar:
               for bar in ax.patches:
                   ax.text(
                       bar.get_x() + bar.get_width() / 2,
                       bar.get_height() + 0.1,
                       str(int(bar.get_height())),
                       ha="center", va="bottom", fontsize=9
                   )
        7. Use plt.tight_layout() to prevent label clipping.
        8. Build the output path: os.path.join(CHARTS_DIR, f"{column}_chart.png")
        9. Save: plt.savefig(output_path, dpi=150)
        10. Close: plt.close(fig)
        11. Print a confirmation and return the output path.
    """
    # --- Write your code here ---

    return None


def export_report(df, filepath, report_lines):
    """
    Write the analysis report to a text file.

    Args:
        df (pd.DataFrame):   The loaded dataset.
        filepath (str):      Path to the original CSV file.
        report_lines (list): List of strings to write to the report.

    Returns:
        str: The path to the saved report file.

    TODO:
        1. Build the report filename from the original CSV name:
               base = os.path.splitext(os.path.basename(filepath))[0]
               report_name = f"{base}_report.txt"
               report_path = os.path.join(REPORTS_DIR, report_name)
        2. Add a report header at the start of report_lines:
               - "DevPath Data Analysis Report"
               - "File: " + filepath
               - "Generated: " + datetime.now().strftime(...)
               - A divider line
        3. Open report_path for writing.
        4. Write each line in report_lines followed by a newline.
        5. Print a confirmation with the full report path.
        6. Return report_path.
    """
    # --- Write your code here ---

    return ""


def get_column_choice(df, prompt):
    """
    Ask the user to choose a column name and validate it.

    Args:
        df (pd.DataFrame): The dataset (used to validate the column name).
        prompt (str):      The input prompt to display.

    Returns:
        str | None: A valid column name, or None if the user skips.

    TODO:
        1. Print the list of available columns for the user to see.
        2. Use input() to ask for a column name using prompt.
        3. If the user presses Enter with no input, return None.
        4. Check whether the input is in df.columns.
           If not, print an error and return None.
        5. Return the valid column name.
    """
    print("\nAvailable columns:", list(df.columns))

    # --- Write your code here ---

    return None


# ---------------------------------------------------------------------------
# Main analysis pipeline — already complete
# ---------------------------------------------------------------------------

def run_analysis(filepath):
    """
    Run the full analysis pipeline for one CSV file.

    Args:
        filepath (str): Path to the CSV file to analyse.
    """
    ensure_directories()

    # Step 1: Load the data
    df = load_csv(filepath)
    if df is None:
        return

    # Step 2: Print and collect overview
    print_overview(df)

    # Step 3: Null value summary
    print_null_summary(df)

    # Step 4: Numeric statistics
    print_statistics(df)

    # Step 5: Optionally generate a bar chart for a categorical column
    print("\n" + "=" * 50)
    print("BAR CHART GENERATION")
    print("=" * 50)
    col = get_column_choice(df, "Enter a column name to chart (Enter to skip): ")
    if col:
        chart_path = generate_bar_chart(df, col)
        if chart_path:
            print(f"Chart saved: {chart_path}")

    # Step 6: Export report
    print("\n" + "=" * 50)
    export_choice = input("Export a text report? (y/n): ").strip().lower()
    if export_choice == "y":
        # Collect printed output into a list for the report
        report_lines = [
            f"File: {filepath}",
            f"Rows: {df.shape[0]}",
            f"Columns: {df.shape[1]}",
            "",
            "Column Types:",
        ]
        for col_name in df.columns:
            report_lines.append(f"  {col_name}: {df.dtypes[col_name]}")

        report_path = export_report(df, filepath, report_lines)
        if report_path:
            print(f"Report saved: {report_path}")


def main():
    """Entry point — ask for a CSV filepath and run the analysis."""
    print("\n" + "=" * 50)
    print("   DevPath — Data Analysis Report Generator")
    print("=" * 50)

    filepath = input("\nEnter path to your CSV file: ").strip()
    if not filepath:
        print("No file path provided. Exiting.")
        return

    run_analysis(filepath)
    print("\nAnalysis complete.\n")


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Sample data — save this to sample_data.csv to test the script
# ---------------------------------------------------------------------------
# name,department,age,salary,years_experience,city
# Alice,Engineering,30,85000,6,London
# Bob,Marketing,25,52000,2,Manchester
# Carol,Engineering,35,92000,10,London
# David,HR,28,48000,3,Birmingham
# Eve,Engineering,40,110000,15,London
# Frank,Marketing,32,61000,7,Leeds
# Grace,HR,27,45000,1,Manchester
# Henry,Engineering,45,125000,20,London
# Iris,Marketing,29,55000,4,Birmingham
# Jack,HR,31,50000,5,Leeds
# Karen,Engineering,38,98000,13,London
# Leo,Marketing,26,53000,2,Manchester
