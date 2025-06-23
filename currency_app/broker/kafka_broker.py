from faststream import FastStream
from faststream.kafka import KafkaBroker

from currency_app.core.config import settings


broker = KafkaBroker(f'{settings.KAFKA.HOST}:{settings.KAFKA.PORT}')
app = FastStream(broker)
currency_publisher = broker.publisher('currency_info')