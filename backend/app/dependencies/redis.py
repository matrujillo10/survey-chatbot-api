"""Dependencies for Redis operations"""

from functools import lru_cache

from redis.asyncio import Redis

from ..core.config import get_settings

settings = get_settings()


@lru_cache(maxsize=1)
def get_redis_client() -> Redis:
    """Get cached Redis client instance."""
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_redis() -> Redis:
    """Get Redis connection from cached client."""
    return get_redis_client()
