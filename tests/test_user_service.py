from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.constants import ADMIN_USERNAME
from src.data.models.user import User
from src.data.schemas.role import RoleConnectDto
from src.data.schemas.user import (
    UserConnectRoleDto,
    UserCreateDto,
    UserDeleteDto,
    UserUpdateDto,
)
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
    user.login = "testuser"
    user.first_name = "Test"
    user.last_name = "User"
    user.email = "test@example.com"
    user.password_hash = "hashed_password"
    user.roles = []
    user.check_password = MagicMock(return_value=True)
    return user


@pytest.fixture
def mock_admin_user(mock_user: MagicMock) -> MagicMock:
    admin_role = MagicMock(name="admin", id=uuid4())
    admin_role.name = ADMIN_USERNAME
    mock_user.roles = [admin_role]
    return mock_user


@pytest.fixture
def mock_regular_user(mock_user: MagicMock) -> MagicMock:
    user_role = MagicMock(name="user", id=uuid4())
    user_role.name = "user"
    mock_user.roles = [user_role]
    return mock_user


async def test_users_success() -> None:
    mock_user_obj = MagicMock(spec=User)
    mock_user_obj.id = uuid4()
    mock_user_obj.login = "user1"
    mock_user_obj.first_name = "First"
    mock_user_obj.last_name = "Last"
    mock_user_obj.email = "user1@example.com"
    mock_user_obj.roles = []

    with patch("src.services.user_service.get_users", AsyncMock(return_value=[mock_user_obj])):
        result = await users()

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].id == mock_user_obj.id


async def test_users_database_error() -> None:
    with patch("src.services.user_service.get_users", AsyncMock(side_effect=Exception("DB error"))):
        with pytest.raises(HTTPException) as exc:
            await users()

        assert exc.value.status_code == 500
        assert exc.value.detail == "INTERNAL SERVER ERROR"


async def test_user_success(mock_user: MagicMock) -> None:
    with patch("src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_user)):
        result = await user(mock_user.id)

        assert result.id == mock_user.id
        assert result.login == mock_user.login


async def test_user_not_found() -> None:
    with patch("src.services.user_service.get_user_by_id", AsyncMock(return_value=None)):
        result = await user(uuid4())

        assert result is None


async def test_user_database_error() -> None:
    with patch(
        "src.services.user_service.get_user_by_id", AsyncMock(side_effect=Exception("Error"))
    ):
        with pytest.raises(HTTPException) as exc:
            await user(uuid4())

        assert exc.value.status_code == 500


async def test_create_user_success() -> None:
    user_in = UserCreateDto(
        login="newuser", password="secure_pass", name="New", surname="User", email="new@example.com"
    )

    with (
        patch("src.services.user_service.insert", AsyncMock()),
        patch(
            "src.services.user_service.create_jwt", AsyncMock(side_effect=["acc_tok", "ref_tok"])
        ),
        patch("src.services.user_service.insert_token", AsyncMock()),
    ):
        result = await create_user(user_in)

        assert "access_token" in result
        assert "refresh_token" in result


async def test_create_user_database_error() -> None:
    user_in = UserCreateDto(
        login="newuser", password="pass", name="New", surname="User", email="new@example.com"
    )

    with patch("src.services.user_service.insert", AsyncMock(side_effect=Exception("DB error"))):
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


async def test_change_role_no_permission(mock_regular_user: MagicMock) -> None:
    data = UserConnectRoleDto(user_id=uuid4(), role_id=uuid4())

    with patch(
        "src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_regular_user)
    ):
        result = await change_role(data, mock_regular_user.id)

        assert "error" in result
        assert "permission" in result["error"].lower()


async def test_update_user_success(mock_admin_user: MagicMock) -> None:
    user_in = UserUpdateDto(
        id=uuid4(),
        password="new_hash",
        name="Updated",
        surname="Name",
        email="updated@example.com",
        roles=[RoleConnectDto(id=uuid4())],
    )

    with (
        patch("src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_admin_user)),
        patch("src.services.user_service.update", AsyncMock()),
    ):
        result = await update_user(user_in, mock_admin_user.id)

        assert result == {"Info": "Success"}


async def test_update_user_no_permission(mock_regular_user: MagicMock) -> None:
    user_in = UserUpdateDto(
        id=uuid4(),
        password="hash",
        name="Test",
        surname="User",
        email="test@example.com",
        roles=[],
    )

    with patch(
        "src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_regular_user)
    ):
        result = await update_user(user_in, mock_regular_user.id)

        assert "error" in result


async def test_delete_user_success(mock_admin_user: MagicMock) -> None:
    user_in = UserDeleteDto(id=uuid4())

    with (
        patch("src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_admin_user)),
        patch("src.services.user_service.delete", AsyncMock()),
    ):
        result = await delete_user(user_in, mock_admin_user.id)

        assert result == {"Info": "Success"}


async def test_delete_user_no_permission(mock_regular_user: MagicMock) -> None:
    user_in = UserDeleteDto(id=uuid4())

    with patch(
        "src.services.user_service.get_user_by_id", AsyncMock(return_value=mock_regular_user)
    ):
        result = await delete_user(user_in, mock_regular_user.id)

        assert "error" in result
