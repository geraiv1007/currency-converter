import jwt
from datetime import datetime, timedelta, timezone
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from typing import Any, Literal
from uuid import uuid4

from currency_app.core.config import settings
from currency_app.exceptions.exceptions import AccessTokenExpiredException, InvalidTokenException


class JWTAuth:

    def __init__(self):
        self.settings = settings.JWT

    def create_jwt_token(self, email: str, token_type: Literal['access', 'refresh'], data=None) -> str:
        current_time = datetime.now(tz=timezone.utc)
        match token_type:
            case 'access':
                delta = timedelta(seconds=self.settings.ACCESS_TOKEN_EXPIRES)
            case 'refresh':
                delta = timedelta(seconds=self.settings.REFRESH_TOKEN_EXPIRES)
            case _:
                raise ValueError('Wrong token type')
        payload = {
            'iss': 'Bomardiro Crocodilo',
            'sub': email,
            'exp': current_time + delta,
            'nbf': current_time,
            'iat': current_time,
            'type': token_type,
            'jti': str(uuid4())
        }
        if data:
            payload.update(data)
        token = jwt.encode(
            payload=payload,
            key=self.settings.SECRET_KEY,
            algorithm=self.settings.ALGORITHM
        )
        return token

    @staticmethod
    def get_token_payload(token) -> dict[str, Any]:
        return jwt.decode(token, options={'verify_signature': False})

    def decode_jwt_token(self, token, verify_exp: bool = True):
        try:
            decoded_token = jwt.decode(
                token,
                self.settings.SECRET_KEY,
                leeway=0,
                algorithms=[self.settings.ALGORITHM],
                options={'verify_exp': verify_exp}
            )
        except ExpiredSignatureError:
            raise AccessTokenExpiredException(message='Please refresh tokens on /refresh_tokens')
        except InvalidTokenError:
            raise InvalidTokenException(message='Error raised while decoding token. Please login again')
        else:
            return decoded_token
