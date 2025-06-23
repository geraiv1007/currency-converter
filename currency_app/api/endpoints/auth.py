from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from typing import Annotated

from currency_app.api.schemas.auth import AuthTokens, UserCreds
from currency_app.core.dependency import get_auth_service, validate_refresh_token
from currency_app.services.auth import AuthService


auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@auth_router.post(
    '/login',
    response_model=AuthTokens
)
async def login(
        user_creds: UserCreds,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthTokens:
    return await auth_service.login(user_creds)


@auth_router.post('/refresh_tokens')
async def refresh_tokens(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    email: Annotated[str, Depends(validate_refresh_token)]
) -> AuthTokens:
    return await auth_service.update_tokens(email)


@auth_router.get(
    '/login/google',
    response_class=PlainTextResponse,
    description='In Swagger please manually open returned URL'
)
async def login_google(
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> str:
    return auth_service.get_google_redirect_url()


@auth_router.get(
    '/google',
    response_model=AuthTokens,
    description='Don\'t send requests manually. Used as redirect URI for google auth'
)
async def google_authentication(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        code: Annotated[str, Query()]
) -> AuthTokens:
    return await auth_service.google_auth(code)


@auth_router.get(
    '/login/yandex',
    response_class=PlainTextResponse,
    description='In Swagger please manually open returned URL'
)
async def login_yandex(
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> str:
    return auth_service.get_yandex_redirect_url()


@auth_router.get(
    '/yandex',
    response_model=AuthTokens,
    description='Don\'t send requests manually. Used as redirect URI for yandex auth'
)
async def yandex_authentication(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        code: Annotated[str, Query()]
) -> AuthTokens:
    return await auth_service.yandex_auth(code)
