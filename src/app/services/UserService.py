from uuid import UUID

from app.data.models.User import User
from app.data.repositories.UserRepository import insert_user as insert, get_user, update_user as update, \
    delete_user as delete, get_users
from app.data.schemas.User import UserCreateDto, UserUpdateDto, UserDeleteDto
from constants import ADMIN_USERNAME


async def users():
    try:
        return await get_users()
    except Exception:
        return {"error": "something went wrong"}

async def user(id: UUID):
    try:
        return await get_user(id)
    except Exception:
        return {"error": "something went wrong"}

async def create_user(user_in: UserCreateDto, current_user: str):
    try:
        auth_user: User = await get_user(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            user: User = User(user_in.login, user_in.password, user_in.name, user_in.surname, user_in.email)
            for role in list(user_in.roles):
                user.roles.append(role)
            await insert(user)
            return {"Info": user_in.dict()}
        else:
            return {"error": "you not have permission"}
    except Exception:
        return {"error": "something went wrong"}


async def update_user(user_in: UserUpdateDto, current_user: str):
    try:
        auth_user: User = await get_user(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await update(user_in)
            return {"Info": user_in.dict()}
        else:
            return {"error": "you not have permission"}
    except Exception:
        return {"error": "something went wrong"}


async def delete_user(user_in: UserDeleteDto, current_user: str):
    try:
        auth_user: User = await get_user(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await delete(user_in.id)
            return {"Info": user_in.dict()}
        else:
            return {"error": "you not have permission"}
    except Exception:
        return {"error": "something went wrong"}
