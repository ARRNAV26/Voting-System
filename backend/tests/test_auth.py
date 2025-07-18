import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
import asyncio

@pytest.mark.asyncio
async def test_register_and_login(monkeypatch):
    # Use in-memory DB for tests
    monkeypatch.setenv("ENVIRONMENT", "test")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Register
        resp = await ac.post("/api/auth/register", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["email"] == "testuser@example.com"
        # Login
        resp = await ac.post("/api/auth/login", data={
            "username": "testuser",
            "password": "testpass123"
        })
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer" 