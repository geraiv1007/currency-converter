from passlib.context import CryptContext
from typing import Any

from currency_app.api.schemas.user import BasicUserCreate, NewUserProfile, UserCreatedResponse
from currency_app.api.schemas.user import UserInfo
from currency_app.exceptions.exceptions import UserAlreadyExistsException
from currency_app.utils.unitofwork import UserUnitOfWork


class UserService:

    def __init__(self, uow: UserUnitOfWork):
        self.uow = uow
        self._bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    async def create_user(self, user: BasicUserCreate) -> UserCreatedResponse:
        async with self.uow:
            user_data = self._user_data_prep(user)
            await self._check_user_registration(user_data)
            new_user = await self.uow.user_repo.create_user(user_data)
            await self.uow.commit()
        new_user_profile = NewUserProfile(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email
        )
        return UserCreatedResponse(user=new_user_profile)

    def _user_data_prep(self, user_data: BasicUserCreate) -> dict[str, Any]:
        user_data = user_data.model_dump()
        user_data['hashed_password'] = self._create_password_hash(user_data.pop('password'))
        user_data['email'] = user_data['email'].lower()
        return user_data

    def _create_password_hash(self, password: str) -> str:
        return self._bcrypt_context.hash(password)

    async def _check_user_registration(self, user: dict[str, Any]):
        username_count, email_count = await self.uow.user_repo.get_user_count(user['username'], user['email'])
        message = None
        if username_count and email_count:
            message = 'username and email'
        elif username_count:
            message = 'username'
        elif email_count:
            message = 'email'
        if message:
            raise UserAlreadyExistsException(
                message=f'User with such {message} is already registered. Try another {message}'
            )

    async def get_user_info(self, email: str) -> UserInfo:
        async with self.uow:
            user_info = await self.uow.user_repo.get_user_by_email(email)
            await self.uow.commit()
        return UserInfo.model_validate(user_info, from_attributes=True)