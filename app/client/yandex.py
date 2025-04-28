from aiohttp import ClientSession
from yarl import URL

from app.api.schemas.user import YandexUserCreate
from app.core.config import settings


class YandexClient:

    def __init__(self):
        self.async_session = ClientSession
        self.settings = settings.YANDEX


    def get_redirect_url(self) -> str:
        url = self.settings.AUTH_URI
        data = {
            'response_type': 'code',
            'client_id': self.settings.CLIENT_ID,
            'redirect_uri': self.settings.REDIRECT_URI,
            'force_confirm': 'true'
        }
        redirect_url = str(URL(url).with_query(data))
        return redirect_url


    async def get_user_data(self, code: str) -> YandexUserCreate:
        access_token = await self._get_yandex_access_token(code)
        user_data = await self._get_data_with_access_token(access_token)
        return user_data


    async def _get_yandex_access_token(self, code: str) -> str:
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.settings.CLIENT_ID,
            'client_secret': self.settings.CLIENT_SECRET
        }
        async with self.async_session() as session:
            response = await session.post(self.settings.TOKEN_URI, data=data)
        access_token = (await response.json())['access_token']
        return access_token


    async def _get_data_with_access_token(self, access_token: str) -> YandexUserCreate:
        async with self.async_session() as session:
            resp = await session.get(
                self.settings.USER_INFO_URI,
                headers={'Authorization': f'OAuth {access_token}'},
                data={'format': 'json'}
            )
        user_data = await resp.json()
        return YandexUserCreate(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['default_email']
        )