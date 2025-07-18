import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app

@pytest.mark.asyncio
def get_auth_token(ac):
    # Register and login a user, return the token
    await ac.post("/api/auth/register", json={
        "username": "sugguser",
        "email": "sugguser@example.com",
        "password": "suggpass123"
    })
    resp = await ac.post("/api/auth/login", data={
        "username": "sugguser",
        "password": "suggpass123"
    })
    return resp.json()["access_token"]

@pytest.mark.asyncio
async def test_suggestion_crud(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        # Create suggestion
        resp = await ac.post("/api/suggestions/", json={
            "title": "Test Suggestion",
            "description": "This is a test suggestion.",
            "category": "General"
        }, headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        suggestion = resp.json()
        assert suggestion["title"] == "Test Suggestion"
        # Read suggestions
        resp = await ac.get("/api/suggestions/", headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        suggestions = resp.json()
        assert any(s["title"] == "Test Suggestion" for s in suggestions)
        # Update suggestion
        resp = await ac.put(f"/api/suggestions/{suggestion['id']}", json={"description": "Updated desc."}, headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        updated = resp.json()
        assert updated["description"] == "Updated desc."
        # Delete suggestion
        resp = await ac.delete(f"/api/suggestions/{suggestion['id']}", headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["message"] == "Suggestion deleted successfully" 