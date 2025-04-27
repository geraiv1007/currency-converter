import redis.asyncio as aioredis

from app.core.config import CacheSettings


def get_redis_connection():
    settings = CacheSettings()
    redis_conn = aioredis.Redis(
        host=settings.HOST,
        port=settings.PORT,
        db=settings.DB,
        password=settings.PASSWORD,
        decode_responses=True
    )
    return redis_conn
