from fastapi import Depends, Security, Request
from faststream.kafka.publisher.asyncapi import AsyncAPIDefaultPublisher
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from currency_app.cache.connect import get_redis_connection
from currency_app.client.currency import CurrencyClient
from currency_app.client.google import GoogleClient
from currency_app.client.yandex import YandexClient
from currency_app.core.security import api_key_refresh_token, api_key_access_token
from currency_app.db.connect import async_session_factory
from currency_app.exceptions.exceptions import WrongAuthorizationHeaderException
from currency_app.repositories.currency_cache import CurrencyCache
from currency_app.repositories.user import UserRepository
from currency_app.services.auth import AuthService
from currency_app.services.currency import CurrencyService
from currency_app.services.user import UserService
from currency_app.utils.jwt_auth import JWTAuth
from currency_app.utils.unitofwork import UserUnitOfWork


def get_user_repository(
    db_session: Annotated[AsyncSession, Depends(async_session_factory.get_db_session)]
) -> UserRepository:
    return UserRepository(async_session=db_session)


def get_user_uow(
        user_uow: Annotated[UserUnitOfWork, Depends()]
) -> UserUnitOfWork:
    return user_uow


def get_google_client(
        google_client: Annotated[GoogleClient, Depends()]
) -> GoogleClient:
    return google_client


def get_yandex_client(
        yandex_client: Annotated[YandexClient, Depends()]
) -> YandexClient:
    return yandex_client


def get_user_service(
        user_uow: Annotated[UserUnitOfWork, Depends(get_user_uow)]
) -> UserService:
    return UserService(uow=user_uow)


def get_auth_service(
        auth_uow: Annotated[UserUnitOfWork, Depends(get_user_uow)],
        google_client: Annotated[GoogleClient, Depends(get_google_client)],
        yandex_client: Annotated[YandexClient, Depends(get_yandex_client)]
) -> AuthService:
    return AuthService(
        uow=auth_uow,
        google_client=google_client,
        yandex_client=yandex_client,
        jwt_auth=JWTAuth()
    )


def get_access_token_from_header(
        header: Annotated[str, Security(api_key_access_token)]
) -> str:
    if not header:
        raise WrongAuthorizationHeaderException(
            'No Authorization header received'
        )
    bearer, _, token = header.rpartition(' ')
    if bearer.lower() != 'bearer':
        raise WrongAuthorizationHeaderException(
            'Please check if bearer is included in Authorization header'
        )
    if not token:
        raise WrongAuthorizationHeaderException(
            'Please check if token value is included in Authorization header'
        )
    return token


def get_refresh_token_from_header(
        token: Annotated[str, Security(api_key_refresh_token)]
) -> str:
    if token is None:
        raise WrongAuthorizationHeaderException(
            'No X-Refresh-Token header received'
        )
    return token


async def validate_access_token(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        token: Annotated[str, Security(get_access_token_from_header)]
) -> str:
    return await auth_service.validate_token(token, token_type='access', verify_exp=True)


async def validate_refresh_token(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        refresh_token: Annotated[str, Security(get_refresh_token_from_header)],
        access_token: Annotated[str, Security(get_access_token_from_header)]
) -> str:
    await auth_service.validate_token(access_token, token_type='access', verify_exp=False)
    return await auth_service.validate_token(refresh_token, token_type='refresh', verify_exp=True)


def get_currency_client(
        currency_client: Annotated[CurrencyClient, Depends()]
):
    return currency_client


def get_cache_connection(
        cache_connection: Annotated[Redis, Depends(get_redis_connection)]
):
    return cache_connection


def get_currency_cache(
        cache_connection: Annotated[Redis, Depends(get_cache_connection)]
):
    return CurrencyCache(cache_connection)


def get_broker_publisher(request: Request):
    currency_publisher = request.app.state.kafka_broker.publisher
    return currency_publisher


def get_broker_admin(request: Request):
    admin_client = request.app.state.admin_client
    return admin_client


def get_currency_service(
        currency_client: Annotated[CurrencyClient, Depends(get_currency_client)],
        currency_cache: Annotated[CurrencyCache, Depends(get_currency_cache)],
        currency_publisher: Annotated[AsyncAPIDefaultPublisher, Depends(get_broker_publisher)]
):
    return CurrencyService(
        currency_client=currency_client,
        currency_cache=currency_cache,
        currency_publisher=currency_publisher
    )
