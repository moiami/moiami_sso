from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import jwt
import pytest
from fastapi import HTTPException

from src.constants import ALGORITHM, CLIENT_ID, ISSUER_URL, PRIVATE_KEY, PUBLIC_KEY
from src.data.models.token import Token
from src.data.schemas.user import UserLoginDto
from src.services.security_service import (
    create_jwt,
    get_access_tokens_data,
    get_refresh_tokens_data,
    login,
    refresh,
    validate_token,
)
from tests.conftest import make_user


@pytest.mark.asyncio
async def test_create_jwt_access_contains_expected_claims() -> None:
    user_id = str(uuid4())
    token = await create_jwt({"id": user_id, "roles": ["admin"]}, "access")
    payload = jwt.decode(
        token, PUBLIC_KEY, algorithms=[ALGORITHM], audience=CLIENT_ID, issuer=ISSUER_URL
    )

    assert payload["sub"] == user_id
    assert payload["id"] == user_id
    assert payload["roles"] == ["admin"]
    assert payload["aud"] == CLIENT_ID
    assert payload["iss"] == ISSUER_URL
    assert payload["exp"] > payload["iat"]


@pytest.mark.asyncio
@patch("src.services.security_service.insert_token", new_callable=AsyncMock)
@patch("src.services.security_service.get_user_by_login", new_callable=AsyncMock)
async def test_login_success_returns_tokens_and_profile(
    mock_get_user: AsyncMock, mock_insert_token: AsyncMock, admin_role
) -> None:
    user = make_user(roles=[admin_role])
    mock_get_user.return_value = user

    result = await login(UserLoginDto(login="alice", password="secret123"))

    assert result["id"] == str(user.id)
    assert result["login"] == "alice"
    assert result["roles"] == ["admin"]
    assert "access_token" in result
    assert "refresh_token" in result
    mock_insert_token.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.services.security_service.get_user_by_login", new_callable=AsyncMock)
async def test_login_returns_failure_on_wrong_password(
    mock_get_user: AsyncMock, admin_role
) -> None:
    mock_get_user.return_value = make_user(roles=[admin_role])

    result = await login(UserLoginDto(login="alice", password="wrong-password"))

    assert result == {"Info": "Login Failed"}


@pytest.mark.asyncio
@patch("src.services.security_service.get_user_by_login", new_callable=AsyncMock)
async def test_login_raises_401_when_user_not_found(mock_get_user: AsyncMock) -> None:
    mock_get_user.side_effect = Exception("not found")

    with pytest.raises(HTTPException) as exc_info:
        await login(UserLoginDto(login="missing", password="secret123"))

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
@patch("src.services.security_service.get_user_by_id", new_callable=AsyncMock)
async def test_validate_token_returns_user_info(mock_get_user: AsyncMock, admin_role) -> None:
    user = make_user(roles=[admin_role])
    mock_get_user.return_value = user
    access_token = await create_jwt(
        {"id": str(user.id), "roles": [admin_role.name]}, "access"
    )

    result = await validate_token(token=access_token)

    assert result["user_id"] == str(user.id)
    assert result["is_valid"] == "True"
    assert "admin" in result["user_roles"]


@pytest.mark.asyncio
async def test_validate_token_raises_401_for_invalid_token() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await validate_token(token="not-a-jwt")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == {"is_valid": "False"}


@pytest.mark.asyncio
@patch("src.services.security_service.get_user_by_id", new_callable=AsyncMock)
async def test_validate_token_raises_401_when_expired(mock_get_user: AsyncMock) -> None:
    user = make_user()
    mock_get_user.return_value = user
    expired = jwt.encode(
        {
            "id": str(user.id),
            "sub": str(user.id),
            "exp": datetime(2000, 1, 1, tzinfo=UTC),
            "iat": datetime(1999, 1, 1, tzinfo=UTC),
            "iss": ISSUER_URL,
            "aud": CLIENT_ID,
        },
        PRIVATE_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        await validate_token(token=expired)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
@patch("src.services.security_service.get_token", new_callable=AsyncMock)
async def test_get_refresh_tokens_data_returns_token_and_user_id(
    mock_get_token: AsyncMock, admin_role
) -> None:
    user = make_user(roles=[admin_role])
    refresh_id = uuid4()
    refresh_token = await create_jwt(
        {"id": str(refresh_id), "user_id": str(user.id)}, "refresh"
    )
    db_token = Token(refresh_id, refresh_token, True)
    mock_get_token.return_value = db_token

    token_row, user_id = await get_refresh_tokens_data(token=refresh_token)

    assert token_row.status is True
    assert user_id == user.id


@pytest.mark.asyncio
@patch("src.services.security_service.get_token", new_callable=AsyncMock)
async def test_get_refresh_tokens_data_raises_401_when_revoked(
    mock_get_token: AsyncMock, admin_role
) -> None:
    user = make_user(roles=[admin_role])
    refresh_id = uuid4()
    refresh_token = await create_jwt(
        {"id": str(refresh_id), "user_id": str(user.id)}, "refresh"
    )
    mock_get_token.return_value = Token(refresh_id, refresh_token, False)

    with pytest.raises(HTTPException) as exc_info:
        await get_refresh_tokens_data(token=refresh_token)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_access_tokens_data_returns_user_id(admin_role) -> None:
    user = make_user(roles=[admin_role])
    access_token = await create_jwt(
        {"id": str(user.id), "roles": [admin_role.name]}, "access"
    )

    user_id = await get_access_tokens_data(token=access_token)

    assert user_id == user.id


@pytest.mark.asyncio
@patch("src.services.security_service.insert_token", new_callable=AsyncMock)
@patch("src.services.security_service.update_token", new_callable=AsyncMock)
@patch("src.services.security_service.get_user_by_id", new_callable=AsyncMock)
async def test_refresh_issues_new_tokens_and_revokes_old(
    mock_get_user: AsyncMock,
    mock_update_token: AsyncMock,
    mock_insert_token: AsyncMock,
    admin_role,
) -> None:
    user = make_user(roles=[admin_role])
    mock_get_user.return_value = user
    old_refresh_id = uuid4()
    old_token = Token(old_refresh_id, "old-refresh", True)

    result = await refresh(user.id, old_token)

    assert "access_token" in result
    assert "refresh_token" in result
    assert old_token.status is False
    mock_update_token.assert_awaited_once_with(old_token)
    mock_insert_token.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.services.security_service.get_user_by_id", new_callable=AsyncMock)
async def test_refresh_raises_500_on_failure(mock_get_user: AsyncMock) -> None:
    mock_get_user.side_effect = Exception("db error")
    old_token = Token(uuid4(), "token", True)

    with pytest.raises(HTTPException) as exc_info:
        await refresh(uuid4(), old_token)

    assert exc_info.value.status_code == 500
