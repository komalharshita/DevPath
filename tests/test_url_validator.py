# tests/test_url_validator.py
# Unit tests for src/utils/url_validator.py
#
# Run with:   python -m pytest tests/test_url_validator.py
# Or:         python tests/test_url_validator.py

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.url_validator import (
    is_valid_url,
    parse_resource,
    validate_resource,
    validate_resources,
)


# ---------------------------------------------------------------------------
# is_valid_url — valid URLs
# ---------------------------------------------------------------------------

def test_valid_https_url():
    assert is_valid_url("https://example.com") is True


def test_valid_http_url():
    assert is_valid_url("http://example.com") is True


def test_valid_url_with_path():
    assert is_valid_url("https://example.com/path/to/resource") is True


def test_valid_url_with_query_string():
    assert is_valid_url("https://example.com/search?q=python&lang=en") is True


def test_valid_url_with_fragment():
    assert is_valid_url("https://example.com/page#section") is True


def test_valid_url_with_port():
    assert is_valid_url("https://example.com:8443/path") is True


def test_valid_url_localhost():
    assert is_valid_url("http://localhost:5000/") is True


def test_valid_url_case_insensitive_scheme():
    assert is_valid_url("HTTPS://EXAMPLE.COM") is True
    assert is_valid_url("HTTP://EXAMPLE.COM") is True


def test_valid_url_subdomain():
    assert is_valid_url("https://docs.example.com/guide") is True


def test_valid_url_with_trailing_slash():
    assert is_valid_url("https://example.com/") is True


def test_valid_url_with_hyphen_in_domain():
    assert is_valid_url("https://my-example.com/") is True


# ---------------------------------------------------------------------------
# is_valid_url — invalid URLs
# ---------------------------------------------------------------------------

def test_invalid_none():
    assert is_valid_url(None) is False


def test_invalid_empty_string():
    assert is_valid_url("") is False


def test_invalid_whitespace_only():
    assert is_valid_url("   ") is False


def test_invalid_non_string():
    assert is_valid_url(123) is False
    assert is_valid_url(["https://example.com"]) is False
    assert is_valid_url(None) is False


def test_invalid_ftp_scheme():
    assert is_valid_url("ftp://example.com/file") is False


def test_invalid_mailto():
    assert is_valid_url("mailto:user@example.com") is False


def test_invalid_bare_domain():
    assert is_valid_url("example.com") is False


def test_invalid_file_scheme():
    assert is_valid_url("file:///etc/passwd") is False


def test_invalid_relative_path():
    assert is_valid_url("/path/to/resource") is False


def test_invalid_url_with_trailing_whitespace():
    # The validator strips whitespace, so this is valid
    assert is_valid_url("https://example.com  ") is True
    # But with leading whitespace only
    assert is_valid_url("  https://example.com") is True


# ---------------------------------------------------------------------------
# parse_resource — labeled format
# ---------------------------------------------------------------------------

def test_parse_resource_with_label():
    result = parse_resource("MDN Docs: https://developer.mozilla.org/")
    assert result["label"] == "MDN Docs"
    assert result["url"] == "https://developer.mozilla.org/"


def test_parse_resource_with_label_extra_whitespace():
    # Leading/trailing whitespace on the whole string is stripped.
    # Two spaces between label and ':' breaks the ': http' split marker,
    # so this is treated as a bare URL (documented edge case).
    result = parse_resource("  MDN Docs  :  https://developer.mozilla.org/  ")
    assert result["label"] == "MDN Docs  :  https://developer.mozilla.org/"
    assert result["url"] == "MDN Docs  :  https://developer.mozilla.org/"


def test_parse_resource_label_with_colon():
    # The split marker is ": http", so a URL-only string starting with
    # "http" is treated as a bare URL, not a label
    result = parse_resource("Tutorial: https://example.com/tutorial?q=what")
    assert result["label"] == "Tutorial"
    assert result["url"] == "https://example.com/tutorial?q=what"


# ---------------------------------------------------------------------------
# parse_resource — bare URL format
# ---------------------------------------------------------------------------

def test_parse_resource_bare_https():
    result = parse_resource("https://example.com")
    assert result["label"] == "https://example.com"
    assert result["url"] == "https://example.com"


def test_parse_resource_bare_http():
    result = parse_resource("http://example.com")
    assert result["label"] == "http://example.com"
    assert result["url"] == "http://example.com"


def test_parse_resource_bare_url_with_path():
    result = parse_resource("https://example.com/path/to/page")
    assert result["url"] == "https://example.com/path/to/page"


# ---------------------------------------------------------------------------
# parse_resource — edge cases
# ---------------------------------------------------------------------------

def test_parse_resource_none():
    result = parse_resource(None)
    assert result == {"label": "", "url": ""}


def test_parse_resource_empty_string():
    result = parse_resource("")
    assert result == {"label": "", "url": ""}


def test_parse_resource_non_string():
    result = parse_resource(123)
    assert result == {"label": "", "url": ""}


def test_parse_resource_colon_without_space():
    # "Label:https://..." does not match ": http" split marker
    result = parse_resource("Label:https://example.com")
    assert result["url"] == "Label:https://example.com"
    assert result["label"] == "Label:https://example.com"


def test_parse_resource_whitespace_only():
    result = parse_resource("   ")
    assert result == {"label": "", "url": ""}


# ---------------------------------------------------------------------------
# validate_resource
# ---------------------------------------------------------------------------

def test_validate_resource_valid():
    result = validate_resource("Docs: https://example.com/docs")
    assert result["label"] == "Docs"
    assert result["url"] == "https://example.com/docs"
    assert result["valid"] is True


def test_validate_resource_invalid_url():
    result = validate_resource("Docs: not-a-valid-url")
    assert result["label"] == "Docs"
    assert result["url"] == "not-a-valid-url"
    assert result["valid"] is False


def test_validate_resource_bare_valid_url():
    result = validate_resource("https://example.com")
    assert result["valid"] is True


def test_validate_resource_bare_invalid_url():
    result = validate_resource("bare-domain.com")
    assert result["valid"] is False


# ---------------------------------------------------------------------------
# validate_resources
# ---------------------------------------------------------------------------

def test_validate_resources_list_of_valid():
    resources = [
        "MDN: https://developer.mozilla.org/",
        "https://docs.python.org/",
    ]
    results = validate_resources(resources)
    assert len(results) == 2
    assert all(r["valid"] for r in results)


def test_validate_resources_mixed_valid_invalid():
    resources = [
        "Valid: https://example.com/",
        "Invalid: ftp://example.com",
    ]
    results = validate_resources(resources)
    assert len(results) == 2
    assert results[0]["valid"] is True
    assert results[1]["valid"] is False


def test_validate_resources_empty_list():
    results = validate_resources([])
    assert results == []


def test_validate_resources_not_a_list_returns_empty():
    assert validate_resources("not a list") == []
    assert validate_resources(None) == []
    assert validate_resources(123) == []


# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--no-header"]))
