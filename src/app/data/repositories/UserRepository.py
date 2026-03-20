from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.data.models.User import User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.data.repositories.RoleRepository import get_role
from app.data.schemas.User import UserUpdateDto
from constants import DB_URL

engine = create_async_engine(DB_URL, echo=True, future=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_users():
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).options(selectinload(User.roles)))
            data = result.scalars().all()
            return data


async def get_user(id) -> User | None:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.id == id).options(selectinload(User.roles)))
            return result.scalar()


async def insert_user(new_user: User) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add(new_user)


async def update_user(user: UserUpdateDto) -> None:
    async with async_session() as session:
        async with session.begin():
            user_to_update: User = await get_user(user.id)
            user_to_update.password = user.password
            user_to_update.name = user.name
            user_to_update.surname = user.surname
            user_to_update.email = user.email
            user_to_update.roles = [await get_role(el.id) for el in user.roles]
            await session.refresh(user_to_update)


async def delete_user(user: UUID) -> None:
    async with async_session() as session:
        async with session.begin():
            stmt = delete(User).where(User.id == user)
            await session.execute(stmt)
