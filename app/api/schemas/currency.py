from datetime import date
from dateutil.parser import isoparse
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Any
import re


class IsoDateCheckMixin:

    @field_validator('date', mode='after')
    @classmethod
    def is_isodate(cls, value: Any):
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise ValueError
            isoparse(value)
        except ValueError as exc:
            exc.args = ('Incorrect input for date',)
            raise
        return value


class CurrencyConvertRequest(BaseModel, IsoDateCheckMixin):

    exchange_from: str = Field(
        serialization_alias='from',
        json_schema_extra={'example': 'USD'},
        description='Currency code to convert from'
    )
    exchange_to: str = Field(
        serialization_alias='to',
        json_schema_extra={'example': 'RUB'},
        description='Currency code to convert to'
    )
    amount: str = Field(
        default='1',
        json_schema_extra={'example': '100'},
        description='Amount of currency to convert (must be greater than zero)'
    )
    date: str = Field(
        default_factory=lambda: date.today().isoformat(),
        json_schema_extra={'example': '2025-01-01'},
        description='Date of the exchange rate to be applied (must be iso format)'
    )


    @field_validator('amount', mode='before')
    @classmethod
    def check_amount(cls, value):
        if not re.fullmatch(r'\d+(\.\d{1,2})?', str(value)):
            raise ValueError('Amount must be an integer')
        if not float(value) > 0:
            raise ValueError('Amount must be greater than 0')
        return value


class CurrencyConvertResponse(CurrencyConvertRequest):

    model_config = {'extra': 'ignore'}

    result: float
    exchange_rate: float


class ExchangeRateRequest(BaseModel):

    currencies: str = Field(
        description='Comma separated currency three letter codes (no spaces)',
        pattern='^[A-Z]{3}(,[A-Z]{3})*$',
        json_schema_extra={'example': 'EUR,GBP'}
    )
    source: str = Field(
        description='Source currency to convert',
        pattern='^[A-Z]{3}$',
        json_schema_extra={'example': 'USD'}
    )


class ExchangeRateHistRequest(ExchangeRateRequest, IsoDateCheckMixin):

    date: str = Field(
        description='Date of the exchange rate to be applied (must be iso format)',
        json_schema_extra={'example': '2025-01-01'}
    )


class ExchangeRateResponse(BaseModel):

    model_config = {'extra': 'ignore'}

    date: str
    source: str
    exchange_rate: dict[str, float]


class ExchangeRatePeriodAlterRequest(ExchangeRateRequest):

    start_date: str = Field(
        description='Start date of the exchange rate dynamics period (must be iso format)',
        json_schema_extra = {'example': '2020-01-01'}
    )
    end_date: str = Field(
        description='End date of the exchange rate dynamics period (must be iso format)',
        json_schema_extra={'example': '2020-07-01'}
    )

    @model_validator(mode='after')
    def check_period_dates(self):
        try:
            if not (
                    re.fullmatch(r'\d{4}-\d{2}-\d{2}', self.start_date) and
                    re.fullmatch(r'\d{4}-\d{2}-\d{2}', self.start_date)
            ):
                raise ValueError
            if isoparse(self.start_date) > isoparse(self.end_date):
                raise ValueError
        except ValueError as exc:
            exc.args = ('Incorrect input for date',)
            raise
        return self


class ExchangeRatePeriodDailyRequest(ExchangeRatePeriodAlterRequest):

    pass


class ExchangeRatePeriodResponse(BaseModel):

    model_config = {'extra': 'ignore'}

    start_date: str
    end_date: str
    source: str


class ExchangeRatePeriodAlterResponse(ExchangeRatePeriodResponse):

    dynamics: dict[str, dict[str, float]]


class ExchangeRatePeriodDailyResponse(ExchangeRatePeriodResponse):

    data: dict[str, dict[str, float]]
