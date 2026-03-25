from uuid import UUID

from fastapi import HTTPException
from starlette import status

from src.constants import ADMIN_USERNAME
from src.data.models.user import User
from src.data.repositories.user_repository import delete_user as delete
from src.data.repositories.user_repository import get_user_by_id, get_users
from src.data.repositories.user_repository import insert_user as insert
from src.data.repositories.user_repository import update_user as update
from src.data.schemas.role import RoleConnectDto, RoleDto
from src.data.schemas.user import (
    UserConnectRoleDto,
    UserCreateDto,
    UserDeleteDto,
    UserDto,
    UserUpdateDto,
)


async def users() -> list[UserDto]:
    try:
        users_arr: list[User] = await get_users()
        users_dto_arr: list[UserDto] = [
            UserDto(
                id=UUID(str(el.id)),
                login=str(el.login),
                name=str(el.first_name),
                surname=str(el.last_name),
                email=str(el.email),
                roles=[
                    RoleDto(id=UUID(str(r.id)), name=str(r.name), description=str(r.description))
                    for r in el.roles
                ],
            )
            for el in users_arr
        ]
        return users_dto_arr
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def user(id: UUID) -> User:
    try:
        return await get_user_by_id(id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def create_user(user_in: UserCreateDto) -> dict[str, str]:
    try:
        user: User = User(
            user_in.login, user_in.password, user_in.name, user_in.surname, user_in.email
        )
        await insert(user)
        return {"Info": "Success"}
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def change_role(data: UserConnectRoleDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            user: User = await get_user_by_id(data.user_id)
            roles: list[RoleConnectDto] = [RoleConnectDto(id=UUID(str(el.id))) for el in user.roles]
            roles.append(RoleConnectDto(id=data.role_id))
            user_to_update: UserUpdateDto = UserUpdateDto(
                id=UUID(str(user.id)),
                password=str(user.password_hash),
                name=str(user.first_name),
                surname=str(user.last_name),
                email=str(user.email),
                roles=roles,
            )
            await update(user_to_update)
            return {"Info": "Success"}
        return {"error": "you not have permission"}
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def update_user(user_in: UserUpdateDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await update(user_in)
            return {"Info": "Success"}
        return {"error": "you not have permission"}
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def delete_user(user_in: UserDeleteDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await delete(user_in.id)
            return {"Info": "Success"}
        return {"error": "you not have permission"}
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e
