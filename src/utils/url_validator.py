# utils/url_validator.py
# Utilities for parsing and validating learning resource URLs.
#
# Resources in projects.json are stored as plain strings in one of
# two formats:
#   "Label text: https://example.com/path"   (label + URL)
#   "https://example.com/path"               (URL only)
#
# This module provides:
#   parse_resource(raw)  → {"label": str, "url": str}
#   is_valid_url(url)    → bool  (format check only, no HTTP request)
#   validate_resource(raw) → {"label": str, "url": str, "valid": bool}
#
# Deliberately no outbound HTTP requests — format validation only.
# This keeps startup fast and avoids network dependencies in tests.

import re

# Matches http:// or https:// followed by a domain and optional path.
# Intentionally strict: rejects bare domains, ftp://, mailto:, etc.
URL_RE = re.compile(
        r'^https?://'                      # scheme
        r'(?:(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}|localhost)'  # domain
        r'(?::\d+)?'                       # optional port
        r'(?:[/?#][^\s]*)?$',              # optional path/query/fragment
        re.IGNORECASE,
    )

# Matches a labeled resource "Label: https://...".  The label is captured
# non-greedily so colons inside the URL are not consumed, and the scheme is
# matched case-insensitively so "HTTPS://" is recognized as a label split.
LABEL_URL_RE = re.compile(r'^(?P<label>.+?):\s*(?P<url>https?://.*)$', re.IGNORECASE)

def is_valid_url(url: str) -> bool:
    """Return True if *url* is a well-formed http/https URL.

    Only checks format — does not make any network request.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL matches the expected http/https pattern.
    """
    if not url or not isinstance(url, str):
        return False
    return bool(URL_RE.match(url.strip()))


def parse_resource(raw: str) -> dict:
    """Split a raw resource string into a label and URL.

    Handles two formats:
        "Label text: https://example.com"  → label="Label text", url="https://..."
        "https://example.com"              → label="https://example.com", url="https://..."

    A string of the form "Label: <http(s)://...>" is split on the scheme
    token (case-insensitive), so "https://" URLs are never truncated.  Any
    other string is treated as a bare URL.

    Args:
        raw: The raw resource string from projects.json.

    Returns:
        A dict with keys "label" (str) and "url" (str).
        Both values are stripped of leading/trailing whitespace.
        If no URL can be parsed, "url" is an empty string.
    """
    if not raw or not isinstance(raw, str):
        return {"label": "", "url": ""}

    raw = raw.strip()

    # Match "Label: <scheme://...>" explicitly.  The label is non-greedy and
    # the scheme is matched case-insensitively, so both "https://" URLs and
    # "HTTPS://" variants are parsed without corrupting the scheme.
    match = LABEL_URL_RE.match(raw)
    if match:
        return {
            "label": match.group("label").strip(),
            "url": match.group("url").strip(),
        }

    # No label prefix — treat the entire string as a URL
    return {"label": raw, "url": raw}


def validate_resource(raw: str) -> dict:
    """Parse a raw resource string and validate its URL format.

    Args:
        raw: The raw resource string from projects.json.

    Returns:
        A dict with keys:
            "label" (str)  — human-readable link text
            "url"   (str)  — the URL (may be empty if unparseable)
            "valid" (bool) — True if the URL passes format validation
    """
    parsed = parse_resource(raw)
    parsed["valid"] = is_valid_url(parsed["url"])
    return parsed


def validate_resources(resources: list) -> list:
    """Validate a list of raw resource strings.

    Args:
        resources: List of raw resource strings from a project's
                   "resources" field.

    Returns:
        List of dicts, each with "label", "url", and "valid" keys.
    """
    if not isinstance(resources, list):
        return []
    return [validate_resource(raw) for raw in resources]