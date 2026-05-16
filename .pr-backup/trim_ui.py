import re

path = "static/script.js"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

s = re.sub(
    r"\n  var lastPayload = null;\n  var exportResultsBtn.*?\n  var recentListEl = document\.getElementById\(\"recent-list\"\);\n",
    "\n",
    s,
    flags=re.S,
)

s = re.sub(
    r"\n  if \(exportResultsBtn\) \{.*?\n  \}\n\n  renderLibraryPanels\(\);\n\n\n  // -+\n  // Saved / recent panels.*?\n  // -+\n\n  function renderLibraryPanels.*?function exportResultsList\(\) \{.*?\n  \}\n\n",
    "\n",
    s,
    flags=re.S,
)

s = s.replace("    lastPayload = payload;\n\n", "")
s = s.replace(
    '    if (typeof DevPathStore !== "undefined") updateSaveButtons();\n', ""
)

old_card = """    var header = document.createElement("div");
    header.className = "project-card-header";

    var title = document.createElement("h3");
    title.className = "project-card-title";
    title.textContent = project.title;
    header.appendChild(title);

    if (typeof DevPathStore !== "undefined") {
      header.appendChild(createSaveButton(project));
    }

    var desc = document.createElement("p");
    desc.className = "project-card-desc";
    desc.textContent = truncate(project.description, 120);

    var matchBox = buildMatchBreakdown(project);"""

new_card = """    var title = document.createElement("h3");
    title.className = "project-card-title";
    title.textContent = project.title;

    var desc = document.createElement("p");
    desc.className = "project-card-desc";
    desc.textContent = truncate(project.description, 120);"""

s = s.replace(old_card, new_card)
s = s.replace(
    "    card.appendChild(header);\n    card.appendChild(desc);\n    if (matchBox) card.appendChild(matchBox);",
    "    card.appendChild(title);\n    card.appendChild(desc);",
)

s = re.sub(
    r"if \(isDetailPage\) \{\n\n  if \(typeof DevPathStore.*?\n  \}\n\n  var codePanel",
    "if (isDetailPage) {\n\n  var codePanel",
    s,
    flags=re.S,
)

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("done")
