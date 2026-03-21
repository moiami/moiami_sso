from uuid import UUID

from sqlalchemy import select, delete

from app.data.models.Role import Role
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.data.schemas.Role import RoleUpdateDto
from constants import DB_URL

engine = create_async_engine(DB_URL, echo=True, future=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_roles():
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Role).options())
            data = result.scalars().all()
            return data


async def get_role(id: UUID) -> Role | None:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Role).where(Role.id == id).options())
            return result.scalar()


async def insert_role(new_role: Role) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add(new_role)


async def update_role(role: RoleUpdateDto) -> None:
    async with async_session() as session:
        async with session.begin():
            role_to_update: Role = await get_role(role.id)
            role_to_update.name = role.name
            role_to_update.description = role.description
            await session.refresh(role_to_update)


async def delete_role(role: UUID) -> None:
    async with async_session() as session:
        async with session.begin():
            stmt = delete(Role).where(Role.id == role)
            await session.execute(stmt)
