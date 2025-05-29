from fastapi.testclient import TestClient
import pytest

def test_login_success(client, test_user):
    response = client.post("/api/auth/login", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["username"] == test_user["username"]

def test_login_invalid_credentials(client):
    response = client.post("/api/auth/login", json={
        "username": "wrong",
        "password": "wrong"
    })
    assert response.status_code == 401

def test_get_current_user(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "username" in data