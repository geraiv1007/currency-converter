from fastapi import APIRouter, Depends
from typing import Annotated

from currency_app.api.schemas.user import BasicUserCreate, UserCreatedResponse, UserInfo
from currency_app.core.dependency import get_user_service, validate_access_token
from currency_app.services.user import UserService


user_router = APIRouter(
    prefix='/user',
    tags=['user']
)

@user_router.post(
    '/create',
    response_model=UserCreatedResponse,
)
async def create_user(
        user_data: BasicUserCreate,
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserCreatedResponse:
    return await user_service.create_user(user_data)


@user_router.get('/me')
async def get_current_user(
        email: Annotated[str, Depends(validate_access_token)],
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserInfo:
    return await user_service.get_user_info(email)