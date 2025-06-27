from faststream import FastStream
from faststream.kafka import KafkaBroker

from currency_app.core.config import settings


class Broker:

    def __init__(self):
        self.kafka_broker = KafkaBroker(f'{settings.KAFKA.HOST}:{settings.KAFKA.PORT}')
        self.app = FastStream(self.kafka_broker)
        self.publisher = None

    async def connect(self):
        await self.kafka_broker.start()

    async def disconnect(self):
        await self.kafka_broker.close()

    def create_publisher(self, topic_name: str):
        self.publisher = self.kafka_broker.publisher(topic_name)
