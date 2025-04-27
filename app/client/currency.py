from aiohttp import ClientSession
from datetime import datetime, timezone
from urllib.parse import urljoin

from app.api.schemas.currency import (
    CurrencyConvertRequest,
    CurrencyConvertResponse,
    ExchangeRateHistRequest,
    ExchangeRatePeriodAlterRequest,
    ExchangeRatePeriodAlterResponse,
    ExchangeRatePeriodDailyRequest,
    ExchangeRatePeriodDailyResponse,
    ExchangeRateRequest,
    ExchangeRateResponse
)
from app.core.config import CurrencyApiSetting
from app.exceptions.exceptions import CurrencyConversionException, ExchangeRateInfoException


class CurrencyClient:

    def __init__(self):
        self.async_session = ClientSession
        self.settings = CurrencyApiSetting()
        self.header = {'apikey': self.settings.API_KEY}

    async def _currency_api_request(self, endpoint: str, params: dict = None) -> dict:
        params = {} if params is None else params
        async with self.async_session() as session:
            url = urljoin(self.settings.API_URL, endpoint)
            response = await session.get(
                url,
                params=params,
                headers={'apikey': self.settings.API_KEY}
            )
            data = await response.json()
        return data

    async def get_currency_list(self) -> dict[str, str]:
        print('дергаем валюты через API')
        data = await self._currency_api_request('list')
        currencies = data.get('currencies')
        return currencies

    async def convert_currency(
            self,
            currency_data: CurrencyConvertRequest
    ) -> CurrencyConvertResponse:
        data = await self._currency_api_request('convert', params=currency_data.model_dump(by_alias=True))
        if not data.get('success'):
            raise CurrencyConversionException
        convert_result = {
            'exchange_from': data['query']['from'],
            'exchange_to': data['query']['to'],
            'amount': str(data['query']['amount']),
            'date': data['date'],
            'result': data['result'],
            'exchange_rate': data['info']['quote']
        }
        return CurrencyConvertResponse.model_validate(convert_result)

    async def _get_exchange_rate_info(
            self,
            currency_data: ExchangeRateRequest | ExchangeRateHistRequest,
            *,
            live=True
    ) -> ExchangeRateResponse:
        endpoint = 'live' if live else 'historical'
        data = await self._currency_api_request(endpoint, params=currency_data.model_dump())
        if not data.get('success'):
            raise ExchangeRateInfoException
        new_data = {}
        for key, value in data['quotes'].items():
            currency = key.split(data['source'])[1]
            new_data[currency] = value
        data['exchange_rate'] = new_data
        del data['quotes']
        data['date'] = datetime.fromtimestamp(data.pop('timestamp'), timezone.utc).strftime('%Y-%m-%d %H:%M')
        return ExchangeRateResponse.model_validate(data)

    async def get_live_exchange_rate_info(
            self,
            currency_data: ExchangeRateRequest
    ) -> ExchangeRateResponse:
        return await self._get_exchange_rate_info(currency_data, live=True)

    async def get_hist_exchange_rate_info(
            self,
            currency_data: ExchangeRateHistRequest
    ) -> ExchangeRateResponse:
        return await self._get_exchange_rate_info(currency_data, live=False)

    async def get_daily_exchange_rate_info(
            self,
            currency_data: ExchangeRatePeriodDailyRequest
    ) -> ExchangeRatePeriodDailyResponse:
        data = await self._currency_api_request('timeframe', params=currency_data.model_dump())
        if not data.get('success'):
            raise ExchangeRateInfoException
        new_data = {}
        for date_, info in data['quotes'].items():
            updated = {}
            for currency, rate in info.items():
                currency = currency.split(data['source'])[1]
                updated[currency] = rate
            new_data[date_] = updated
        data['data'] = new_data
        del data['quotes']
        return ExchangeRatePeriodDailyResponse.model_validate(data)

    async def get_exchange_rate_dynamics(
            self,
            currency_data: ExchangeRatePeriodAlterRequest
    ) -> ExchangeRatePeriodAlterResponse:
        data = await self._currency_api_request('change', params=currency_data.model_dump())
        if not data.get('success'):
            raise ExchangeRateInfoException
        new_data = {}
        for key, value in data['quotes'].items():
            currency = key.split(data['source'])[1]
            new_data[currency] = value
        data['dynamics'] = new_data
        del data['quotes']
        return ExchangeRatePeriodAlterResponse.model_validate(data)
