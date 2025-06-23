import json
from aiosmtplib.errors import SMTPException
from fastapi import Depends
from faststream.broker.fastapi.context import Context
from faststream.kafka.fastapi import KafkaRouter
from faststream.kafka.message import KafkaMessage
from functools import partial
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    wait_random,
    retry_if_exception_type,
    RetryCallState
)
from typing import Annotated

from email_app.schemas.mail import CurrencyInfoMail, ErrorMailInfo
from email_app.core.config import settings
from email_app.core.dependency import get_mail_service
from email_app.services.mail import MailService


mail_router = KafkaRouter(
    bootstrap_servers=f'{settings.KAFKA.HOST}:{settings.KAFKA.PORT}',
    prefix='/mail'
)
dead_email_publisher = mail_router.broker.publisher('email_error')


@mail_router.subscriber(
    'currency_info',
    group_id='currency',
    auto_commit=False
)
async def handle_currency_info(
        currency_info: CurrencyInfoMail,
        mail_service: Annotated[MailService, Depends(get_mail_service)],
        message: KafkaMessage = Context('message')
):
    async def after_retry_callback(retry_state: RetryCallState, msg: KafkaMessage):
        if retry_state.outcome.failed and retry_state.attempt_number == 3:
            email, info, info_type = json.loads(msg.body).values()
            topic_message = ErrorMailInfo(
                email=email,
                message=info,
                info_type=info_type,
                error=str(retry_state.outcome.exception())
            )
            await dead_email_publisher.publish(topic_message, 'email_error')
            await msg.ack()

    after_retry_callback = partial(after_retry_callback, msg=message)

    @retry(
            stop=stop_after_attempt(3),
            wait=wait_fixed(5) + wait_random(0, 2),
            retry=retry_if_exception_type(SMTPException),
            retry_error_callback = lambda retry_state: None,
            after=after_retry_callback
        )
    async def send_email(info):
        try:
            await mail_service.send_email(info)
            await message.ack()
        except SMTPException:
            raise
        except Exception as exc:
            # logging(exc)
            await message.ack()
    await send_email(currency_info)

