import re

path = "static/style.css"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

blocks = [
    r"/\* ---- Saved / Recent library -+\*/.*?/\* ---- Form Section",
    r"\.btn-export-results.*?/\* Results grid \*/",
    r"\.project-card-header.*?\.match-score \{[^}]+\}\n",
    r"\.btn-save-project,.*?\.btn-save-project\.is-saved \{[^}]+\}\n\n",
]

for pat in blocks:
    s = re.sub(pat, lambda m: m.group(0).split("*/")[0] + "*/" if "Form Section" in pat else "", s, count=1, flags=re.S)
    # simpler: manual markers

start = s.find("/* ---- Saved / Recent library")
end = s.find("/* ---- Form Section")
if start != -1 and end != -1:
    s = s[:start] + s[end:]

start = s.find(".btn-export-results")
end = s.find("/* Results grid */")
if start != -1 and end != -1:
    s = s[:start] + s[end:]

start = s.find(".project-card-header")
end = s.find("/* Results grid */")
if start != -1 and end != -1:
    # project-card-header is inside removed block - already removed?
    pass

# remove export through match-score before results grid
start = s.find(".btn-export-results")
if start == -1:
    start = s.find(".project-card-header")
end = s.find(".results-grid {")
if start != -1 and end != -1:
    s = s[:start] + s[end:]

start = s.find(".btn-save-project,")
end = s.find("/* Detail body */")
if start != -1 and end != -1:
    s = s[:start] + s[end:]

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("css done")
