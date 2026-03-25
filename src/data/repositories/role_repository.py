from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.constants import DB_URL
from src.data.models.role import Role
from src.data.schemas.role import RoleUpdateDto

engine = create_async_engine(DB_URL, echo=True, future=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_roles() -> list[Role]:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Role).options())
        return list(result.scalars().all())


async def get_role(id: UUID) -> Role:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Role).where(Role.id == id).options())
        return result.scalar_one()


async def insert_role(new_role: Role) -> None:
    async with async_session() as session, session.begin():
        session.add(new_role)


async def update_role(role: RoleUpdateDto) -> None:
    async with async_session() as session, session.begin():
        role_to_update: Role = (
            await session.execute(select(Role).where(Role.id == id).options())
        ).scalar_one()
        role_to_update.name = role.name
        role_to_update.description = role.description


async def delete_role(role: UUID) -> None:
    async with async_session() as session, session.begin():
        await session.execute(delete(Role).where(Role.id == role))
