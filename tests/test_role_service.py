from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.data.models.role import Role
from src.data.schemas.role import RoleCreateDto, RoleDeleteDto, RoleUpdateDto
from src.services.role_service import create_role, delete_role, role, roles, update_role
from tests.conftest import make_user


@pytest.mark.asyncio
@patch("src.services.role_service.get_roles", new_callable=AsyncMock)
async def test_roles_returns_dto_list(mock_get_roles: AsyncMock) -> None:
    db_role = Role("admin", "Administrator")
    db_role.id = uuid4()
    mock_get_roles.return_value = [db_role]

    result = await roles()

    assert len(result) == 1
    assert result[0].name == "admin"
    assert result[0].id == db_role.id


@pytest.mark.asyncio
@patch("src.services.role_service.get_role", new_callable=AsyncMock)
async def test_role_returns_dto(mock_get_role: AsyncMock) -> None:
    db_role = Role("member", "Member role")
    db_role.id = uuid4()
    mock_get_role.return_value = db_role

    result = await role(db_role.id)

    assert result.name == "member"
    assert result.id == db_role.id


@pytest.mark.asyncio
@patch("src.services.role_service.get_role", new_callable=AsyncMock)
async def test_role_raises_404_when_missing(mock_get_role: AsyncMock) -> None:
    mock_get_role.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await role(uuid4())

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
@patch("src.services.role_service.insert", new_callable=AsyncMock)
@patch("src.services.role_service.get_user_by_id", new_callable=AsyncMock)
async def test_create_role_succeeds_for_admin(
    mock_get_user: AsyncMock, mock_insert: AsyncMock, admin_role
) -> None:
    admin = make_user(roles=[admin_role])
    mock_get_user.return_value = admin
    role_in = RoleCreateDto(name="editor", description="Can edit content")

    result = await create_role(role_in, admin.id)

    assert result == {"Info": "Success"}
    mock_insert.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.services.role_service.get_user_by_id", new_callable=AsyncMock)
async def test_create_role_forbidden_for_non_admin(
    mock_get_user: AsyncMock, member_role
) -> None:
    user = make_user(roles=[member_role])
    mock_get_user.return_value = user

    with pytest.raises(HTTPException) as exc_info:
        await create_role(RoleCreateDto(name="editor", description="desc"), user.id)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
@patch("src.services.role_service.update", new_callable=AsyncMock)
@patch("src.services.role_service.get_user_by_id", new_callable=AsyncMock)
async def test_update_role_succeeds_for_admin(
    mock_get_user: AsyncMock, mock_update: AsyncMock, admin_role
) -> None:
    admin = make_user(roles=[admin_role])
    mock_get_user.return_value = admin
    role_in = RoleUpdateDto(id=uuid4(), name="admin", description="Updated")

    result = await update_role(role_in, admin.id)

    assert result == {"Info": "Success"}
    mock_update.assert_awaited_once_with(role_in)


@pytest.mark.asyncio
@patch("src.services.role_service.delete", new_callable=AsyncMock)
@patch("src.services.role_service.get_user_by_id", new_callable=AsyncMock)
async def test_delete_role_succeeds_for_admin(
    mock_get_user: AsyncMock, mock_delete: AsyncMock, admin_role
) -> None:
    admin = make_user(roles=[admin_role])
    mock_get_user.return_value = admin
    role_id = uuid4()

    result = await delete_role(RoleDeleteDto(id=role_id), admin.id)

    assert result == {"Info": "Success"}
    mock_delete.assert_awaited_once_with(role_id)
