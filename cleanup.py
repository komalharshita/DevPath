with open("static/script.js", "r") as f:
    lines = f.readlines()

def find_line(pattern, start=0):
    for idx in range(start, len(lines)):
        if pattern in lines[idx]:
            return idx
    return -1

# Restore script.js from git to try again
import os
os.system("git checkout HEAD -- static/script.js")

with open("static/script.js", "r") as f:
    lines = f.readlines()

out = []
i = 0
while i < len(lines):
    # Fix the duplicated validateForm and showSuggestions block
    if "function showSuggestions(items) {" in lines[i] and 400 < i < 500:
        end_idx = find_line("  // Form validation", i)
        dropdown_start = find_line("var dropdownBtn = document.getElementById(\"skills-dropdown-toggle\");", i)
        dropdown_end = find_line("  // Show suggestions on input", dropdown_start)
        
        if dropdown_start != -1 and dropdown_end != -1:
            out.extend(lines[dropdown_start-1:dropdown_end])
        
        if end_idx != -1:
            i = end_idx
        else:
            i += 1
        continue
        
    # Remove the stray `return card;`
    if "return card;" in lines[i] and i + 1 < len(lines) and "}" in lines[i+1] and 900 < i < 940:
        i += 2
        continue
        
    # Remove duplicated skillsInput listeners but KEEP the closing brace!
    if "skillsInput.setAttribute(\"role\", \"combobox\");" in lines[i] and i > 900:
        end_idx = find_line("} // end isIndexPage", i)
        if end_idx != -1:
            i = end_idx  # DO NOT ADD 1! We want to keep the closing brace!
        else:
            i += 1
        continue

    # Fix the syntax error at the end of the file
    if "update();" in lines[i] and i + 1 < len(lines) and "})();" in lines[i+1] and i > 1200:
        out.append("}\n")
        i += 2
        continue
        
    # Remove the broken initScrollSpy
    if "(function initScrollSpy() {" in lines[i] and i > 1200:
        break # Rest of the file is broken

    out.append(lines[i])
    i += 1

with open("static/script.js", "w") as f:
    f.writelines(out)

