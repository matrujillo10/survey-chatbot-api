"""Session Redis repository"""

import json
from typing import Optional

from redis.asyncio import Redis

from ..session_repository import SessionRepository
from ...models.sessions import SessionId, Session
from ...core.logging import get_logger

logger = get_logger(__name__)

# Constants for Redis keys
ACTIVE_SESSION_PREFIX = "active_session:"
INACTIVE_SESSION_PREFIX = "inactive_session:"
SESSION_TTL = 3600  # 1 hour in seconds
UNACTIVE_SESSION_TTL = 600  # 10 minute in seconds


class RedisSessionRepository(SessionRepository):
    """Redis implementation of session repository."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def _get_active_key(self, session_id: SessionId) -> str:
        """Get Redis key for active session."""
        return f"{ACTIVE_SESSION_PREFIX}{session_id.user_id}:{session_id.survey_id}"

    def _get_inactive_key(self, session_id: SessionId) -> str:
        """Get Redis key for inactive session."""
        return f"{INACTIVE_SESSION_PREFIX}{session_id.user_id}:{session_id.survey_id}"

    def _serialize_session(self, session: Session) -> str:
        """Serialize session to JSON string."""
        return json.dumps(session.model_dump(mode="json", exclude_none=True))

    def _deserialize_session(self, session_data: str) -> Optional[Session]:
        """Deserialize session from JSON string."""
        try:
            data = json.loads(session_data)
            return Session.model_validate(data)
        except Exception as e:
            logger.error("Failed to deserialize session: %s", str(e), exc_info=True)
            return None

    async def get_active_session(self, session_id: SessionId) -> Optional[Session]:
        """Get an active session by ID."""
        key = self._get_active_key(session_id)
        session_data = await self.redis.get(key)
        if session_data:
            return self._deserialize_session(session_data)
        return None

    async def get_unactive_session(self, session_id: SessionId) -> Optional[Session]:
        """Get an inactive session by ID."""
        key = self._get_inactive_key(session_id)
        session_data = await self.redis.get(key)
        if session_data:
            return self._deserialize_session(session_data)
        return None

    async def delete_unactive_session(self, session_id: SessionId) -> None:
        """Delete an inactive session."""
        key = self._get_inactive_key(session_id)
        await self.redis.delete(key)

    async def set_active_session(self, session_id: SessionId, session: Session) -> None:
        """Set a session as active."""
        key = self._get_active_key(session_id)
        session_data = self._serialize_session(session)
        await self.redis.setex(key, SESSION_TTL, session_data)

    async def delete_active_session(self, session_id: SessionId) -> None:
        """Delete an active session."""
        key = self._get_active_key(session_id)
        await self.redis.delete(key)

    async def set_unactive_session(self, session_id: SessionId, session: Session) -> None:
        """Set a session as unactive."""
        key = self._get_inactive_key(session_id)
        session_data = self._serialize_session(session)
        await self.redis.setex(key, UNACTIVE_SESSION_TTL, session_data)
