from abc import ABC, abstractmethod

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    pass


class Repository(AbstractRepository):

    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session

    def create_user(self, user: UserCreateSchema):
        pass