import os
import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_rate_limiting_api_recommend(client):
    """Fire 3 rapid requests; the 3rd should be rate limited (429)."""
    # Set rate limit low for THIS test
    os.environ["RECOMMENDER_RATE_LIMIT"] = "2 per minute"
    
    payload = {
        "skills": "Python",
        "level": "Beginner",
        "interest": "Data",
        "time": "Low"
    }

    try:
        # Request 1: Should be 200
        resp1 = client.post("/api/recommend", json=payload)
        assert resp1.status_code == 200

        # Request 2: Should be 200
        resp2 = client.post("/api/recommend", json=payload)
        assert resp2.status_code == 200

        # Request 3: Should be 429
        resp3 = client.post("/api/recommend", json=payload)
        assert resp3.status_code == 429
        
        data = resp3.get_json()
        assert "error" in data
        assert "Rate limit exceeded" in data["error"]
    finally:
        # Reset rate limit so other tests are not affected
        os.environ["RECOMMENDER_RATE_LIMIT"] = "60 per minute"
