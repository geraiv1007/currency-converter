from abc import ABC, abstractmethod
from currency_app.db.connect import async_session_factory
from currency_app.repositories.jwt import JWTRepository
from currency_app.repositories.user import UserRepository


class UOW(ABC):

    @classmethod
    @abstractmethod
    def repo(cls):
        pass

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, *args):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass


class BaseUOW(UOW):

    repo = None

    def __init__(self):
        self.async_session_factory = async_session_factory

    async def __aenter__(self):
        self.async_session = await self.async_session_factory.get_db_session()
        for name, repo in self.repo.items():
            setattr(self, name, repo(async_session=self.async_session))

    async def __aexit__(self, *args):
        await self.rollback()
        await self.async_session.close()

    async def commit(self):
        await self.async_session.commit()

    async def rollback(self):
        await self.async_session.rollback()


class UserUnitOfWork(BaseUOW):

    def __init__(self):
        super().__init__()

    repo = {'user_repo': UserRepository, 'jwt_repo': JWTRepository}
