import jwt
from aiohttp import ClientSession
from jwt import PyJWKClient
from jwt.exceptions import InvalidAudienceError, ExpiredSignatureError, InvalidIssuerError
from yarl import URL

from currency_app.api.schemas.user import GoogleUserCreate
from currency_app.core.config import settings
from currency_app.exceptions.exceptions import InvalidGoogleTokenException


class GoogleClient:

    def __init__(self):
        self.async_session = ClientSession
        self.settings = settings.GOOGLE

    def get_redirect_url(self) -> str:
        url = self.settings.AUTH_URI
        data = {
            'response_type': 'code',
            'client_id': self.settings.CLIENT_ID,
            'redirect_uri': self.settings.REDIRECT_URI,
            'scope': 'openid profile email',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        redirect_url = str(URL(url).with_query(data))
        return redirect_url

    async def get_user_data(self, code: str) -> GoogleUserCreate:
        id_token = await self._get_google_id_token(code)
        user_data = await self._get_data_from_id_token(id_token)
        return user_data

    async def _get_google_id_token(self, code: str) -> str:
        data = {
            "code": code,
            "client_id": self.settings.CLIENT_ID,
            "client_secret": self.settings.CLIENT_SECRET,
            "redirect_uri": self.settings.REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        async with self.async_session() as session:
            response = await session.post(self.settings.TOKEN_URI, data=data)
            id_token = (await response.json())['id_token']
        return id_token

    async def _get_data_from_id_token(self, id_token: str) -> GoogleUserCreate:
        jwk_client = PyJWKClient(self.settings.CERT_URI)
        signing_key = jwk_client.get_signing_key_from_jwt(id_token)
        try:
            payload = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.settings.CLIENT_ID,
                issuer=["https://accounts.google.com", "accounts.google.com"],
            )
        except (InvalidAudienceError, InvalidIssuerError, ExpiredSignatureError):
            raise InvalidGoogleTokenException(
                message='Please try again to authenticate with Google or choose another method'
            )
        else:
            return GoogleUserCreate(
                first_name=payload['given_name'],
                last_name=payload['family_name'],
                email=payload['email']
            )
