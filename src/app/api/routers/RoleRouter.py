import logging
from uuid import UUID

from fastapi import APIRouter, Depends

from app.data.schemas.Role import RoleCreateDto, RoleUpdateDto, RoleDeleteDto
from app.services.SecurityService import get_tokens_data
from app.services.RoleService import create_role, update_role, delete_role, get_roles, role as get_role

router = APIRouter(prefix='')


@router.get("/roles")
async def roles(current_user: str = Depends(get_tokens_data)):
    logging.info('GET: /roles.')
    return await get_roles()


@router.get("/role")
async def roles(id: UUID, current_user: str = Depends(get_tokens_data)):
    logging.info('GET: /role.')
    return await get_role(id)


@router.post("/create_role")
async def create(new_role: RoleCreateDto, current_user: str = Depends(get_tokens_data)):
    logging.info('POST: /create_role.')
    return await create_role(new_role, current_user)


@router.patch("/update_role")
async def update(updated_role: RoleUpdateDto, current_user: str = Depends(get_tokens_data)):
    logging.info('PATCH: /update_role.')
    return await update_role(updated_role, current_user)


@router.delete("/delete_role")
async def delete(deleted_role: RoleDeleteDto, current_user: str = Depends(get_tokens_data)):
    logging.info('DELETE: /delete_role.')
    return await delete_role(deleted_role, current_user)
