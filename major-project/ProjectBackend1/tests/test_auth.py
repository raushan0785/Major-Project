"""Integration tests for the Mongo-backed auth API."""

from __future__ import annotations

import os

import pytest
from httpx import AsyncClient, ASGITransport

os.environ.setdefault("MONGODB_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "test_genai_srs")

from app.main import app  # noqa: E402
from app.mongo import close_mongo_connection, connect_to_mongo, db  # noqa: E402


@pytest.fixture(autouse=True)
async def mongo_connection():
    await connect_to_mongo()
    yield
    if db is not None:
        await db.client.drop_database(os.environ["DB_NAME"])
    await close_mongo_connection()


@pytest.fixture(autouse=True)
async def clean_users():
    if db is not None:
        await db.users.delete_many({})


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_signup_creates_user():
    payload = {"email": "alice@example.com", "password": "Secret123!", "full_name": "Alice"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/auth/signup", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == payload["email"]
    assert body["full_name"] == payload["full_name"]
    assert "hashed_password" not in body


@pytest.mark.anyio
async def test_duplicate_signup_returns_400():
    payload = {"email": "bob@example.com", "password": "Secret123!", "full_name": "Bob"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/auth/signup", json=payload)
        duplicate = await client.post("/auth/signup", json=payload)

    assert duplicate.status_code == 400


@pytest.mark.anyio
async def test_login_returns_token():
    payload = {"email": "carol@example.com", "password": "Secret123!", "full_name": "Carol"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/auth/signup", json=payload)
        response = await client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.anyio
async def test_me_returns_profile():
    payload = {"email": "dave@example.com", "password": "Secret123!", "full_name": "Dave"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/auth/signup", json=payload)
        login = await client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
        token = login.json()["access_token"]

        me = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert me.status_code == 200
    profile = me.json()
    assert profile["email"] == payload["email"]
    assert profile["full_name"] == payload["full_name"]
    assert "hashed_password" not in profile
