from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

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
    user.id = str(uuid4())
    user.login = "test"
    user.roles = [MagicMock(name="admin")]
    user.check_password = MagicMock(return_value=True)
    return user


@pytest.fixture
def mock_token() -> MagicMock:
    token = MagicMock(spec=Token)
    token.id = uuid4()
    token.status = True
    return token


async def test_login_success(mock_user: MagicMock) -> None:
    user_in = UserLoginDto(login="test", password="pass")
    with (
        patch("src.services.security_service.get_user_by_login", AsyncMock(return_value=mock_user)),
        patch("src.services.security_service.create_jwt", AsyncMock(side_effect=["acc", "ref"])),
        patch("src.services.security_service.insert_token", AsyncMock()),
    ):
        result = await login(user_in)
        assert "access_token" in result


async def test_login_user_not_found() -> None:
    user_in = UserLoginDto(login="test", password="pass")
    with patch("src.services.security_service.get_user_by_login", AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc:
            await login(user_in)
        assert exc.value.status_code == 401


async def test_login_wrong_password(mock_user: MagicMock) -> None:
    user_in = UserLoginDto(login="test", password="wrong")
    mock_user.check_password.return_value = False
    with patch(
        "src.services.security_service.get_user_by_login", AsyncMock(return_value=mock_user)
    ):
        result = await login(user_in)
        assert result == {"Info": "Login Failed"}


async def test_refresh_success(mock_user: MagicMock, mock_token: MagicMock) -> None:
    with (
        patch("src.services.security_service.get_user_by_id", AsyncMock(return_value=mock_user)),
        patch("src.services.security_service.create_jwt", AsyncMock(side_effect=["acc", "ref"])),
        patch("src.services.security_service.update_token", AsyncMock()),
        patch("src.services.security_service.insert_token", AsyncMock()),
    ):
        result = await refresh(mock_user.id, mock_token)
        assert "access_token" in result
        assert mock_token.status is False


async def test_create_jwt_access() -> None:
    token = await create_jwt({"id": str(uuid4())}, "access")
    assert isinstance(token, str)
    assert len(token) > 0


async def test_create_jwt_refresh() -> None:
    token = await create_jwt({"id": str(uuid4())}, "refresh")
    assert isinstance(token, str)


async def test_validate_token_valid() -> None:
    token = await create_jwt({"id": str(uuid4())}, "access")
    result = await validate_token(token)
    assert result["info"] == "valid"


async def test_validate_token_invalid() -> None:
    result = await validate_token("invalid")
    assert "Invalid" in result["info"]


async def test_get_access_data_success() -> None:
    user_id = str(uuid4())
    token = await create_jwt({"id": user_id}, "access")
    result_id = await get_access_tokens_data(token)
    assert str(result_id) == user_id


async def test_get_access_data_invalid() -> None:
    with pytest.raises(HTTPException) as exc:
        await get_access_tokens_data("invalid")
    assert exc.value.status_code == 401


async def test_get_refresh_data_success(mock_token: MagicMock) -> None:
    user_id = str(uuid4())
    token_str = await create_jwt({"id": str(mock_token.id), "user_id": user_id}, "refresh")
    with patch("src.services.security_service.get_token", AsyncMock(return_value=mock_token)):
        result_token, _ = await get_refresh_tokens_data(token_str)
        assert result_token.id == mock_token.id


async def test_get_refresh_data_invalid() -> None:
    with pytest.raises(HTTPException) as exc:
        await get_refresh_tokens_data("invalid")
    assert exc.value.status_code == 401
