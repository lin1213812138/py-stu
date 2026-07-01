import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_me(async_client: AsyncClient):
    reg = {"username": "meuser", "email": "me@example.com", "password": "Pass1234"}
    await async_client.post("/api/v1/auth/register", json=reg)
    login_resp = await async_client.post("/api/v1/auth/login", json={"username": "meuser", "password": "Pass1234"})
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = await async_client.get("/api/v1/users/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["username"] == "meuser"
