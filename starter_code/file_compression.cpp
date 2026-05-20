/*
Project:    File Compression Tool
Difficulty: Intermediate
Skills:     C++, fstream, string, iostream
Time:       High (several days)

What you will build:
    A command-line file compression tool that implements run-length
    encoding to compress and decompress text files. Shows the
    compression ratio achieved.

How to run:
    g++ file_compression.cpp -o compress
    ./compress compress input.txt output.rle
    ./compress decompress output.rle result.txt

Learning goals:
    - Reading and writing files using fstream
    - Implementing a basic compression algorithm
    - Working with strings and characters in C++
    - Handling command-line arguments

Roadmap:
    Step 1:  Project is already set up — run it and explore the output
    Step 2:  Complete readFile() to load file contents into a string
    Step 3:  Complete writeFile() to save a string to a file
    Step 4:  Complete compressRLE() to implement run-length encoding
    Step 5:  Complete decompressRLE() to reverse the compression
    Step 6:  Complete showCompressionRatio() to display size stats
    Step 7:  Test with different text files including edge cases
*/

#include <iostream>
#include <fstream>
#include <string>

// ---------------------------------------------------------------------------
// Core functions — complete the TODOs to make each one work
// ---------------------------------------------------------------------------

/**
 * Read the full contents of a file into a string.
 *
 * @param filename Path to the file to read
 * @param content  String to store the file contents in
 * @return true if successful, false if file could not be opened
 *
 * TODO:
 * 1. Open the file using std::ifstream
 * 2. Check if the file opened successfully
 * 3. Read the entire contents using std::istreambuf_iterator
 * 4. Store in the content parameter
 * 5. Return true on success, false on failure
 */
bool readFile(const std::string& filename, std::string& content) {

    // --- Write your file reading code here ---

    return false;
}

/**
 * Write a string to a file.
 *
 * @param filename Path to the output file
 * @param content  The string content to write
 * @return true if successful, false if file could not be opened
 *
 * TODO:
 * 1. Open the file using std::ofstream
 * 2. Check if the file opened successfully
 * 3. Write the content string to the file
 * 4. Return true on success, false on failure
 */
bool writeFile(const std::string& filename, const std::string& content) {

    // --- Write your file writing code here ---

    return false;
}

/**
 * Compress a string using run-length encoding.
 * Run-length encoding replaces consecutive repeated characters
 * with the character followed by its count.
 *
 * Example: "AAABBBCCCC" -> "A3B3C4"
 * Example: "ABCD" -> "A1B1C1D1"
 *
 * @param input The original string to compress
 * @return The compressed string
 *
 * TODO:
 * 1. Loop through each character in input
 * 2. Count consecutive occurrences of the same character
 * 3. Append the character and its count to the result string
 * 4. Move to the next different character and repeat
 * 5. Return the compressed result
 */
std::string compressRLE(const std::string& input) {
    std::string result = "";

    // --- Write your compression code here ---

    return result;
}

/**
 * Decompress a run-length encoded string back to the original.
 *
 * Example: "A3B3C4" -> "AAABBBCCCC"
 *
 * @param input The compressed RLE string
 * @return The decompressed original string
 *
 * TODO:
 * 1. Loop through the compressed string two characters at a time
 * 2. First character is the letter, second is the count digit
 * 3. Repeat the letter count times and append to result
 * 4. Handle multi-digit counts (e.g. A12 means 12 A's)
 * 5. Return the decompressed result
 */
std::string decompressRLE(const std::string& input) {
    std::string result = "";

    // --- Write your decompression code here ---

    return result;
}

/**
 * Calculate and display the compression ratio.
 *
 * @param originalSize   Size of the original content in bytes
 * @param compressedSize Size of the compressed content in bytes
 *
 * TODO:
 * 1. Calculate ratio as (1 - compressedSize/originalSize) * 100
 * 2. Print original size, compressed size, and ratio percentage
 * 3. Print a message if compression made the file larger
 */
void showCompressionRatio(size_t originalSize, size_t compressedSize) {

    // --- Write your ratio display code here ---

}

// ---------------------------------------------------------------------------
// Entry point — already complete, no changes needed here
// ---------------------------------------------------------------------------

int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cout << "Usage: ./compress <compress|decompress> <input> <output>" << std::endl;
        return 1;
    }

    std::string mode = argv[1];
    std::string inputFile = argv[2];
    std::string outputFile = argv[3];

    std::string content;
    if (!readFile(inputFile, content)) {
        std::cout << "Error: Could not open input file: " << inputFile << std::endl;
        return 1;
    }

    std::string result;
    if (mode == "compress") {
        result = compressRLE(content);
        showCompressionRatio(content.size(), result.size());
    } else if (mode == "decompress") {
        result = decompressRLE(content);
    } else {
        std::cout << "Error: Mode must be 'compress' or 'decompress'" << std::endl;
        return 1;
    }

    if (!writeFile(outputFile, result)) {
        std::cout << "Error: Could not write to output file: " << outputFile << std::endl;
        return 1;
    }

    std::cout << "Done! Output written to: " << outputFile << std::endl;
    return 0;
}