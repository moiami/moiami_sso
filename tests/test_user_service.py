from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.constants import ADMIN_USERNAME
from src.data.models.user import User
from src.data.schemas.role import RoleConnectDto
from src.data.schemas.user import UserConnectRoleDto, UserCreateDto, UserDeleteDto, UserUpdateDto
from src.services.user_service import (
    change_role,
    create_user,
    delete_user,
    update_user,
    user,
    users,
)


@pytest.fixture
def mock_user() -> MagicMock:
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.login = "test"
    user.first_name = "Test"
    user.last_name = "User"
    user.email = "test@example.com"
    user.password_hash = "hash123"
    user.roles = []
    return user


@pytest.fixture
def mock_admin_user(mock_user: MagicMock) -> MagicMock:
    admin_role = MagicMock(name="admin", id=uuid4())
    admin_role.name = ADMIN_USERNAME
    mock_user.roles = [admin_role]
    return mock_user


async def test_users_success() -> None:
    mock_user_obj = MagicMock(spec=User)
    mock_user_obj.id = uuid4()
    mock_user_obj.login = "test"
    mock_user_obj.first_name = "Test"
    mock_user_obj.last_name = "User"
    mock_user_obj.email = "test@example.com"
    mock_user_obj.roles = []

    with patch("src.services.user_service.get_users", AsyncMock(return_value=[mock_user_obj])):
        result = await users()
        assert isinstance(result, list)


async def test_users_error() -> None:
    with patch("src.services.user_service.get_users", AsyncMock(side_effect=Exception("DB Error"))):
        with pytest.raises(HTTPException) as exc:
            await users()
        assert exc.value.status_code == 500


async def test_user_success(mock_user: MagicMock) -> None:
    with patch("src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_user)):
        result = await user(mock_user.id)
        assert result.id == mock_user.id


async def test_user_error() -> None:
    with patch(
        "src.services.user_service.get_user_by_id", AsyncMock(side_effect=Exception("Error"))
    ):
        with pytest.raises(HTTPException) as exc:
            await user(uuid4())
        assert exc.value.status_code == 500


async def test_create_user_success() -> None:
    user_in = UserCreateDto(
        login="test", password="pass", name="Test", surname="User", email="test@example.com"
    )
    with patch("src.services.user_service.insert", AsyncMock()):
        result = await create_user(user_in)
        assert result == {"Info": "Success"}


async def test_create_user_error() -> None:
    user_in = UserCreateDto(
        login="test", password="pass", name="Test", surname="User", email="test@example.com"
    )
    with patch("src.services.user_service.insert", AsyncMock(side_effect=Exception("Error"))):
        with pytest.raises(HTTPException) as exc:
            await create_user(user_in)
        assert exc.value.status_code == 500


async def test_change_role_success(mock_admin_user: MagicMock) -> None:
    data = UserConnectRoleDto(user_id=uuid4(), role_id=uuid4())
    with (
        patch("src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_admin_user)),
        patch("src.services.user_service.update", AsyncMock()),
    ):
        result = await change_role(data, mock_admin_user.id)
        assert result == {"Info": "Success"}


async def test_change_role_no_permission(mock_user: MagicMock) -> None:
    mock_user.roles = [MagicMock(name="user", id=uuid4())]
    data = UserConnectRoleDto(user_id=uuid4(), role_id=uuid4())
    with patch("src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_user)):
        result = await change_role(data, mock_user.id)
        assert "error" in result
        assert "permission" in result["error"]


async def test_update_user_success(mock_admin_user: MagicMock) -> None:
    user_in = UserUpdateDto(
        id=uuid4(),
        password="hash",
        name="Test",
        surname="User",
        email="test@example.com",
        roles=[RoleConnectDto(id=uuid4())],
    )
    with (
        patch("src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_admin_user)),
        patch("src.services.user_service.update", AsyncMock()),
    ):
        result = await update_user(user_in, mock_admin_user.id)
        assert result == {"Info": "Success"}


async def test_update_user_no_permission(mock_user: MagicMock) -> None:
    mock_user.roles = [MagicMock(name="user", id=uuid4())]
    user_in = UserUpdateDto(
        id=uuid4(),
        password="hash",
        name="Test",
        surname="User",
        email="test@example.com",
        roles=[],
    )
    with patch("src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_user)):
        result = await update_user(user_in, mock_user.id)
        assert "error" in result


async def test_delete_user_success(mock_admin_user: MagicMock) -> None:
    user_in = UserDeleteDto(id=uuid4())
    with (
        patch("src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_admin_user)),
        patch("src.services.user_service.delete", AsyncMock()),
    ):
        result = await delete_user(user_in, mock_admin_user.id)
        assert result == {"Info": "Success"}


async def test_delete_user_no_permission(mock_user: MagicMock) -> None:
    mock_user.roles = [MagicMock(name="user", id=uuid4())]
    user_in = UserDeleteDto(id=uuid4())
    with patch("src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_user)):
        result = await delete_user(user_in, mock_user.id)
        assert "error" in result
