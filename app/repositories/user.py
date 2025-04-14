from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UserRepository:

    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session

    async def create_user(self, user: dict) -> User:
        new_user = User(**user)
        self.async_session.add(new_user)
        return new_user

    async def get_user_by_username(self, username: str) -> User:
        stmt = (
            select(User)
            .where(User.username == username)
        )
        user_info = await self.async_session.scalar(stmt)
        return user_info

    async def get_user_by_email(self, email: str) -> User:
        stmt = (
            select(User)
            .where(User.email == email)
        )
        user_info = await self.async_session.scalar(stmt)
        return user_info

    async def get_user_count(self, username: str, email: str) -> tuple[int, int]:
        username_stmt = (
            select(func.count(User.username).label('username')).
            where(User.username == username)
        )
        email_stmt = (
            select(func.count(User.email).label('email')).
            where(User.email == email)
        )
        username_count = await self.async_session.scalar(username_stmt)
        email_count = await self.async_session.scalar(email_stmt)
        return username_count, email_count

    async def get_user_creds(self, username: str) -> tuple[int, int] | None:
        stmt = (
            select(User.username, User.hashed_password)
            .where(User.username == username)
        )
        user_creds = (await self.async_session.execute(stmt)).one_or_none()
        return user_creds




