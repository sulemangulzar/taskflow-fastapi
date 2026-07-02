import redis.asyncio as redis

from app.core.config import settings

# decode_responses=True automatically converts bytes to strings
token_blocklist = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True
)
