/*
Project:    CSV Data Analyzer
Difficulty: Intermediate
Skills:     Rust, csv crate, std::fs, std::io
Time:       High (several days)

What you will build:
    A command-line tool that reads a CSV file and generates basic
    statistics like min, max, mean, and count per column. Displays
    a formatted summary table in the terminal.

How to run:
    cargo run -- data.csv

Learning goals:
    - Reading CSV files using the csv crate
    - Rust error handling with Result and the ? operator
    - Working with HashMaps and Vectors
    - Formatting and displaying tabular data

Roadmap:
    Step 1:  Project is already set up — run it with a sample CSV
    Step 2:  Complete readCsv() to parse the file into rows
    Step 3:  Complete getNumericColumns() to detect number columns
    Step 4:  Complete calculateStats() to compute min, max, mean
    Step 5:  Complete countMissing() to find empty values
    Step 6:  Complete printSummary() to display the results table
    Step 7:  Test with CSV files of different sizes and column types
*/

use std::collections::HashMap;
use std::env;
use std::fs::File;
use std::io::{self, BufReader};

// ---------------------------------------------------------------------------
// Data structures
// ---------------------------------------------------------------------------

// Holds computed statistics for a single numeric column
struct ColumnStats {
    min: f64,
    max: f64,
    mean: f64,
    count: usize,
    missing: usize,
}

// ---------------------------------------------------------------------------
// Core functions — complete the TODOs to make each one work
// ---------------------------------------------------------------------------

/// Read a CSV file and return headers and rows separately.
///
/// Returns a tuple of (headers, rows) where:
///   headers is a Vec<String> of column names
///   rows is a Vec<Vec<String>> of data rows
///
/// TODO:
/// 1. Add csv = "1.2" to your Cargo.toml dependencies
/// 2. Open the file using File::open(path)?
/// 3. Create a csv::Reader from the file
/// 4. Read headers using rdr.headers()?
/// 5. Loop through records and collect into rows vector
/// 6. Return (headers, rows) as a tuple
fn read_csv(path: &str) -> Result<(Vec<String>, Vec<Vec<String>>), Box<dyn std::error::Error>> {
    let headers: Vec<String> = Vec::new();
    let rows: Vec<Vec<String>> = Vec::new();

    // --- Write your CSV reading code here ---

    Ok((headers, rows))
}

/// Detect which column indices contain numeric data.
/// A column is numeric if more than 50% of its values parse as f64.
///
/// Returns a Vec of column indices that are numeric.
///
/// TODO:
/// 1. Loop through each column index
/// 2. For each column collect all values from all rows
/// 3. Try parsing each value as f64
/// 4. If more than half parse successfully mark as numeric
/// 5. Return the list of numeric column indices
fn get_numeric_columns(rows: &Vec<Vec<String>>, header_count: usize) -> Vec<usize> {
    let mut numeric_cols: Vec<usize> = Vec::new();

    // --- Write your column detection code here ---

    numeric_cols
}

/// Calculate min, max, and mean for a single numeric column.
///
/// TODO:
/// 1. Loop through all rows and get the value at col_index
/// 2. Skip empty values and count them as missing
/// 3. Parse non-empty values as f64
/// 4. Track min and max using f64::min() and f64::max()
/// 5. Sum all values and divide by count for mean
/// 6. Return a ColumnStats struct with all computed values
fn calculate_stats(rows: &Vec<Vec<String>>, col_index: usize) -> ColumnStats {

    // --- Write your stats calculation code here ---

    ColumnStats {
        min: 0.0,
        max: 0.0,
        mean: 0.0,
        count: 0,
        missing: 0,
    }
}

/// Print a formatted summary table for all numeric columns.
///
/// TODO:
/// 1. Print a header row with column names
/// 2. Print a separator line
/// 3. For each numeric column print its stats in aligned columns
/// 4. Format numbers to 2 decimal places
/// 5. Print total row count at the bottom
fn print_summary(
    headers: &Vec<String>,
    numeric_cols: &Vec<usize>,
    stats: &HashMap<usize, ColumnStats>,
    total_rows: usize,
) {

    // --- Write your summary printing code here ---

}

// ---------------------------------------------------------------------------
// Entry point — already complete, no changes needed here
// ---------------------------------------------------------------------------

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        eprintln!("Usage: cargo run -- <csv_file>");
        std::process::exit(1);
    }

    let path = &args[1];
    println!("Analyzing: {}\n", path);

    let (headers, rows) = match read_csv(path) {
        Ok(data) => data,
        Err(e) => {
            eprintln!("Error reading CSV: {}", e);
            std::process::exit(1);
        }
    };

    println!("Rows: {}  |  Columns: {}\n", rows.len(), headers.len());

    let numeric_cols = get_numeric_columns(&rows, headers.len());
    let mut stats: HashMap<usize, ColumnStats> = HashMap::new();

    for col_index in &numeric_cols {
        stats.insert(*col_index, calculate_stats(&rows, *col_index));
    }

    print_summary(&headers, &numeric_cols, &stats, rows.len());
}