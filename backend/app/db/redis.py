import redis.asyncio as redis

from app.core.config import settings

# decode_responses=True automatically converts bytes to strings.
# Use REDIS_URL so hosted Redis providers with TLS URLs, such as rediss://, work correctly.
token_blocklist = redis.from_url(settings.REDIS_URL, decode_responses=True)
