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


class CurrencyService:

    def __init__(
            self,
            currency_client: CurrencyClient
    ):
        self.currency_client = currency_client

    async def get_available_currencies(self) -> dict[str, str]:
        currencies = await self.currency_client.get_currency_list()
        return currencies

    async def exchange_currency(
            self,
            currency_data: CurrencyConvertRequest
    ) -> CurrencyConvertResponse:
        convert_result = await self.currency_client.convert_currency(currency_data)
        return convert_result

    async def get_live_currency_exchange_rate(
            self,
            currency_data: ExchangeRateRequest
    ) -> ExchangeRateResponse:
        exchange_rate = await self.currency_client.get_live_exchange_rate_info(currency_data)
        return exchange_rate

    async def get_hist_currency_exchange_rate(
            self,
            currency_data: ExchangeRateHistRequest
    ) -> ExchangeRateResponse:
        exchange_rate = await self.currency_client.get_hist_exchange_rate_info(currency_data)
        return exchange_rate

    async def get_exchange_rate_dynamics(
            self,
            currency_data: ExchangeRatePeriodAlterRequest
    ) -> ExchangeRatePeriodAlterResponse:
        dynamics_data = await self.currency_client.get_exchange_rate_dynamics(currency_data)
        return dynamics_data

    async def get_daily_currency_exchange_rate(
            self,
            currency_data: ExchangeRatePeriodDailyRequest
    ) -> ExchangeRatePeriodDailyResponse:
        daily_data = await self.currency_client.get_daily_exchange_rate_info(currency_data)
        return daily_data
