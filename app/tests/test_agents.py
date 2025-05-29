import pytest

def test_mycocore_snapshot(client, auth_headers):
    response = client.get("/api/mycocore/snapshot", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "uptime" in data

def test_neuroweave_ask(client, auth_headers):
    response = client.post(
        "/api/neuroweave/ask",
        headers=auth_headers,
        json={"prompt": "test prompt"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data

def test_rootbloom_generate(client, auth_headers):
    response = client.post(
        "/api/rootbloom/generate",
        headers=auth_headers,
        json={"prompt": "test prompt"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data