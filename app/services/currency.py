from datetime import date

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
from app.client.currency import CurrencyClient
from app.exceptions.exceptions import WrongCurrencyCodeException
from app.repositories.currency_cache import CurrencyCache


class CurrencyService:

    def __init__(
            self,
            currency_client: CurrencyClient,
            currency_cache: CurrencyCache
    ):
        self.currency_client = currency_client
        self.currency_cache = currency_cache

    async def _check_incoming_currencies(self, currencies: set[str]):
        if not (all_currencies := await self.currency_cache.get_available_currencies()):
            all_currencies = set(await self.currency_client.get_currency_list())
            await self.currency_cache.set_available_currencies(all_currencies)
        if not currencies.issubset(all_currencies):
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
        await self.currency_cache.set_exchange_rate(
            from_=exchange_from,
            to_=exchange_to,
            date_=currency_data.date,
            rate=convert_result.exchange_rate
                )
        return convert_result

    async def get_live_currency_exchange_rate(
            self,
            currency_data: ExchangeRateRequest
    ) -> ExchangeRateResponse:
        input_currencies = {
            *currency_data.currencies.split(','),
            currency_data.source
        }
        await self._check_incoming_currencies(input_currencies)

        exchange_rate = await self.currency_client.get_live_exchange_rate_info(currency_data)
        return exchange_rate

    async def get_hist_currency_exchange_rate(
            self,
            currency_data: ExchangeRateHistRequest
    ) -> ExchangeRateResponse:
        input_currencies = {
            *currency_data.currencies.split(','),
            currency_data.source
        }
        await self._check_incoming_currencies(input_currencies)
        exchange_rate = await self.currency_client.get_hist_exchange_rate_info(currency_data)
        return exchange_rate

    async def get_exchange_rate_dynamics(
            self,
            currency_data: ExchangeRatePeriodAlterRequest
    ) -> ExchangeRatePeriodAlterResponse:
        input_currencies = {
            *currency_data.currencies.split(','),
            currency_data.source
        }
        await self._check_incoming_currencies(input_currencies)
        dynamics_data = await self.currency_client.get_exchange_rate_dynamics(currency_data)
        return dynamics_data

    async def get_daily_currency_exchange_rate(
            self,
            currency_data: ExchangeRatePeriodDailyRequest
    ) -> ExchangeRatePeriodDailyResponse:
        input_currencies = {
            *currency_data.currencies.split(','),
            currency_data.source
        }
        await self._check_incoming_currencies(input_currencies)
        daily_data = await self.currency_client.get_daily_exchange_rate_info(currency_data)
        return daily_data
