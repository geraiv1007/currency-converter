import json
from datetime import datetime, timedelta
from redis.asyncio import Redis


class CurrencyCache:

    def __init__(self, redis_conn: Redis):
        self.redis_conn = redis_conn

    async def get_available_currencies(self) -> dict[str, str]:
        async with self.redis_conn as red:
            currencies = await red.hgetall('available_currencies')
        return currencies

    async def set_available_currencies(self, currencies):
        async with self.redis_conn as red:
            await red.hset(
                'available_currencies',
                mapping=currencies
            )
            delay = datetime.now() + timedelta(hours=3)
            await red.expireat('available_currencies', delay)

    async def get_exchange_rate(self, from_: str, to_: str, date_: str):
        async with self.redis_conn as red:
            rate = (await red.json().get('rates', f'$.{from_}.{to_}.{date_}'))
        return rate[0] if rate else rate

    async def set_exchange_rate(self, from_: str, to_: str, date_: str, rate: float):
        async with self.redis_conn as red:
            if not await red.json().type('rates', '$'):
                await red.json().set(
                    'rates',
                    f'$',
                    json.loads('{{"{}": {{"{}": {{"{}": {}}}}}}}'.format(from_, to_, date_, rate))
                )
            elif not await red.json().type('rates', f'$.{from_}'):
                await red.json().set(
                    'rates',
                    f'$.{from_}',
                    json.loads('{{"{}": {{"{}": {}}}}}'.format(to_, date_, rate))
                )
            elif not await red.json().type('rates', f'$.{from_}.{to_}'):
                await red.json().set(
                    'rates',
                    f'$.{from_}.{to_}',
                    json.loads('{{"{}": {}}}'.format(date_, rate))
                )
            elif not await red.json().type('rates', f'$.{from_}.{to_}.{date_}'):
                await red.json().set(
                    'rates',
                    f'$.{from_}.{to_}.{date_}', rate
                )
