from uuid import UUID

from fastapi import HTTPException
from starlette import status

from src.constants import ADMIN_USERNAME
from src.data.models.role import Role
from src.data.models.user import User
from src.data.repositories.role_repository import (
    delete_role as delete,
)
from src.data.repositories.role_repository import (
    get_role,
    get_roles,
)
from src.data.repositories.role_repository import (
    insert_role as insert,
)
from src.data.repositories.role_repository import (
    update_role as update,
)
from src.data.repositories.user_repository import get_user_by_id
from src.data.schemas.role import RoleCreateDto, RoleDeleteDto, RoleDto, RoleUpdateDto


async def roles() -> list[RoleDto]:
    try:
        roles_arr: list[Role] = await get_roles()
        if roles_arr is None:
            raise Exception
        result: list[RoleDto] = []
        for role in roles_arr:
            result.append(
                RoleDto(
                    id=UUID(str(role.id)), name=str(role.name), description=str(role.description)
                )
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def role(id: UUID) -> RoleDto:
    try:
        role: Role = await get_role(id)
        if role is None:
            raise TypeError
        role_dto: RoleDto = RoleDto(
            id=UUID(str(role.id)), name=str(role.name), description=str(role.description)
        )
        return role_dto
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def create_role(role_in: RoleCreateDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if auth_user is None:
            raise Exception
        roles: list[Role] = list(auth_user.roles)
        if any(role.name == ADMIN_USERNAME for role in roles):
            role: Role = Role(role_in.name, role_in.description)
            await insert(role)
            return {"Info": "Success"}
        raise ValueError
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def update_role(role_in: RoleUpdateDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if auth_user is None:
            raise Exception
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await update(role_in)
            return {"Info": "Success"}
        raise ValueError
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def delete_role(role_in: RoleDeleteDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if auth_user is None:
            raise Exception
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await delete(role_in.id)
            return {"Info": "Success"}
        raise ValueError
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e
