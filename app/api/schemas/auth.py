from pydantic import BaseModel, Field


class UserCreds(BaseModel):

    username: str
    password: str


class AuthTokens(BaseModel):

    access_token: str
    refresh_token: str
    token_type: str = Field(default='bearer')
