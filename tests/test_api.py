from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.data.models.role import Role
from src.main import app
from src.services.security_service import get_access_tokens_data, validate_token
from tests.conftest import make_user


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
@patch("src.api.routers.auth_router.security_login", new_callable=AsyncMock)
async def test_auth_login_endpoint(mock_login: AsyncMock, client: AsyncClient) -> None:
    user_id = str(uuid4())
    mock_login.return_value = {
        "id": user_id,
        "login": "alice",
        "name": "Alice",
        "surname": "Smith",
        "email": "alice@example.com",
        "roles": [],
        "access_token": "access",
        "refresh_token": "refresh",
    }

    response = await client.post(
        "/api/v1/auth/login",
        json={"login": "alice", "password": "secret123"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "access"
    assert response.headers["X-User-Id"] == user_id


@pytest.mark.asyncio
async def test_auth_validate_endpoint_sets_headers(client: AsyncClient) -> None:
    user_id = str(uuid4())

    async def mock_validate() -> dict[str, str]:
        return {
            "user_id": user_id,
            "user_roles": "['admin']",
            "is_valid": "True",
        }

    app.dependency_overrides[validate_token] = mock_validate
    try:
        response = await client.post("/api/v1/auth/validate")
    finally:
        app.dependency_overrides.pop(validate_token, None)

    assert response.status_code == 200
    assert response.headers["X-User-Id"] == user_id
    assert response.headers["X-User-Role"] == "['admin']"


@pytest.mark.asyncio
@patch("src.api.routers.user_router.get_users", new_callable=AsyncMock)
async def test_users_list_with_auth_override(
    mock_get_users: AsyncMock,
    client: AsyncClient,
    admin_role: Role,
) -> None:
    user = make_user(roles=[admin_role])
    mock_get_users.return_value = []

    async def mock_auth() -> object:
        return user.id

    app.dependency_overrides[get_access_tokens_data] = mock_auth
    try:
        response = await client.get("/api/v1/user/users")
    finally:
        app.dependency_overrides.pop(get_access_tokens_data, None)

    assert response.status_code == 200
    assert response.json() == []
