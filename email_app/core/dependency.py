from email_app.client.mail import MailClient
from email_app.services.mail import MailService

from fastapi import Depends
from typing import Annotated


def get_mail_client(mail_client: Annotated[MailClient, Depends()]):
    return mail_client

def get_mail_service(mail_client: Annotated[MailClient, Depends(get_mail_client)]):
    return MailService(mail_client)