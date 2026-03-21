from uuid import UUID

from app.data.models.Role import Role
from app.data.models.User import User
from app.data.repositories.RoleRepository import insert_role as insert, delete_role as delete, update_role as update, \
    get_roles, get_role
from app.data.repositories.UserRepository import get_user
from app.data.schemas.Role import RoleCreateDto, RoleUpdateDto, RoleDeleteDto
from constants import ADMIN_USERNAME


async def roles():
    try:
        return await get_roles()
    except Exception:
        return {"error": "something went wrong"}


async def role(id: UUID):
    try:
        return await get_role(id)
    except Exception:
        return {"error": "something went wrong"}


async def create_role(role_in: RoleCreateDto, current_user: str):
    try:
        auth_user: User = await get_user(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            role: Role = Role(role_in.name, role_in.description)
            await insert(role)
            return {"Info": role.dict()}
        else:
            return {"error": "you not have permission"}
    except Exception:
        return {"error": "something went wrong"}


async def update_role(role_in: RoleUpdateDto, current_user: str):
    try:
        auth_user: User = await get_user(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await update(role_in)
            return {"Info": role_in.dict()}
        else:
            return {"error": "you not have permission"}
    except Exception:
        return {"error": "something went wrong"}


async def delete_role(role_in: RoleDeleteDto, current_user: str):
    try:
        auth_user: User = await get_user(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await delete(role_in.id)
            return {"Info": role_in.dict()}
        else:
            return {"error": "you not have permission"}
    except Exception as e:
        return {"error": "something went wrong"}
