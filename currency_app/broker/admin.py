from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from currency_app.core.config import settings


class KafkaAdmin:

    def __init__(self):
        self.bootstrap_servers = f'{settings.KAFKA.HOST}:{settings.KAFKA.PORT}'
        self.client = None

    async def start(self):
        self.client = AIOKafkaAdminClient(
            bootstrap_servers=f'{settings.KAFKA.HOST}:{settings.KAFKA.PORT}'
        )
        await self.client.start()

    async def close(self):
        await self.client.close()

    async def create_topic(self, name: str, partitions: int, replication_factor: int):
        new_topic = NewTopic(
            name=name,
            num_partitions=partitions,
            replication_factor=replication_factor
        )
        await self.client.create_topics(new_topics=[new_topic])

    async def get_topics(self):
        return await self.client.list_topics()
