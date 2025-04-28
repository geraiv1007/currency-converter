import redis.asyncio as aioredis

from app.core.config import settings


def get_redis_connection():
    redis_conn = aioredis.Redis(
        host=settings.CACHE.HOST,
        port=settings.CACHE.PORT,
        db=settings.CACHE.DB,
        password=settings.CACHE.PASSWORD,
        decode_responses=True
    )
    return redis_conn
