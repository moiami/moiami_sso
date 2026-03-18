from sqlalchemy import select
from sqlalchemy.orm import joinedload, raiseload, selectinload

from app.data.models.Role import Role
from app.data.models.User import User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine('postgresql+asyncpg://postgres:root@localhost:1234/postgres', echo=True, future=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_users():
    #будет переделано
    data = []
    res = []
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).options(selectinload(User.roles)) )
            data = result.scalars().all()

    for user in data:
        us = User(user.login,user.password_hash,user.first_name,user.last_name,user.email)
        for role in list(user.roles):
            us.assign_role(role)
        res.append(us)
    return res

async def get_user(username: str) -> User | None:
    #будет переделано
    for user in await get_users():
        if user.login == username:
            return user
    return None

async def insert_user(new_user:User) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add(new_user)

async def insert_role(new_role:Role) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add(new_role)