# tests/test_html_template_duplicate_ids.py
# Regression test for issue #1878: element IDs must be unique within a template.
# Duplicate IDs are invalid HTML and break getElementById() lookups (dead UI).

import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(ROOT, "src", "templates")

ID_RE = re.compile(r'\bid="([^"]+)"')


def _template_files():
    return sorted(glob.glob(os.path.join(TEMPLATES_DIR, "**", "*.html"), recursive=True))


def test_no_duplicate_ids_in_templates():
    """Each template may define an element ID only once."""
    dupes = {}
    for path in _template_files():
        with open(path, encoding="utf-8") as f:
            content = f.read()
        ids = ID_RE.findall(content)
        duplicated = {i for i in ids if ids.count(i) > 1}
        if duplicated:
            dupes[os.path.relpath(path, TEMPLATES_DIR)] = sorted(duplicated)
    assert not dupes, (
        "duplicate element IDs found in templates (issue #1878): "
        f"{dupes}"
    )
