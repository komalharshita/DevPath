# markdown_converter.py
# Starter code template for DevPath Markdown to HTML Converter CLI project.
#
# Your task is to implement a Markdown to HTML converter.

import re
import os
import sys

def convert_markdown_to_html(markdown_text):
    """
    Convert basic Markdown syntax to valid HTML markup.
    
    Rules to support:
      - Headings: # Header 1 -> <h1>Header 1</h1>
      - Headings: ## Header 2 -> <h2>Header 2</h2>
      - Bold: **text** -> <strong>text</strong>
      - Italic: *text* -> <em>text</em>
      
    Returns:
      str: The parsed HTML text.
    """
    html = markdown_text
    
    # TODO: Use regular expressions or string replacements to translate headers:
    #   Hint: re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # TODO: Translate second-level headers: ## Header -> <h2>Header</h2>
    
    # TODO: Translate Bold text (**text**) -> <strong>text</strong>
    
    # TODO: Translate Italic text (*text*) -> <em>text</em>
    
    return html

if __name__ == '__main__':
    print("--- Markdown to HTML CLI ---")
    md_file = input("Enter path to markdown file (.md): ")
    
    if not os.path.exists(md_file):
        print(f"Error: File '{md_file}' does not exist.")
        sys.exit(1)
        
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()
        
    html_output = convert_markdown_to_html(md_content)
    
    out_file = os.path.splitext(md_file)[0] + ".html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_output)
        
    print(f"Success! Converted HTML written to: {out_file}")
