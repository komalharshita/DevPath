# tests/test_html_anchor_integrity.py
# Regression test for issue #1876: every same-page anchor (<a href="#id">) in an
# HTML template must target an element ID that actually exists in that file.
#
# Cross-page fragment links (e.g. href="/#home") intentionally point at sections
# of the homepage and are exempt; only bare "#fragment" targets are checked.

import os
import re

import pytest

TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "src",
    "templates",
)

_HREF_RE = re.compile(r'href="#([^"]+)"')
_ID_RE = re.compile(r'\bid="([^"]+)"')

TEMPLATE_FILES = [
    os.path.relpath(p, TEMPLATES_DIR)
    for p in (
        os.path.join(TEMPLATES_DIR, "explore.html"),
        os.path.join(TEMPLATES_DIR, "index.html"),
        os.path.join(TEMPLATES_DIR, "project.html"),
        os.path.join(TEMPLATES_DIR, "profile.html"),
        os.path.join(TEMPLATES_DIR, "contact.html"),
        os.path.join(TEMPLATES_DIR, "compare.html"),
    )
]


def _parse_template(path):
    with open(os.path.join(TEMPLATES_DIR, path), encoding="utf-8") as f:
        content = f.read()
    ids = set(_ID_RE.findall(content))
    return content, ids


@pytest.mark.parametrize("template", TEMPLATE_FILES)
def test_in_page_anchors_have_matching_ids(template):
    """Bare #fragment anchors must resolve to an element ID in the same file."""
    content, ids = _parse_template(template)
    targets = _HREF_RE.findall(content)
    missing = sorted({t for t in targets if t not in ids})
    assert not missing, (
        f"{template} has in-page anchors with no matching element ID: {missing}"
    )


def test_explore_has_no_dead_section_anchors():
    """explore.html must not reference homepage-only sections as bare anchors."""
    content, ids = _parse_template("explore.html")
    targets = _HREF_RE.findall(content)
    assert targets == [], (
        "explore.html still contains dead in-page anchors (issue #1876): "
        f"{sorted(set(targets))}"
    )
