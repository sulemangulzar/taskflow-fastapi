import time
from typing import Any

import redis.asyncio as redis

from app.core.config import settings


class InMemoryTokenBlocklist:
    def __init__(self) -> None:
        self._store: dict[str, float | None] = {}

    def _cleanup(self) -> None:
        now = time.time()
        expired_keys = [
            key
            for key, expires_at in self._store.items()
            if expires_at is not None and expires_at <= now
        ]
        for key in expired_keys:
            self._store.pop(key, None)

    async def set(self, name: str, value: Any, ex: int | None = None) -> bool:
        expires_at = time.time() + ex if ex else None
        self._store[name] = expires_at
        return True

    async def exists(self, name: str) -> int:
        self._cleanup()
        return 1 if name in self._store else 0


if settings.REDIS_URL == "memory://":
    token_blocklist = InMemoryTokenBlocklist()
else:
    # decode_responses=True automatically converts bytes to strings.
    # Use REDIS_URL so hosted Redis providers with TLS URLs, such as rediss://, work correctly.
    token_blocklist = redis.from_url(settings.REDIS_URL, decode_responses=True)
