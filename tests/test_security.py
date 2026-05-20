from app import app
from flask import render_template


def test_project_template_escapes_malicious_content():
    malicious_project = {
        "id": 999,
        "title": '<script>alert("XSS")</script>',
        "level": 'Beginner',
        "interest": 'Web',
        "skills": ['Python'],
        "description": '<img src=x onerror=alert(1)>',
        "features": ['<svg/onload=alert(2)>'],
        "roadmap": ['Step 1: <script>bad()</script>'],
        "resources": ['Malicious: http://example.com', '<script>alert(3)</script>'],
        "tech_stack": ['<b>bash</b>']
    }

    with app.app_context():
        rendered = render_template('project.html', project=malicious_project)

    # Ensure user-supplied script payloads do not appear unescaped
    assert '<script>alert("XSS")</script>' not in rendered
    assert '<script>bad()</script>' not in rendered
    assert '<script>alert(3)</script>' not in rendered

    # The raw tag text should be escaped where expected (no live HTML tags)
    assert '<img' not in rendered
    # Legit SVG icons exist in template; ensure no inline event-injection like '<svg/onload' is present
    assert '<svg/onload' not in rendered
    assert '&lt;img' in rendered or '&lt;script' in rendered

    # PROJECT_ID should be safely serialized as a number in JS
    assert 'var PROJECT_ID = 999' in rendered
