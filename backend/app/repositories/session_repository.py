"""Session repository"""

from typing import Optional, Protocol

from ..models.sessions import SessionId, Session


class SessionRepository(Protocol):
    """Interface for session repository."""

    async def get_active_session(self, session_id: SessionId) -> Optional[Session]:
        """Get an active session by ID."""

    async def get_unactive_session(self, session_id: SessionId) -> Optional[Session]:
        """Get an inactive session by ID."""

    async def delete_unactive_session(self, session_id: SessionId) -> None:
        """Delete an inactive session."""

    async def set_active_session(self, session_id: SessionId, session: Session) -> None:
        """Set a session as active."""

    async def set_unactive_session(self, session_id: SessionId, session: Session) -> None:
        """Set a session as unactive."""

    async def delete_active_session(self, session_id: SessionId) -> None:
        """Delete an active session."""
