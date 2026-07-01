import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(async_client: AsyncClient):
    payload = {"username": "testuser", "email": "test@example.com", "password": "Test1234"}
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_register_duplicate(async_client: AsyncClient):
    payload = {"username": "dupuser", "email": "dup@example.com", "password": "Test1234"}
    await async_client.post("/api/v1/auth/register", json=payload)
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400
    assert resp.json()["code"] == 10002


@pytest.mark.asyncio
async def test_login(async_client: AsyncClient):
    reg = {"username": "loginuser", "email": "login@example.com", "password": "Pass1234"}
    await async_client.post("/api/v1/auth/register", json=reg)
    resp = await async_client.post("/api/v1/auth/login", json={"username": "loginuser", "password": "Pass1234"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert "access_token" in data["data"]
