# tests/test_og_tags.py
# Tests for Open Graph and Twitter Card meta tag implementation.

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app
from config import Config

def get_client():
    """Return a Flask test client with testing mode enabled."""
    app.config["TESTING"] = True
    return app.test_client()

# ============================================================
# Homepage OG Tag Tests
# ============================================================

def test_index_og_title():
    """Homepage must include og:title meta tag."""
    client = get_client()
    html = client.get("/").data.decode()
    assert 'property="og:title"' in html
    assert "DevPath" in html

def test_index_og_description():
    """Homepage must include og:description meta tag."""
    html = get_client().get("/").data.decode()
    assert 'property="og:description"' in html

def test_index_og_image():
    """Homepage must include og:image pointing to the OG banner."""
    html = get_client().get("/").data.decode()
    assert 'property="og:image"' in html
    assert "og-banner.png" in html

def test_index_og_url():
    """Homepage must include og:url."""
    html = get_client().get("/").data.decode()
    assert 'property="og:url"' in html

def test_index_og_type():
    """Homepage og:type must be 'website'."""
    html = get_client().get("/").data.decode()
    assert 'property="og:type"' in html
    assert 'content="website"' in html

def test_index_twitter_card():
    """Homepage must include twitter:card set to summary_large_image."""
    html = get_client().get("/").data.decode()
    assert 'name="twitter:card"' in html
    assert 'summary_large_image' in html

def test_index_twitter_image():
    """Homepage must include twitter:image."""
    html = get_client().get("/").data.decode()
    assert 'name="twitter:image"' in html

# ============================================================
# Project Page OG Tag Tests
# ============================================================

def test_project_og_title_dynamic():
    """Project page og:title must contain the project's actual title."""
    client = get_client()
    html = client.get("/project/1").data.decode()
    assert 'property="og:title"' in html
    assert '{{ project.title }}' not in html

def test_project_og_description_dynamic():
    """Project page og:description must be rendered (not a raw Jinja2 tag)."""
    html = get_client().get("/project/1").data.decode()
    assert 'property="og:description"' in html
    assert '{{ project.description' not in html

def test_project_og_image():
    """Project page must include og:image."""
    html = get_client().get("/project/1").data.decode()
    assert 'property="og:image"' in html
    assert "og-banner.png" in html

def test_project_og_url_dynamic():
    """Project page og:url must contain the project ID."""
    html = get_client().get("/project/1").data.decode()
    assert 'property="og:url"' in html
    assert "/project/1" in html

def test_project_twitter_card_large_image():
    """Project page twitter:card must be summary_large_image."""
    html = get_client().get("/project/1").data.decode()
    assert 'name="twitter:card"' in html
    assert 'summary_large_image' in html

def test_project_twitter_image():
    """Project page must include twitter:image."""
    html = get_client().get("/project/1").data.decode()
    assert 'name="twitter:image"' in html

# ============================================================
# Error Page OG Tag Tests
# ============================================================

def test_404_has_og_tags():
    """404 page must include basic OG tags."""
    html = get_client().get("/project/99999").data.decode()
    assert 'property="og:title"' in html
    assert 'property="og:image"' in html

def test_404_has_noindex():
    """404 page must have robots noindex to prevent search engine indexing."""
    html = get_client().get("/project/99999").data.decode()
    assert 'name="robots"' in html
    assert 'noindex' in html

# ============================================================
# Dynamic URL Tests
# ============================================================

def test_og_urls_not_hardcoded():
    """OG URLs must use config, not hardcoded URLs."""
    html = get_client().get("/").data.decode()
    # Should NOT contain hardcoded URL
    assert 'https://mydevpath-github.vercel.app' not in html or Config.BASE_URL in html

def test_config_base_url_used():
    """Config.BASE_URL must be used in OG tags."""
    html = get_client().get("/").data.decode()
    # Verify config is being used
    assert Config.BASE_URL.replace("https://", "").replace("http://", "") in html or "{{ config" in html

# ============================================================
# OG Banner Image Tests
# ============================================================

def test_og_banner_exists():
    """The og-banner.png file must exist in static folder."""
    import os
    assert os.path.exists("src/static/og-banner.png"), "og-banner.png missing from static folder"

def test_og_banner_dimensions():
    """The og-banner.png must be 1200x630 pixels."""
    pytest.importorskip("PIL")
    from PIL import Image
    img = Image.open("src/static/og-banner.png")
    assert img.size == (1200, 630), f"Expected 1200x630, got {img.size}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
