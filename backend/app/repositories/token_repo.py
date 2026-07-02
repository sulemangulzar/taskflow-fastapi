import time

from app.db.redis import token_blocklist


async def add_jti_to_blocklist(jti: str, exp: int) -> None:
    ttl = exp - int(time.time())
    if ttl > 0:
        await token_blocklist.set(name=jti, value="1", ex=ttl)


async def token_in_blocklist(jti: str) -> bool:
    return await token_blocklist.exists(jti) > 0
