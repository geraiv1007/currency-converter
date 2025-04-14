from fastapi import status
from fastapi.exceptions import HTTPException


class UserAlreadyExistsException(HTTPException):

    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail='User already exists')
        self.message = message


class AuthException(HTTPException):

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=getattr(self, 'detail', None),
            headers={"WWW-Authenticate": "Bearer"})
        self.message = message


class UserNotFoundException(AuthException):

    detail='User not found'


class UserPasswordIncorrectException(AuthException):

    detail='Wrong user password'


class AccessTokenExpiredException(AuthException):

    detail='Token expired'


class WrongTokenTypeException(AuthException):

    detail='Wrong token type'


class InvalidTokenException(AuthException):

    detail='Invalid token'


class RevokedTokenException(AuthException):

    detail='Revoked token'


class WrongAuthorizationHeaderException(AuthException):

    detail='Authorization header error'


class InvalidGoogleTokenException(InvalidTokenException):

    pass