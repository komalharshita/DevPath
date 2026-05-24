# keyword_searcher.py
# Starter code template for DevPath Text File Keyword Searcher project.
#
# Your task is to build a CLI utility that searches text files for a keyword.

import os
import sys

def search_keyword_in_file(filepath, keyword):
    """
    Search for a keyword in the given file.
    
    Args:
      filepath (str): Path to the text file to search.
      keyword (str): The search keyword (case-insensitive).
      
    Returns:
      list of dict: List of matching lines. Example:
        [
          {'line_no': 5, 'text': 'This line contains Python keyword.'},
          ...
        ]
    """
    matches = []
    
    # TODO: Open file safely using 'with open(filepath, "r", encoding="utf-8") as f'
    # TODO: Read file line by line, track line number starting from 1
    # TODO: Check if keyword is in the line (case-insensitive)
    # TODO: Append a dict to matches: {'line_no': line_num, 'text': line_content.strip()}
    
    return matches

if __name__ == '__main__':
    print("--- Text File Keyword Searcher ---")
    
    # Read user inputs
    target_file = input("Enter path to text file: ")
    search_word = input("Enter keyword to search: ")
    
    if not os.path.exists(target_file):
        print(f"Error: File '{target_file}' does not exist.")
        sys.exit(1)
        
    results = search_keyword_in_file(target_file, search_word)
    
    if results:
        print(f"\nFound {len(results)} matches:")
        for r in results:
            print(f"Line {r['line_no']}: {r['text']}")
    else:
        print("\nNo matches found.")
