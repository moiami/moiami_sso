from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.data.schemas.user import UserConnectRoleDto, UserCreateDto, UserDeleteDto
from src.services.user_service import change_role, create_user, delete_user
from tests.conftest import make_user


@pytest.mark.asyncio
@patch("src.services.user_service.insert_token", new_callable=AsyncMock)
@patch("src.services.user_service.insert", new_callable=AsyncMock)
async def test_create_user_returns_tokens(
    mock_insert: AsyncMock, mock_insert_token: AsyncMock
) -> None:
    user_in = UserCreateDto(
        login="newuser",
        password="pass12345",
        name="New",
        surname="User",
        email="new@example.com",
    )

    result = await create_user(user_in)

    assert "access_token" in result
    assert "refresh_token" in result
    mock_insert.assert_awaited_once()
    mock_insert_token.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.services.user_service.get_user_by_id", new_callable=AsyncMock)
@patch("src.services.user_service.update", new_callable=AsyncMock)
async def test_change_role_succeeds_for_admin(
    mock_update: AsyncMock,
    mock_get_user: AsyncMock,
    admin_role,
    member_role,
) -> None:
    admin = make_user(login="admin", roles=[admin_role])
    target = make_user(login="bob", roles=[member_role])
    mock_get_user.side_effect = [admin, target]

    data = UserConnectRoleDto(user_id=target.id, role_id=uuid4())

    result = await change_role(data, admin.id)

    assert result == {"Info": "Success"}
    mock_update.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.services.user_service.get_user_by_id", new_callable=AsyncMock)
async def test_change_role_denied_without_admin(
    mock_get_user: AsyncMock, member_role
) -> None:
    user = make_user(roles=[member_role])
    mock_get_user.return_value = user

    data = UserConnectRoleDto(user_id=uuid4(), role_id=uuid4())

    result = await change_role(data, user.id)

    assert result == {"error": "you not have permission"}


@pytest.mark.asyncio
@patch("src.services.user_service.delete", new_callable=AsyncMock)
@patch("src.services.user_service.get_user_by_id", new_callable=AsyncMock)
async def test_delete_user_succeeds_for_admin(
    mock_get_user: AsyncMock, mock_delete: AsyncMock, admin_role
) -> None:
    admin = make_user(roles=[admin_role])
    mock_get_user.return_value = admin
    target_id = uuid4()

    result = await delete_user(UserDeleteDto(id=target_id), admin.id)

    assert result == {"Info": "Success"}
    mock_delete.assert_awaited_once_with(target_id)


@pytest.mark.asyncio
@patch("src.services.user_service.get_user_by_id", new_callable=AsyncMock)
async def test_delete_user_denied_without_admin(
    mock_get_user: AsyncMock, member_role
) -> None:
    user = make_user(roles=[member_role])
    mock_get_user.return_value = user

    result = await delete_user(UserDeleteDto(id=uuid4()), user.id)

    assert result == {"error": "you not have permission"}
