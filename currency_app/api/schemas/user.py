from fastapi import status
from pydantic import BaseModel


class BasicUserCreate(BaseModel):

    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class ExternalAuthUserCreate(BaseModel):

    first_name: str
    last_name: str
    email: str


class GoogleUserCreate(ExternalAuthUserCreate):

    pass


class YandexUserCreate(ExternalAuthUserCreate):

    pass


class UserInfo(BaseModel):

    model_config = {'extra': 'ignore'}

    first_name: str
    last_name: str
    username: str | None = None
    email: str


class NewUserProfile(BaseModel):

    id: int
    username: str
    email: str


class UserCreatedResponse(BaseModel):

    status_code: int = status.HTTP_201_CREATED
    detail: str = 'User created'
    user: NewUserProfile


class UserExceptionResponse(BaseModel):

    detail: str
    message: str
