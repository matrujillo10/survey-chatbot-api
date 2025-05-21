"""Service for handling the chat."""

from .survey_service import SurveyService
from .session_service import SessionService
from .response_service import ResponseService
from ..models.sessions import SessionId
from ..models.surveys import Question
from ..core.logging import get_logger
from ..core.exceptions import BusinessRuleError

logger = get_logger(__name__)


class ChatsService:
    """Service for handling the chat."""

    def __init__(
        self,
        survey_service: SurveyService,
        response_service: ResponseService,
        session_service: SessionService,
    ):
        self.survey_service = survey_service
        self.response_service = response_service
        self.session_service = session_service

    async def connect(self, session_id: SessionId) -> Question:
        """Connect to the chat."""
        if await self.session_service.is_session_active(session_id):
            raise BusinessRuleError("Session already active")
        session = await self.session_service.get_active_session(session_id)
        if session.response and session.response.is_complete:
            raise BusinessRuleError("Survey already completed")
        return session.survey.get_question(session.response.current_question_id)

    async def disconnect(self, session_id: SessionId) -> None:
        """Disconnect from the chat."""
        await self.session_service.deactivate_session(session_id)

    async def handle_message(self, session_id: SessionId, message: str) -> Question:
        """Handle a message from the chat."""
        session = await self.session_service.get_active_session(session_id)
        if not session:
            raise BusinessRuleError("Session not found")

        # Get the current question
        question = session.survey.get_question(session.response.current_question_id)

        # Add the response to the question
        session.response = await self.response_service.add_question_response(
            session.response.id, question, message
        )
        await self.session_service.update_session(session_id, session)

        # Return the next question
        if session.response.current_question_id is not None:
            return session.survey.get_question(session.response.current_question_id)

        # If the survey is complete, delete the session
        await self.session_service.delete_session(session_id)

        return None
