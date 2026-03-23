from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from app.data.models.user import User
from app.data.repositories.role_repository import get_role
from app.data.schemas.user import UserUpdateDto
from constants import DB_URL

engine = create_async_engine(DB_URL, echo=True, future=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_users() -> list[User]:
    async with async_session() as session, session.begin():
        result = await session.execute(select(User).options(selectinload(User.roles)))
        return result.scalars().all()


async def get_user_by_id(id:UUID) -> User | None:
    async with async_session() as session, session.begin():
        result = await session.execute(select(User).where(User.id == id).options(selectinload(User.roles)))
        return result.scalar()


async def get_user_by_login(login:str) -> User | None:
    async with async_session() as session, session.begin():
        result = await session.execute(select(User).where(User.login == login).options(selectinload(User.roles)))
        return result.scalar()


async def insert_user(new_user: User) -> None:
    async with async_session() as session, session.begin():
        session.add(new_user)


async def update_user(user: UserUpdateDto) -> None:
    async with async_session() as session, session.begin():
        user_to_update: User = await get_user_by_id(user.id)
        user_to_update.password = user.password
        user_to_update.name = user.name
        user_to_update.surname = user.surname
        user_to_update.email = user.email
        user_to_update.roles = [await get_role(el.id) for el in user.roles]


async def delete_user(user: UUID) -> None:
    async with async_session() as session, session.begin():
        await session.execute(delete(User).where(User.id == user))
