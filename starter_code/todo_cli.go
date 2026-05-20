/*
Project:    CLI Task Automation Tool
Difficulty: Intermediate
Skills:     Go, os package, filepath package, flag package
Time:       Medium (a weekend)

What you will build:
    A command-line tool that organizes files in a folder by extension,
    batch renames files using patterns, deletes empty folders, and logs
    all operations to a text file.

How to run:
    go run todo_cli.go --dir ./sample_folder

Learning goals:
    - Parsing CLI arguments using the flag package
    - Working with files and folders using os and filepath
    - Writing logs to a text file
    - Organizing code into small focused functions

Roadmap:
    Step 1:  Project is already set up — run it and explore the output
    Step 2:  Complete scanDirectory() to list all files in a folder
    Step 3:  Complete groupByExtension() to group files by their type
    Step 4:  Complete moveFiles() to move files into correct subfolders
    Step 5:  Complete deleteEmptyFolders() to clean up empty directories
    Step 6:  Complete logOperation() to write each action to a log file
    Step 7:  Test with a sample folder containing mixed file types
*/

package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
)

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

// Name of the log file where all operations are recorded
const LOG_FILE = "operations.log"

// ---------------------------------------------------------------------------
// Core functions — complete the TODOs to make each one work
// ---------------------------------------------------------------------------

// scanDirectory reads all files in the given folder and returns their paths.
//
// TODO:
//  1. Use os.ReadDir(dirPath) to read all entries in the folder.
//  2. Loop through entries and skip any that are directories.
//  3. Append the full file path using filepath.Join(dirPath, entry.Name()).
//  4. Return the slice of file paths.
func scanDirectory(dirPath string) ([]string, error) {
	var files []string

	// --- Write your directory scanning code here ---

	return files, nil
}

// groupByExtension takes a list of file paths and groups them by extension.
// Returns a map where the key is the extension (e.g. "pdf") and the value
// is a slice of file paths with that extension.
//
// TODO:
//  1. Loop through each file path.
//  2. Get the extension using filepath.Ext(file) — it returns ".pdf" etc.
//  3. Strip the leading dot to get just "pdf".
//  4. Append the file path to the correct key in the map.
func groupByExtension(files []string) map[string][]string {
	groups := make(map[string][]string)

	// --- Write your grouping code here ---

	return groups
}

// moveFiles moves each file into a subfolder named after its extension.
// For example, report.pdf goes into dirPath/pdf/report.pdf
//
// TODO:
//  1. Loop through each extension and its files in the groups map.
//  2. Create a subfolder using os.MkdirAll(targetFolder, 0755).
//  3. Move each file using os.Rename(oldPath, newPath).
//  4. Call logOperation() to record each move.
//  5. Return the total count of files moved.
func moveFiles(dirPath string, groups map[string][]string) (int, error) {
	moved := 0

	// --- Write your file moving code here ---

	return moved, nil
}

// deleteEmptyFolders removes any empty subfolders inside dirPath.
//
// TODO:
//  1. Use os.ReadDir(dirPath) to list all entries.
//  2. For each entry that is a directory, read its contents.
//  3. If the directory is empty, delete it with os.Remove().
//  4. Call logOperation() to record each deletion.
func deleteEmptyFolders(dirPath string) error {

	// --- Write your cleanup code here ---

	return nil
}

// logOperation appends a single log message to the log file.
//
// TODO:
//  1. Open LOG_FILE in append mode using os.OpenFile with os.O_APPEND flag.
//  2. Write the message followed by a newline character.
//  3. Close the file after writing.
func logOperation(message string) error {

	// --- Write your logging code here ---

	return nil
}

// ---------------------------------------------------------------------------
// Entry point — already complete, no changes needed here
// ---------------------------------------------------------------------------

func main() {
	// Parse the --dir flag from command line
	dirPath := flag.String("dir", ".", "Path to the folder to organize")
	flag.Parse()

	fmt.Printf("Scanning folder: %s\n", *dirPath)

	// Step 1: Scan the directory
	files, err := scanDirectory(*dirPath)
	if err != nil {
		fmt.Printf("Error scanning directory: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Found %d files\n", len(files))

	// Step 2: Group files by extension
	groups := groupByExtension(files)
	fmt.Printf("Found %d file types\n", len(groups))

	// Step 3: Move files into subfolders
	moved, err := moveFiles(*dirPath, groups)
	if err != nil {
		fmt.Printf("Error moving files: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Moved %d files successfully\n", moved)

	// Step 4: Clean up empty folders
	err = deleteEmptyFolders(*dirPath)
	if err != nil {
		fmt.Printf("Error cleaning up folders: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("\nDone! Check %s for the full operation log.\n", LOG_FILE)
}