"""Service for managing sessions"""

from ..services.survey_service import SurveyService
from ..services.response_service import ResponseService
from ..repositories import SessionRepository
from ..models.sessions import SessionId, Session
from ..core.logging import get_logger

logger = get_logger(__name__)


class SessionService:
    """Service for managing sessions"""

    def __init__(
        self,
        session_repository: SessionRepository,
        survey_service: SurveyService,
        response_service: ResponseService,
    ):
        self.session_repository = session_repository
        self.survey_service = survey_service
        self.response_service = response_service

    async def get_active_session(self, session_id: SessionId) -> Session:
        """Get the active session for a given session ID."""
        session = await self.session_repository.get_active_session(session_id)
        if session is not None:
            return session

        # Validates if survey exists
        survey = await self.survey_service.get_survey(session_id.survey_id)

        session = await self.session_repository.get_unactive_session(session_id)
        if session is not None:
            await self.session_repository.delete_unactive_session(session_id)
        else:
            session = Session(id=session_id)

        session.survey = survey

        if session.response is None:
            # Get response by survey and user, to validate if it exists
            session.response = await self.response_service.get_response_by_survey_and_user(
                session_id.survey_id, session_id.user_id
            )

            # If response does not exist, create it
            if session.response is None:
                session.response = await self.response_service.create_response(
                    session_id.survey_id, session_id.user_id
                )

        elif session.response.id is not None:
            # Faster to look up by id than by survey and user
            session.response = await self.response_service.get_response(session.response.id)

        await self.session_repository.set_active_session(session_id, session)

        return session

    async def is_session_active(self, session_id: SessionId) -> bool:
        """Check if a session is active."""
        return await self.session_repository.get_active_session(session_id) is not None

    async def deactivate_session(self, session_id: SessionId) -> None:
        """Deactivate a session."""
        session = await self.session_repository.get_active_session(session_id)
        if session is not None:
            await self.session_repository.set_unactive_session(session_id, session)
            await self.session_repository.delete_active_session(session_id)

    async def update_session(self, session_id: SessionId, session: Session) -> None:
        """Update a session."""
        await self.session_repository.set_active_session(session_id, session)

    async def delete_session(self, session_id: SessionId) -> None:
        """Delete a session."""
        await self.session_repository.delete_active_session(session_id)
