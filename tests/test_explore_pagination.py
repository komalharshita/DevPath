import pytest
from app import app

def test_explore_route_pagination():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        response = client.get("/explore?page=1&per_page=5")
        assert response.status_code == 200
