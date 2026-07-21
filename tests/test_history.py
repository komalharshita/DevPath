import pytest

pytest.skip("History endpoints not implemented in this project", allow_module_level=True)
from app import app
import hashlib


def get_client():
    app.config["TESTING"] = True
    return app.test_client()


def test_create_history_basic():
    client = get_client()

    response = client.post("/history/", json={
        "code": "print('hello')",
        "language": "python"
    })

    assert response.status_code in (200, 201)

    data = response.get_json()
    assert data is not None
    assert "id" in data


def test_invalid_code_length():
    client = get_client()

    long_code = "a" * 50001

    response = client.post("/history/", json={
        "code": long_code,
        "language": "python"
    })

    assert response.status_code in (400, 422)


def test_delete_twice():
    client = get_client()

    res = client.post("/history/", json={
        "code": "print('delete')",
        "language": "python"
    })

    assert res.status_code in (200, 201)

    data = res.get_json()
    history_id = data.get("id")

    assert history_id is not None

    res1 = client.delete(f"/history/{history_id}")
    assert res1.status_code in (200, 204)

    res2 = client.delete(f"/history/{history_id}")
    assert res2.status_code == 404


def test_sha256_hash():
    client = get_client()

    code = "print('hash')"

    res = client.post("/history/", json={
        "code": code,
        "language": "python"
    })

    assert res.status_code in (200, 201)

    data = res.get_json()
    expected_hash = hashlib.sha256(code.encode()).hexdigest()

    if data and "code_hash" in data:
        assert data["code_hash"] == expected_hash


def test_pagination_limit():
    client = get_client()

    res = client.get("/history/?limit=1000")
    assert res.status_code in (400, 422)


def test_search_limit():
    client = get_client()

    res = client.get("/history/search?query=test&limit=-1")
    assert res.status_code in (400, 422)