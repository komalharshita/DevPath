from app import app
from flask import render_template


def test_index_template_escapes_malicious_stats():
    # Inject malicious strings into stats to simulate unsafe data
    malicious_stats = {
        "total_projects": '<script>alert(1)</script>',
        "unique_skills": '<img src=x onerror=alert(2)>',
        "beginner_friendly": '<svg/onload=alert(3)>'
    }

    with app.app_context():
        rendered = render_template('index.html', stats=malicious_stats)

    # Ensure injected scripts and raw tags are escaped
    assert '<script>alert(1)</script>' not in rendered
    assert '<img src=x onerror=alert(2)>' not in rendered
    assert '<svg/onload=alert(3)>' not in rendered
    assert '&lt;script' in rendered or '&lt;img' in rendered
