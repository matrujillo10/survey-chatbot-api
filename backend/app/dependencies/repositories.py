"""Dependencies for repositories"""

from typing import Annotated

from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase
from redis.asyncio import Redis

from ..repositories.surveys_repository import SurveyRepository
from ..repositories.responses_repository import ResponseRepository
from ..repositories.session_repository import SessionRepository
from ..repositories.mongodb import MongoDBSurveyRepository, MongoDBResponseRepository
from ..repositories.redis.session_redis_repository import RedisSessionRepository
from .database import get_database
from .redis import get_redis


async def get_survey_repository(
    db: Annotated[AsyncDatabase, Depends(get_database)]
) -> SurveyRepository:
    """Get survey repository instance."""
    return MongoDBSurveyRepository(db)


async def get_response_repository(
    db: Annotated[AsyncDatabase, Depends(get_database)]
) -> ResponseRepository:
    """Get response repository instance."""
    return MongoDBResponseRepository(db)


async def get_session_repository(redis: Annotated[Redis, Depends(get_redis)]) -> SessionRepository:
    """Get session repository instance."""
    return RedisSessionRepository(redis)


SurveyRepositoryDep = Annotated[SurveyRepository, Depends(get_survey_repository)]
ResponseRepositoryDep = Annotated[ResponseRepository, Depends(get_response_repository)]
SessionRepositoryDep = Annotated[SessionRepository, Depends(get_session_repository)]
