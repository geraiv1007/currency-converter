from datetime import date
from typing import Literal

from faststream.kafka.publisher.asyncapi import AsyncAPIDefaultPublisher
from pydantic import EmailStr, BaseModel

from currency_app.api.schemas.currency import (
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
from currency_app.api.schemas.mail import CurrencyInfoMail
from currency_app.client.currency import CurrencyClient
from currency_app.exceptions.exceptions import WrongCurrencyCodeException
from currency_app.repositories.currency_cache import CurrencyCache


class CurrencyService:

    def __init__(
            self,
            currency_client: CurrencyClient,
            currency_cache: CurrencyCache,
            currency_publisher: AsyncAPIDefaultPublisher
    ):
        self.currency_client = currency_client
        self.currency_cache = currency_cache
        self.currency_publisher = currency_publisher

    async def _check_incoming_currencies(self, currencies: set[str]):
        if not (all_currencies := await self.currency_cache.get_available_currencies()):
            all_currencies = await self.currency_client.get_currency_list()
            await self.currency_cache.set_available_currencies(all_currencies)
        if not currencies.issubset(set(all_currencies)):
            raise WrongCurrencyCodeException

    async def get_available_currencies(self) -> dict[str, str]:
        if currencies := await self.currency_cache.get_available_currencies():
            return currencies
        currencies = await self.currency_client.get_currency_list()
        await self.currency_cache.set_available_currencies(currencies)
        return currencies

    async def exchange_currency(
            self,
            currency_data: CurrencyConvertRequest
    ) -> CurrencyConvertResponse:
        exchange_from = currency_data.exchange_from
        exchange_to = currency_data.exchange_to
        await self._check_incoming_currencies({exchange_from, exchange_to})

        if date.today().isoformat() != currency_data.date:
            if rate := await self.currency_cache.get_exchange_rate(
                from_=exchange_from,
                to_=exchange_to,
                date_=currency_data.date
            ):
                date_ = currency_data.date
                result = round(float(currency_data.amount) * rate, 4)
                convert_result = CurrencyConvertResponse(
                    exchange_from=exchange_from,
                    exchange_to=exchange_to,
                    amount=currency_data.amount,
                    date=date_,
                    result=result,
                    exchange_rate=rate
                )
                return convert_result
        convert_result = await self.currency_client.convert_currency(currency_data)
        if date.today().isoformat() != currency_data.date:
            await self.currency_cache.set_exchange_rate(
                from_=exchange_from,
                to_=exchange_to,
                date_=currency_data.date,
                rate=convert_result.exchange_rate
                    )
        return convert_result

    async def get_live_currency_exchange_rate(
            self,
            currency_data: ExchangeRateRequest,
            email: EmailStr
    ) -> ExchangeRateResponse:
        input_currencies = {
            *currency_data.currencies.split(','),
            currency_data.source
        }
        await self._check_incoming_currencies(input_currencies)
        currency_info = await self.currency_client.get_live_exchange_rate_info(currency_data)
        if currency_data.send_email:
            await self._publish_currency_info(currency_info, 'live', email)
        return currency_info

    async def get_hist_currency_exchange_rate(
            self,
            currency_data: ExchangeRateHistRequest,
            email: EmailStr
    ) -> ExchangeRateResponse:
        input_currencies = {
            *currency_data.currencies.split(','),
            currency_data.source
        }
        await self._check_incoming_currencies(input_currencies)
        currency_info = await self.currency_client.get_hist_exchange_rate_info(currency_data)
        if currency_data.send_email:
            await self._publish_currency_info(currency_info, 'hist', email)
        return currency_info

    async def get_exchange_rate_dynamics(
            self,
            currency_data: ExchangeRatePeriodAlterRequest,
            email: EmailStr
    ) -> ExchangeRatePeriodAlterResponse:
        input_currencies = {
            *currency_data.currencies.split(','),
            currency_data.source
        }
        await self._check_incoming_currencies(input_currencies)
        currency_info = await self.currency_client.get_exchange_rate_dynamics(currency_data)
        if currency_data.send_email:
            await self._publish_currency_info(currency_info, 'change', email)
        return currency_info

    async def get_daily_currency_exchange_rate(
            self,
            currency_data: ExchangeRatePeriodDailyRequest,
            email: EmailStr
    ) -> ExchangeRatePeriodDailyResponse:
        input_currencies = {
            *currency_data.currencies.split(','),
            currency_data.source
        }
        await self._check_incoming_currencies(input_currencies)
        currency_info = await self.currency_client.get_daily_exchange_rate_info(currency_data)
        if currency_data.send_email:
            await self._publish_currency_info(currency_info, 'daily', email)
        return currency_info

    async def _publish_currency_info(
            self,
            info: BaseModel,
            info_type: Literal['live','hist','change','daily'],
            email: EmailStr
    ):
        currency_info = CurrencyInfoMail(
            email=email,
            message=info.model_dump_json(),
            info_type=info_type
        )
        await self.currency_publisher.publish(currency_info, 'currency_info')
