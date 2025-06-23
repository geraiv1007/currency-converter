import aiosmtplib
import json
import mimetypes
import pandas as pd
from email.message import EmailMessage
from io import BytesIO

from email_app.core.config import settings


class MailClient:

    def __init__(self):
        self.settings = settings.MAIL

    @staticmethod
    def _build_html_content(df: pd.DataFrame) -> str:
        string_table = df.to_string(index=False)
        content = f"""
                <html>
                  <body>
                    <p>Dear User,</p>
                    <p>You have requested exchange rate info:</p>
                    <pre style="font-family: monospace;">{string_table}</pre>
                    <p>Best regards,<br>Currency API</p>
                  </body>
                </html>
                """
        return content

    def _create_email(self, email: str, content: str, attachment: dict) -> EmailMessage:
        message = EmailMessage()
        message["From"] = self.settings.USERNAME
        message["To"] = email
        message["Subject"] = 'Currency Converter info request'
        message.set_content("Your email client does not support HTML messages.")
        message.add_alternative(content, subtype="html")
        message.add_attachment(
            attachment['data'],
            maintype=attachment['maintype'],
            subtype=attachment['subtype'],
            filename='currency_info.csv'
        )
        return message

    def _generate_attachment(self, df: pd.DataFrame) -> dict:
        attachment = BytesIO()
        df.to_csv(attachment, index=False)
        maintype, subtype = mimetypes.types_map['.csv'].split('/')
        bytes_data = attachment.getvalue()
        return {
            'data': bytes_data,
            'maintype': maintype,
            'subtype': subtype
        }

    async def send_email(self, email: str, info_table: str):

        df = pd.DataFrame(json.loads(info_table))
        html_content = self._build_html_content(df)
        attachment = self._generate_attachment(df)
        email_message = self._create_email(email, html_content, attachment)

        await aiosmtplib.send(
            email_message,
            hostname=self.settings.HOSTNAME,
            port=self.settings.PORT,
            username=self.settings.USERNAME,
            password=self.settings.PASSWORD,
            use_tls=True
        )
