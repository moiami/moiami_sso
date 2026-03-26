from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import jwt
import pytest
from fastapi import HTTPException

from src.data.models.token import Token
from src.data.models.user import User
from src.data.schemas.user import UserLoginDto
from src.services.security_service import (
    create_jwt,
    get_access_tokens_data,
    get_refresh_tokens_data,
    login,
    refresh,
    validate_token,
)


@pytest.fixture
def mock_user() -> MagicMock:
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.login = "testuser"
    user.first_name = "Test"
    user.last_name = "User"
    user.email = "test@example.com"
    role_mock = MagicMock()
    role_mock.name = "admin"
    role_mock.id = uuid4()
    user.roles = [role_mock]

    user.check_password = MagicMock(return_value=True)
    return user


@pytest.fixture
def mock_token() -> MagicMock:
    token = MagicMock(spec=Token)
    token.id = uuid4()
    token.token = "mock_refresh_token"
    token.status = True
    return token


async def test_login_success(mock_user: MagicMock) -> None:
    user_in = UserLoginDto(login="testuser", password="correct_password")

    with (
        patch("src.services.security_service.get_user_by_login", AsyncMock(return_value=mock_user)),
        patch(
            "src.services.security_service.create_jwt",
            AsyncMock(side_effect=["access_123", "refresh_456"]),
        ),
        patch("src.services.security_service.insert_token", AsyncMock()),
    ):
        result = await login(user_in)

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["user_id"] == str(mock_user.id)
        assert result["access_token"] == "access_123"
        assert result["refresh_token"] == "refresh_456"


async def test_login_user_not_found() -> None:
    user_in = UserLoginDto(login="unknown", password="pass")

    with patch("src.services.security_service.get_user_by_login", AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc:
            await login(user_in)

        assert exc.value.status_code == 401
        assert exc.value.detail == "incorrect data"


async def test_login_wrong_password(mock_user: MagicMock) -> None:
    user_in = UserLoginDto(login="testuser", password="wrong_password")
    mock_user.check_password.return_value = False

    with patch(
        "src.services.security_service.get_user_by_login", AsyncMock(return_value=mock_user)
    ):
        result = await login(user_in)

        assert result == {"Info": "Login Failed"}


async def test_refresh_success(mock_user: MagicMock, mock_token: MagicMock) -> None:
    with (
        patch("src.services.security_service.get_user_by_id", AsyncMock(return_value=mock_user)),
        patch(
            "src.services.security_service.create_jwt",
            AsyncMock(side_effect=["new_access", "new_refresh"]),
        ),
        patch("src.services.security_service.update_token", AsyncMock()),
        patch("src.services.security_service.insert_token", AsyncMock()),
    ):
        result = await refresh(mock_user.id, mock_token)

        assert result["access_token"] == "new_access"
        assert result["refresh_token"] == "new_refresh"
        assert mock_token.status is False


async def test_refresh_database_error(mock_user: MagicMock, mock_token: MagicMock) -> None:
    with (
        patch(
            "src.services.security_service.get_user_by_id",
            AsyncMock(side_effect=Exception("DB error")),
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            await refresh(mock_user.id, mock_token)

        assert exc.value.status_code == 500


async def test_create_jwt_access_token() -> None:
    payload = {"id": str(uuid4()), "role": "admin"}
    token = await create_jwt(payload, "access")

    assert isinstance(token, str)
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert decoded["id"] == payload["id"]
    assert "exp" in decoded


async def test_create_jwt_refresh_token() -> None:
    payload = {"id": str(uuid4()), "user_id": str(uuid4())}
    token = await create_jwt(payload, "refresh")

    assert isinstance(token, str)
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert decoded["id"] == payload["id"]


async def test_validate_token_valid(mock_user: MagicMock, mock_token: MagicMock) -> None:
    user_id = str(uuid4())
    token_str = await create_jwt({"id": user_id}, "access")

    mock_token.status = True

    with (
        patch("src.services.security_service.get_token", AsyncMock(return_value=mock_token)),
        patch("src.services.security_service.get_user_by_id", AsyncMock(return_value=mock_user)),
    ):
        result = await validate_token(token_str)

        assert result["id"] == user_id
        assert result["login"] == mock_user.login
        assert result["is_valid"] == "True"
        assert "admin" in result["roles"]


async def test_validate_token_expired() -> None:
    from src.constants import ALGORITHM, SECRET_KEY

    expired_payload = {"id": str(uuid4()), "exp": 0}
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exc:
        await validate_token(expired_token)

    assert exc.value.status_code == 401
    assert exc.value.detail["info"] == "The token has expired"
    assert exc.value.detail["is_valid"] == "False"


async def test_validate_token_invalid_signature() -> None:
    invalid_token = "eyJhbGciOiJIUzI1NiJ9.eyJpZCI6InRlc3QifQ.invalid_signature"

    with pytest.raises(HTTPException) as exc:
        await validate_token(invalid_token)

    assert exc.value.status_code == 401
    assert exc.value.detail["info"] == "Invalid token"


async def test_validate_token_not_in_db(mock_token: MagicMock) -> None:
    user_id = str(uuid4())
    token_str = await create_jwt({"id": user_id}, "access")

    with (
        patch("src.services.security_service.get_token", AsyncMock(return_value=None)),
    ):
        with pytest.raises(HTTPException) as exc:
            await validate_token(token_str)
        assert exc.value.status_code == 401

    mock_token.status = False
    with (
        patch("src.services.security_service.get_token", AsyncMock(return_value=mock_token)),
    ):
        with pytest.raises(HTTPException) as exc:
            await validate_token(token_str)
        assert exc.value.status_code == 401


async def test_get_refresh_tokens_data_success(mock_token: MagicMock) -> None:
    user_id = uuid4()
    token_str = await create_jwt({"id": str(mock_token.id), "user_id": str(user_id)}, "refresh")

    with patch("src.services.security_service.get_token", AsyncMock(return_value=mock_token)):
        result_token, result_user_id = await get_refresh_tokens_data(token_str)

        assert result_token.id == mock_token.id
        assert result_user_id == user_id


async def test_get_refresh_tokens_data_invalid() -> None:
    with pytest.raises(HTTPException) as exc:
        await get_refresh_tokens_data("invalid_token")

    assert exc.value.status_code == 401


async def test_get_access_tokens_data_success() -> None:
    user_id = uuid4()
    token_str = await create_jwt({"id": str(user_id)}, "access")

    result = await get_access_tokens_data(token_str)

    assert result == user_id


async def test_get_access_tokens_data_invalid() -> None:
    with pytest.raises(HTTPException) as exc:
        await get_access_tokens_data("bad_token")

    assert exc.value.status_code == 401
