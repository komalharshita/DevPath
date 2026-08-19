import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_share_project_button_rendered(client):
    """Test that the Share Project button is rendered on the project detail page."""
    response = client.get('/project/1')
    assert response.status_code == 200
    assert b'id="btn-share-project"' in response.data
    assert b'Copy Direct Link' in response.data

def test_share_toast_element_rendered(client):
    """Test that the share-toast element is present on the project detail page."""
    response = client.get('/project/1')
    assert response.status_code == 200
    assert b'id="share-toast"' in response.data
