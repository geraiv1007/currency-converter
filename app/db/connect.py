from app.core.config import DBSettings

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from typing import AsyncGenerator, Any


class AsyncSessionFactory:

    def __init__(self):
        self.db_settings = DBSettings()
        self.engine = self._async_engine_init()
        self.async_session_maker = async_sessionmaker(bind=self.engine, expire_on_commit=False)

    def _async_engine_init(self):
        engine = create_async_engine(self.db_settings.connection_url)
        return engine

    async def get_db_session(self) -> AsyncSession:
        session = self.async_session_maker()
        return session


async_session_factory = AsyncSessionFactory()