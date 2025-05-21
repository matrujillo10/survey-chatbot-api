"""Responses repository"""

from typing import List, Optional, Protocol

from ..models.responses import SurveyResponse, QuestionResponse


class ResponseRepository(Protocol):
    """Interface for survey response repository."""

    async def insert(self, response: SurveyResponse) -> SurveyResponse:
        """Insert a new survey response."""

    async def find_by_survey_and_user(self, survey_id: str, user_id: str) -> List[SurveyResponse]:
        """Find all responses for a survey and user."""

    async def add_question_response(
        self,
        response_id: str,
        question_response: QuestionResponse,
        next_question_id: Optional[str] = None,
        is_complete: bool = False,
    ) -> Optional[SurveyResponse]:
        """Add a new question response to a survey response."""

    async def find_by_id(self, response_id: str) -> Optional[SurveyResponse]:
        """Find a survey response by its id."""

    async def find_by_survey(self, survey_id: str) -> List[SurveyResponse]:
        """Find all survey responses for a survey."""
