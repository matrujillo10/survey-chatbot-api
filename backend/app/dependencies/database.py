"""Dependencies for database operations"""

from functools import lru_cache

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import get_settings

settings = get_settings()


@lru_cache(maxsize=1)
def get_mongodb_client() -> AsyncMongoClient:
    """Get cached MongoDB client instance."""
    return AsyncMongoClient(settings.MONGODB_URL)


async def get_database() -> AsyncDatabase:
    """Get database connection from cached client."""
    client = get_mongodb_client()
    return client.get_database(settings.MONGODB_DATABASE)
