import pytest
import sys
import os

# Ensure src directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_random_project_route_redirect(client):
    """Test that /random-project returns 302 redirecting to a valid project page."""
    response = client.get('/random-project')
    assert response.status_code == 302
    assert '/project/' in response.location

def test_random_alias_route_redirect(client):
    """Test that /random alias route returns 302 redirecting to a valid project page."""
    response = client.get('/random')
    assert response.status_code == 302
    assert '/project/' in response.location

def test_random_project_follows_redirect(client):
    """Test that following the redirect from /random-project loads a project page successfully."""
    response = client.get('/random-project', follow_redirects=True)
    assert response.status_code == 200
    assert b"Project" in response.data or b"DevPath" in response.data
