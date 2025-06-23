import json
import pandas as pd

from email_app.client.mail import MailClient
from email_app.schemas.mail import CurrencyInfoMail


class MailService:

    def __init__(self, client: MailClient):
        self.client = client

    async def send_email(self, info: CurrencyInfoMail):
        email, message, type_ = info.model_dump().values()
        match type_:
            case 'live' | 'hist':
                message = self._rate_info_email_prep(message)
            case 'change':
                message = self._change_info_email_prep(message)
            case 'daily':
                message = self._daily_info_email_prep(message)
        await self.client.send_email(email, message)

    @staticmethod
    def _change_info_email_prep(message) -> str:
        df = pd.DataFrame(json.loads(message))
        left = df.loc[:,:'source']
        right = pd.DataFrame.from_records(df['dynamics'].values, index=df['dynamics'].index)
        currency_info = pd.concat([left, right], axis=1)
        currency_info.index.name = 'currency'
        currency_info = currency_info.reset_index()
        result_table = currency_info.to_json()
        return result_table

    @staticmethod
    def _rate_info_email_prep(message) -> str:
        currency_info = pd.DataFrame(json.loads(message))
        currency_info.index.name = 'currency'
        currency_info = currency_info.reset_index()
        currency_info['date'] = pd.to_datetime(currency_info['date']).dt.strftime('%Y-%m-%d')
        result_table = currency_info.to_json()
        return result_table

    @staticmethod
    def _daily_info_email_prep(message) -> str:
        df = pd.DataFrame(json.loads(message))
        left = df.loc[:, 'source']
        right = pd.DataFrame.from_records(df['data'].values, index=df['data'].index)
        currency_info = pd.concat([left, right], axis=1)
        currency_info.index.name = 'date'
        currency_info = currency_info.reset_index()
        result_table = currency_info.to_json()
        return result_table
