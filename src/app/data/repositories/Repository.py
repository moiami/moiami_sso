from sqlalchemy import select, UUID
from sqlalchemy.orm import joinedload, raiseload, selectinload

from app.data.models.Role import Role
from app.data.models.User import User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine('postgresql+asyncpg://postgres:root@localhost:1234/postgres', echo=True, future=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_users():
    data = []
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).options(selectinload(User.roles)) )
            data = result.scalars().all()
    return data

async def get_user(id) -> User | None:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.id == id).options(selectinload(User.roles)))
            return result.scalar()

async def insert_user(new_user:User) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add(new_user)

async def insert_role(new_role:Role) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add(new_role)