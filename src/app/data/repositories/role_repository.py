from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.data.models.role import Role
from app.data.schemas.role import RoleUpdateDto
from constants import DB_URL

engine = create_async_engine(DB_URL, echo=True, future=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_roles() -> Sequence[Any]:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Role).options())
        return result.scalars().all()


async def get_role(id: UUID) -> Role | None:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Role).where(Role.id == id).options())
        return result.scalar()


async def insert_role(new_role: Role) -> None:
    async with async_session() as session, session.begin():
        session.add(new_role)


async def update_role(role: RoleUpdateDto) -> None:
    async with async_session() as session, session.begin():
        role_to_update: Role = await get_role(role.id)
        role_to_update.name = role.name
        role_to_update.description = role.description


async def delete_role(role: UUID) -> None:
    async with async_session() as session, session.begin():
        await session.execute(delete(Role).where(Role.id == role))
