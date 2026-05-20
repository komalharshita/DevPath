/*
Project:    File Organizer Automation
Difficulty: Intermediate
Skills:     Kotlin, java.io.File, kotlin.collections
Time:       Medium (a weekend)

What you will build:
    A Kotlin command-line tool that scans a folder and automatically
    organizes files into subfolders by their extension. Generates a
    summary report of all files moved.

How to run:
    kotlinc file_organizer.kt -include-runtime -d organizer.jar
    java -jar organizer.jar /path/to/folder

Learning goals:
    - Working with File I/O in Kotlin
    - Using Kotlin collection functions like groupBy and forEach
    - Creating and moving files programmatically
    - Generating formatted console reports

Roadmap:
    Step 1:  Project is already set up — run it on a sample folder
    Step 2:  Complete scanFolder() to list all files in a directory
    Step 3:  Complete groupByExtension() to categorize files
    Step 4:  Complete createSubfolders() to make target directories
    Step 5:  Complete moveFiles() to move files to correct folders
    Step 6:  Complete printSummary() to display the operation report
    Step 7:  Test with a folder containing at least 10 mixed files
*/

import java.io.File

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

// Extensions that should be skipped and not moved
val SKIP_EXTENSIONS = listOf("", "log", "tmp")

// ---------------------------------------------------------------------------
// Core functions — complete the TODOs to make each one work
// ---------------------------------------------------------------------------

/**
 * Scan a folder and return a list of all files inside it.
 * Does not recurse into subfolders.
 *
 * TODO:
 * 1. Create a File object from the folderPath string
 * 2. Check if it exists and is a directory
 * 3. Use listFiles() to get all entries
 * 4. Filter to keep only files not directories
 * 5. Return the filtered list
 */
fun scanFolder(folderPath: String): List<File> {
    val files = mutableListOf<File>()

    // --- Write your folder scanning code here ---

    return files
}

/**
 * Group a list of files by their extension.
 * Returns a Map where key is extension and value is list of files.
 *
 * TODO:
 * 1. Use the groupBy() function on the files list
 * 2. Extract the extension using file.extension
 * 3. Convert extension to lowercase for consistency
 * 4. Filter out extensions in SKIP_EXTENSIONS
 */
fun groupByExtension(files: List<File>): Map<String, List<File>> {

    // --- Write your grouping code here ---

    return emptyMap()
}

/**
 * Create a subfolder for each extension inside the target folder.
 * Returns a map of extension to the created folder File object.
 *
 * TODO:
 * 1. Loop through each extension in the groups map
 * 2. Create a File for targetFolder/extensionName
 * 3. Call mkdirs() to create the folder and any parents
 * 4. Store in a result map and return it
 */
fun createSubfolders(targetFolder: String, groups: Map<String, List<File>>): Map<String, File> {
    val folders = mutableMapOf<String, File>()

    // --- Write your subfolder creation code here ---

    return folders
}

/**
 * Move each file to its corresponding subfolder.
 * Returns the total count of files successfully moved.
 *
 * TODO:
 * 1. Loop through each extension and its files
 * 2. Look up the target subfolder from the folders map
 * 3. Build the destination path using File(folder, file.name)
 * 4. Use file.renameTo(destination) to move the file
 * 5. Count successful moves and return the total
 */
fun moveFiles(groups: Map<String, List<File>>, folders: Map<String, File>): Int {
    var moved = 0

    // --- Write your file moving code here ---

    return moved
}

/**
 * Print a formatted summary of the organization operation.
 *
 * TODO:
 * 1. Print a header line
 * 2. Loop through groups and print each extension with file count
 * 3. Print the total files moved
 * 4. Print a completion message
 */
fun printSummary(groups: Map<String, List<File>>, totalMoved: Int) {

    // --- Write your summary printing code here ---

}

// ---------------------------------------------------------------------------
// Entry point — already complete, no changes needed here
// ---------------------------------------------------------------------------

fun main(args: Array<String>) {
    if (args.isEmpty()) {
        println("Usage: java -jar organizer.jar <folder_path>")
        return
    }

    val folderPath = args[0]
    println("Organizing folder: $folderPath\n")

    val files = scanFolder(folderPath)
    if (files.isEmpty()) {
        println("No files found in $folderPath")
        return
    }

    println("Found ${files.size} files")

    val groups = groupByExtension(files)
    val folders = createSubfolders(folderPath, groups)
    val totalMoved = moveFiles(groups, folders)

    printSummary(groups, totalMoved)
}