"""
api_etl_pipeline.py
===================
Project:    API ETL Pipeline
Difficulty: Intermediate
Skills:     Python, requests, pandas, JSON handling, os module
Time:       Medium (2–5 days)

What you will build:
    Fetch data from a public API and automatically transform it into
    a clean, structured CSV dataset. The pipeline will validate API
    responses, normalize nested JSON data, handle missing values,
    generate summary statistics, and export the processed dataset
    for analytics, dashboards, or machine learning workflows.

    The final cleaned dataset and summary report are exported as files
    that can be reused for further data analysis projects.

How to run:
    pip install pandas requests
    python api_etl_pipeline.py

When prompted, enter a public API URL that returns JSON data.
A sample API endpoint is included at the bottom of this file
to help you test the project quickly without searching for APIs.

Learning goals:
    - Working with REST APIs using requests
    - Understanding JSON response structures
    - Extracting and normalizing nested API data
    - Converting JSON data into pandas DataFrames
    - Cleaning and transforming datasets
    - Exporting structured datasets to CSV files
    - Generating reusable summary reports

Roadmap:
    Step 1:  Run the script using the sample API endpoint
    Step 2:  Complete fetch_api_data() to retrieve JSON data safely
    Step 3:  Complete validate_response() to verify API responses
    Step 4:  Complete normalize_json() to flatten nested JSON data
    Step 5:  Complete create_dataframe() to build a pandas DataFrame
    Step 6:  Complete clean_data() to handle missing values and duplicates
    Step 7:  Complete export_csv() to save the processed dataset
    Step 8:  Complete generate_summary_report() to export statistics
    Step 9:  Test the pipeline with at least two different public APIs
"""
import os
import sys

try:
    import pandas as pd
    import requests
except ImportError:
    print("Required packages not installed.")
    print("Run: pip install pandas requests")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = "output"


# ---------------------------------------------------------------------------
# Setup helpers — already complete
# ---------------------------------------------------------------------------

def ensure_output_directory():
    """Create output directory if it does not already exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Core functions — complete the TODOs below
# ---------------------------------------------------------------------------

def fetch_api_data(url):
    """
    Fetch JSON data from a public API endpoint.

    Args:
        url (str): The API endpoint URL.

    Returns:
        dict | list | None:
            Parsed JSON response if successful, otherwise None.

    TODO:
        1. Validate that the URL starts with http:// or https://
           Example APIs:
              https://jsonplaceholder.typicode.com/users
              https://dummyjson.com/products
              https://dummyjson.com/users
        2. Send a GET request using:
               requests.get(url, timeout=10)
        3. Use response.raise_for_status() to detect HTTP errors
           such as 404 or 500 status codes.
        4. Convert the API response into JSON format using:
               response.json()
        5. Handle request exceptions using try/except blocks.
        6. Print a success message showing that the data was fetched.
        7. Return the parsed JSON response.
    """
    # --- Write your code here ---

    return None


def validate_response(data):
    """
    Validate the API response before processing.

    Args:
        data (dict | list): The parsed API response.

    Returns:
        bool:
            True if the response is valid, otherwise False.

    TODO:
        1. Check whether the response is empty.
        2. Ensure the response is either:
               - a dictionary
               - or a list
        3. Print a helpful validation message.
        4. Return True if the response is valid.
           Otherwise return False.
    """
    # --- Write your code here ---

    return False


def normalize_json(data):
    """
    Normalize and flatten nested JSON data.

    Args:
        data (dict | list): Raw JSON response.

    Returns:
        pd.DataFrame:
            Flattened DataFrame generated from JSON data.

    TODO:
        1. Use pd.json_normalize(data) to flatten nested JSON fields.
        2. Example:
               {
                   "name": "John",
                   "address": {
                       "city": "London"
                   }
               }
           becomes:
               name | address.city
        3. Handle both dictionary and list responses.
        4. Print the resulting column names.
        5. Return the normalized DataFrame.
    """
    # --- Write your code here ---

    return pd.DataFrame()


def create_dataframe(data):
    """
    Convert normalized JSON data into a pandas DataFrame.

    Args:
        data (dict | list): API response data.

    Returns:
        pd.DataFrame:
            Constructed pandas DataFrame.

    TODO:
        1. Create a DataFrame using pandas.
        2. Example:
               df = pd.DataFrame(data)
        3. Print dataset shape information using:
               df.shape
        4. Display the first few rows using:
               df.head()
        5. Return the DataFrame.
    """
    # --- Write your code here ---

    return pd.DataFrame()


def clean_data(df):
    """
    Clean the dataset by handling missing values and duplicates.

    Args:
        df (pd.DataFrame): Raw DataFrame.

    Returns:
        pd.DataFrame:
            Cleaned DataFrame.

    TODO:
        1. Identify missing values using:
               df.isnull().sum()
        2. Remove duplicate rows using:
               df.drop_duplicates()
        3. Handle missing values using:
               df.fillna()
        4. Standardize column names if necessary.
        5. Print dataset shape after cleaning.
        6. Return the cleaned DataFrame.
    """
    # --- Write your code here ---

    return df


def export_csv(df, filename="processed_data.csv"):
    """
    Export the processed dataset to a CSV file.

    Args:
        df (pd.DataFrame): Cleaned dataset.
        filename (str): Output CSV filename.

    Returns:
        str:
            Filepath of the exported CSV file.

    TODO:
        1. Build the full output path using:
               os.path.join()
        2. Export the dataset using:
               df.to_csv(output_path, index=False)
        3. Use index=False to prevent pandas from adding row numbers.
        4. Print a confirmation message after export.
        5. Return the output filepath.
    """
    # --- Write your code here ---

    return ""


def generate_summary_report(df):
    """
    Generate a summary report for the dataset.

    Args:
        df (pd.DataFrame): Cleaned dataset.

    TODO:
        1. Print dataset shape:
               df.shape
        2. Display column names and data types:
               df.dtypes
        3. Show missing value counts:
               df.isnull().sum()
        4. Generate descriptive statistics:
               df.describe()
        5. Display:
               - total rows
               - total columns
               - column names
               - missing value counts
               - numeric statistics
        6. Print the summary report clearly.
    """
    # --- Write your code here ---

    pass


# -----------------------------------------------------------------------------------
# Main pipeline — already complete and ready to run after completing core functions
# -----------------------------------------------------------------------------------

def run_pipeline(api_url):
    """
    Run the complete API ETL pipeline.

    Args:
        api_url (str): Public API endpoint URL.
    """
    ensure_output_directory()

    data = fetch_api_data(api_url) #fetch the data from the given url
    if not validate_response(data): #validate the response
        return

    normalized_df = normalize_json(data) # normalize nested json responses

    df = create_dataframe(normalized_df) #create a new dataframe with the normalized json

    cleaned_df = clean_data(df) #clean the created data table

    export_path = export_csv(cleaned_df) #export it to csv

    print(f"\nCSV exported successfully: {export_path}")

    generate_summary_report(cleaned_df) #generate summary for the exported csv


def main():
    """main function to test the pipeline if run directly"""
    print("\n" + "=" * 50)
    print("DevPath — API ETL Pipeline")
    print("=" * 50)

    api_url = input("\nEnter a public API URL: ").strip()

    if not api_url:
        print("No API URL provided. Exiting.")
        return

    run_pipeline(api_url)

    print("\nPipeline execution complete.\n")


if __name__ == "__main__":
    main()