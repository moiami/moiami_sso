import logging
from uuid import UUID

from fastapi import APIRouter, Depends

from src.data.schemas.role import RoleCreateDto, RoleDeleteDto, RoleDto, RoleUpdateDto
from src.services.role_service import (
    create_role,
    delete_role,
    update_role,
)
from src.services.role_service import (
    role as get_role,
)
from src.services.role_service import (
    roles as get_roles,
)
from src.services.security_service import get_access_tokens_data

router = APIRouter(prefix="/api/v1/roles")


@router.get("/roles")
async def roles(current_user: UUID = Depends(get_access_tokens_data)) -> list[RoleDto]:
    logging.info("GET: /roles.", current_user)
    return await get_roles()


@router.get("/role")
async def role(id: UUID, _current_user: UUID = Depends(get_access_tokens_data)) -> RoleDto:
    logging.info("GET: /role.")
    return await get_role(id)


@router.post("/create_role")
async def create(
    new_role: RoleCreateDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    logging.info("POST: /create_role.")
    return await create_role(new_role, current_user)


@router.patch("/update_role")
async def update(
    updated_role: RoleUpdateDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    logging.info("PATCH: /update_role.")
    return await update_role(updated_role, current_user)


@router.delete("/delete_role")
async def delete(
    deleted_role: RoleDeleteDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    logging.info("DELETE: /delete_role.")
    return await delete_role(deleted_role, current_user)
