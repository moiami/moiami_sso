from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from src.constants import DB_URL
from src.data.models.role import Role
from src.data.models.user import User
from src.data.schemas.user import UserUpdateDto

engine = create_async_engine(DB_URL, echo=True, future=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_users() -> list[User]:
    async with async_session() as session, session.begin():
        result = await session.execute(select(User).options(selectinload(User.roles)))
        return list(result.scalars().all())


async def get_user_by_id(id: UUID) -> User:
    async with async_session() as session, session.begin():
        result = await session.execute(
            select(User).where(User.id == id).options(selectinload(User.roles))
        )
        return result.scalar_one()


async def get_user_by_login(login: str) -> User:
    async with async_session() as session, session.begin():
        result = await session.execute(
            select(User).where(User.login == login).options(selectinload(User.roles))
        )
        return result.scalar_one()


async def insert_user(new_user: User) -> None:
    async with async_session() as session, session.begin():
        session.add(new_user)


async def update_user(user: UserUpdateDto) -> None:
    async with async_session() as session, session.begin():
        user_to_update: User = (
            await session.execute(
                select(User).where(User.id == user.id).options(selectinload(User.roles))
            )
        ).scalar_one()
        if user_to_update is None:
            raise Exception
        user_to_update.password = user.password
        user_to_update.name = user.name
        user_to_update.surname = user.surname
        user_to_update.email = user.email
        user_to_update.roles.clear()

        for el in user.roles:
            role = (await session.execute(select(Role).where(Role.id == el.id))).scalar()
            if role:
                user_to_update.roles.append(role)


async def delete_user(user: UUID) -> None:
    async with async_session() as session, session.begin():
        await session.execute(delete(User).where(User.id == user))
