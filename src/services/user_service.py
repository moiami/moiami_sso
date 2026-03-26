from uuid import UUID, uuid4

from fastapi import HTTPException
from starlette import status

from src.constants import ADMIN_USERNAME
from src.data.models.token import Token
from src.data.models.user import User
from src.data.repositories.auth_repository import insert_token
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
from src.services.security_service import create_jwt


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
        id_us: UUID = uuid4()
        user: User = User(
            user_in.login, user_in.password, user_in.name, user_in.surname, user_in.email
        )
        user.id = id_us
        await insert(user)
        access_token = await create_jwt({"id": str(id_us), "roles": []}, "access")
        refresh_token = await create_jwt({"id": str(id_us), "user_id": str(id_us)}, "refresh")
        await insert_token(Token(id_us, refresh_token, True))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
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
