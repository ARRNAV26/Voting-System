import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app

@pytest.mark.asyncio
def get_auth_token(ac, username, email, password):
    await ac.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    resp = await ac.post("/api/auth/login", data={
        "username": username,
        "password": password
    })
    return resp.json()["access_token"]

@pytest.mark.asyncio
async def test_vote_crud(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # User 1 creates suggestion
        token1 = await get_auth_token(ac, "voteuser1", "voteuser1@example.com", "voteuser1pass")
        headers1 = {"Authorization": f"Bearer {token1}"}
        resp = await ac.post("/api/suggestions/", json={
            "title": "Vote Suggestion",
            "description": "Vote test.",
            "category": "General"
        }, headers=headers1)
        suggestion = resp.json()
        # User 2 votes
        token2 = await get_auth_token(ac, "voteuser2", "voteuser2@example.com", "voteuser2pass")
        headers2 = {"Authorization": f"Bearer {token2}"}
        resp = await ac.post("/api/votes/", json={
            "suggestion_id": suggestion["id"],
            "is_upvote": True
        }, headers=headers2)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["vote_count"] == 1
        # Update vote
        resp = await ac.post("/api/votes/", json={
            "suggestion_id": suggestion["id"],
            "is_upvote": False
        }, headers=headers2)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["vote_count"] == -1
        # Remove vote
        resp = await ac.delete(f"/api/votes/{suggestion['id']}", headers=headers2)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["vote_count"] == 0
        assert data["user_vote"] is None 