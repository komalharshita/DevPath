# services/url_validator_service.py
import re

# Matches http:// or https:// followed by a domain and optional path.
# Intentionally strict: rejects bare domains, ftp://, mailto:, etc.
_URL_RE = re.compile(
    r'^https?://'                      # scheme
    r'(?:(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}|localhost)'  # domain
    r'(?::\d+)?'                       # optional port
    r'(?:[/?#][^\s]*)?$',              # optional path/query/fragment
    re.IGNORECASE,
)


def is_valid_url(url: str) -> bool:
    """Return True if *url* is a well-formed http/https URL.

    Only checks format — does not make any network request.
    """
    if not url or not isinstance(url, str):
        return False
    return bool(_URL_RE.match(url.strip()))


def parse_resource(raw: str) -> dict:
    """Split a raw resource string into a label and URL."""
    if not raw or not isinstance(raw, str):
        return {"label": "", "url": ""}

    raw = raw.strip()

    # Find the first occurrence of ": http" to split label from URL
    split_marker = ": http"
    idx = raw.find(split_marker)
    if idx != -1:
        label = raw[:idx].strip()
        url   = raw[idx + 2:].strip()   # skip ": " → starts at "http"
        return {"label": label, "url": url}

    # No label prefix — treat the entire string as a URL
    return {"label": raw, "url": raw}


def validate_resource(raw: str) -> dict:
    """Parse a raw resource string and validate its URL format."""
    parsed = parse_resource(raw)
    parsed["valid"] = is_valid_url(parsed["url"])
    return parsed


def validate_resources(resources: list) -> list:
    """Validate a list of raw resource strings."""
    if not isinstance(resources, list):
        return []
    return [validate_resource(r) for r in resources if r]
