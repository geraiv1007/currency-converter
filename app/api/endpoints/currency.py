from fastapi import APIRouter, Depends, Query
from typing import Annotated

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
from app.core.dependency import get_currency_service, validate_access_token
from app.services.currency import CurrencyService


currency_router = APIRouter(
    prefix='/currency',
    tags=['currency']
)

@currency_router.get(
    '/list',
    summary='Currency list',
    description='Get a list of available currencies to use in this API',
    responses={
        200: {
            'model': ExchangeRatePeriodAlterResponse,
            'description': 'Exchange rates',
            'content': {
                'application/json': {
                    'example': {
                        'AED': 'United Arab Emirates Dirham',
                        'AFN': 'Afghan Afghani',
                        'ALL': 'Albanian Lek'
                    }
                }
            }
        }
    }
)
async def get_currency_list(
        currency_service: Annotated[CurrencyService, Depends(get_currency_service)]
) -> dict[str, str]:
    currencies = await currency_service.get_available_currencies()
    return currencies


@currency_router.get(
    '/exchange_rate/live',
    summary='Live exchange rates',
    description='Get most actual exchange rate of a source and arbitrary currency',
    responses={
        200: {
            'model': ExchangeRatePeriodAlterResponse,
            'description': 'Exchange rates',
            'content': {
                'application/json': {
                    'example': {
                        'date': '2025-01-01 23:59',
                        'source': 'USD',
                        'exchange_rate': {
                            'EUR': 0.966055,
                            'GBP': 0.798825
                        }
                    }
                }
            }
        }
    },
    #dependencies=[Depends(validate_access_token)]
)
async def get_live_exchange_rate(
        currency_service: Annotated[CurrencyService, Depends(get_currency_service)],
        currency_data: Annotated[ExchangeRateRequest, Query()]
) -> ExchangeRateResponse:
    exchange_rate = await currency_service.get_live_currency_exchange_rate(currency_data)
    return exchange_rate


@currency_router.get(
    '/exchange_rate/hist',
    summary='Historical exchange rates',
    description='Get exchange rate of a source and arbitrary currency on a certain historical date',
    responses={
        200: {
            'model': ExchangeRatePeriodAlterResponse,
            'description': 'Exchange rates',
            'content': {
                'application/json': {
                    'example': {
                        'date': '2025-01-01 23:59',
                        'source': 'USD',
                        'exchange_rate': {
                            'EUR': 0.966055,
                            'GBP': 0.798825
                        }
                    }
                }
            }
        }
    },
    #dependencies=[Depends(validate_access_token)]
)
async def get_hist_exchange_rate(
    currency_service: Annotated[CurrencyService, Depends(get_currency_service)],
    currency_data: Annotated[ExchangeRateHistRequest, Query()]
) -> ExchangeRateResponse:
    exchange_rate = await currency_service.get_hist_currency_exchange_rate(currency_data)
    return exchange_rate


@currency_router.get(
    '/exchange_rate/change',
    summary='Exchange rate dynamics',
    description='Get margin and percentage changes of one or more currencies relative to the source currency',
    responses={
        200: {
            'model': ExchangeRatePeriodAlterResponse,
            'description': 'Exchange rates',
            'content': {
                'application/json': {
                    'example': {
                        "start_date": "2010-01-01",
                        "end_date": "2020-01-01",
                        "source": "USD",
                        "dynamics": {
                            "EUR": {
                                "start_rate": 0.697253,
                                "end_rate": 0.891401,
                                "change": 0.1941,
                                "change_pct": 27.8447
                            }
                        }
                    }
                }
            }
        }
    },
    #dependencies=[Depends(validate_access_token)]
)
async def get_exchange_rate_dynamics(
        currency_service: Annotated[CurrencyService, Depends(get_currency_service)],
        currency_data: Annotated[ExchangeRatePeriodAlterRequest, Query()]
) -> ExchangeRatePeriodAlterResponse:
    dynamics_data = await currency_service.get_exchange_rate_dynamics(currency_data)
    return dynamics_data


@currency_router.get(
    '/exchange_rate/daily',
    summary='Daily historical exchange rates',
    description='Get daily historical exchange rates between two dates with a maximum time frame of 365 days',
    responses={
        200: {
            'model': ExchangeRatePeriodDailyResponse,
            'description': 'Exchange rates',
            'content': {
                'application/json': {
                    'example': {
                        'start_date': '2010-01-01',
                        'end_date': '2010-07-01',
                        'source': 'USD',
                        'data': {
                            '2010-01-01': {
                                'EUR': 0.697253,
                                'GBP': 0.618224
                            },
                            '2010-01-02': {
                                'EUR': 0.696083,
                                'GBP': 0.617865
                            }
                        }
                    }
                }
            }
        }
    },
    #dependencies=[Depends(validate_access_token)]
)
async def get_daily_exchange_rate(
        currency_service: Annotated[CurrencyService, Depends(get_currency_service)],
        currency_data: Annotated[ExchangeRatePeriodDailyRequest, Query()]
) -> ExchangeRatePeriodDailyResponse:
    daily_data = await currency_service.get_daily_currency_exchange_rate(currency_data)
    return daily_data


@currency_router.get(
    '/convert',
    summary='Currency conversion',
    description='Convert arbitrary amount of one currency to another on a certain date',
    responses={
        200: {
            'model': CurrencyConvertResponse,
            'description': 'Conversion result',
            'content': {
                'application/json': {
                    'example': {
                        'from': 'USD',
                        'to': 'RUB',
                        'amount': '100',
                        'date': '2025-01-01',
                        'result': 11372.1575,
                        'exchange_rate': 113.721575
                    }
                }
            }
        }
    },
    #dependencies=[Depends(validate_access_token)]
)
async def convert_currency(
        currency_service: Annotated[CurrencyService, Depends(get_currency_service)],
        currency_data: Annotated[CurrencyConvertRequest, Query()]
) -> CurrencyConvertResponse:
    convert_result = await currency_service.exchange_currency(currency_data)
    return convert_result
