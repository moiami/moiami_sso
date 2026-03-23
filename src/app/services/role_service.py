from uuid import UUID

from app.data.models.role import Role
from app.data.models.user import User
from app.data.repositories.role_repository import delete_role as delete
from app.data.repositories.role_repository import get_role, get_roles
from app.data.repositories.role_repository import insert_role as insert
from app.data.repositories.role_repository import update_role as update
from app.data.repositories.user_repository import get_user_by_id
from app.data.schemas.role import RoleCreateDto, RoleDeleteDto, RoleDto, RoleUpdateDto
from constants import ADMIN_USERNAME


async def roles() -> list[Role] | dict[str,str]:
    try:
        return await get_roles()
    except Exception:
        return {"error": "something went wrong"}


async def role(id: UUID) -> RoleDto | dict[str,str]:
    try:
        role:Role = await get_role(id)
        role_dto:RoleDto = RoleDto(id=role.id, name=role.name, description=role.description)
        return role_dto
    except Exception:
        return {"error": "something went wrong"}


async def create_role(role_in: RoleCreateDto, current_user: UUID) -> dict[str,str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            role: Role = Role(role_in.name, role_in.description)
            await insert(role)
            return {"Info": role.dict()}
        return {"error": "you not have permission"}
    except Exception:
        return {"error": "something went wrong"}


async def update_role(role_in: RoleUpdateDto, current_user: UUID) -> dict[str,str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await update(role_in)
            return {"Info": role_in.dict()}
        return {"error": "you not have permission"}
    except Exception:
        return {"error": "something went wrong"}


async def delete_role(role_in: RoleDeleteDto, current_user: UUID) -> dict[str,str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await delete(role_in.id)
            return {"Info": role_in.dict()}
        return {"error": "you not have permission"}
    except Exception:
        return {"error": "something went wrong"}
