from passlib.context import CryptContext
from typing import Literal

from app.api.schemas.auth import AuthTokens, UserCreds
from app.client.google import GoogleClient
from app.client.yandex import YandexClient
from app.exceptions.exceptions import (
    WrongTokenTypeException,
    RevokedTokenException,
    UserNotFoundException,
    UserPasswordIncorrectException
)
from app.utils.jwt_auth import JWTAuth
from app.utils.unitofwork import UserUnitOfWork


class AuthService:

    def __init__(
            self,
            uow: UserUnitOfWork,
            google_client: GoogleClient,
            yandex_client: YandexClient,
            jwt_auth: JWTAuth
    ):
        self.uow = uow
        self.jwt_auth = jwt_auth
        self.google_client = google_client
        self.yandex_client = yandex_client
        self._bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    async def login(self, user_creds: UserCreds) -> AuthTokens:
        await self._user_authenticate(user_creds)
        async with self.uow:
            email = (await self.uow.user_repo.get_user_by_username(user_creds.username)).email
        await self.revoke_tokens(email)
        access_token, refresh_token = await self.issue_tokens(email)
        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def _verify_password(self, password: str, hashed_password: str) -> bool:
        return self._bcrypt_context.verify(password, hashed_password)

    async def _user_authenticate(self, user_creds: UserCreds):
        async with self.uow:
            user_data = await self.uow.user_repo.get_user_creds(user_creds.username)
        if not user_data:
            raise UserNotFoundException(message='Provide another username')
        _, hashed_password = user_data
        if not await self._verify_password(user_creds.password, hashed_password):
            raise UserPasswordIncorrectException(message='Try another password')

    async def issue_tokens(self, email: str) -> tuple[str, str]:
        access_token = self.jwt_auth.create_jwt_token(email=email, token_type='access')
        refresh_token = self.jwt_auth.create_jwt_token(email=email, token_type='refresh')

        async with self.uow:
            await self.uow.jwt_repo.add_user_tokens((access_token, refresh_token))
            await self.uow.commit()

        return access_token, refresh_token

    async def update_tokens(self, email: str) -> AuthTokens:
        await self.revoke_tokens(email)
        access_token, refresh_token = await self.issue_tokens(email)
        return AuthTokens(access_token=access_token, refresh_token=refresh_token)

    async def revoke_tokens(self, email: str):
        async with self.uow:
            await self.uow.jwt_repo.revoke_user_tokens(email)
            await self.uow.commit()

    async def _check_token_revoked(self, token_id: str) -> bool:
        print(token_id)
        async with self.uow:
            status = await self.uow.jwt_repo.check_token_revoked(token_id)
        return status

    async def validate_token(
            self,
            token: str,
            token_type: Literal['access', 'refresh'],
            verify_exp: bool = False
    ) -> str:
        decoded_token = self.jwt_auth.decode_jwt_token(token, verify_exp=verify_exp)

        if decoded_token['type'] != token_type:
            raise WrongTokenTypeException(message=f'Expected {token_type} token to be received')

        if await self._check_token_revoked(token):
            raise RevokedTokenException(message='Authentication failed due to revoked token')

        if not (email := decoded_token['sub']):
            raise UserNotFoundException(message='User from token not found')

        return email

    async def _check_user_account_by_email(self, user_data):
        async with self.uow:
            user = await self.uow.user_repo.get_user_by_email(user_data.email.lower())
        if not user:
            async with self.uow:
                await self.uow.user_repo.create_user(user_data.model_dump())
                await self.uow.commit()

    def get_google_redirect_url(self) -> str:
        return self.google_client.get_redirect_url()

    async def google_auth(self, code: str) -> AuthTokens:
        user_data = await self.google_client.get_user_data(code)
        await self._check_user_account_by_email(user_data)
        await self.revoke_tokens(user_data.email)
        access_token, refresh_token = await self.issue_tokens(user_data.email)
        return AuthTokens(access_token=access_token, refresh_token=refresh_token)

    def get_yandex_redirect_url(self) -> str:
        return self.yandex_client.get_redirect_url()

    async def yandex_auth(self, code: str) -> AuthTokens:
        user_data = await self.yandex_client.get_user_data(code)
        await self._check_user_account_by_email(user_data)
        await self.revoke_tokens(user_data.email)
        access_token, refresh_token = await self.issue_tokens(user_data.email)
        return AuthTokens(access_token=access_token, refresh_token=refresh_token)