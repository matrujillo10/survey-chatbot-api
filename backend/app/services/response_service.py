"""Service for managing survey responses."""

from typing import List, Optional

from ..repositories.responses_repository import ResponseRepository
from ..repositories.surveys_repository import SurveyRepository
from ..models.responses import SurveyResponse, QuestionResponse
from ..models.surveys import Question
from ..core.exceptions import ResourceNotFoundError, ServiceError
from ..core.logging import get_logger


logger = get_logger(__name__)


class ResponseService:
    """Service for managing survey responses."""

    def __init__(
        self, response_repository: ResponseRepository, survey_repository: SurveyRepository
    ):
        self.response_repository = response_repository
        self.survey_repository = survey_repository

    async def create_response(self, survey_id: str, user_id: str) -> SurveyResponse:
        """Create a new survey response."""
        try:
            # Verify survey exists
            survey = await self.survey_repository.find_by_id(survey_id)
            if not survey:
                raise ResourceNotFoundError(f"Survey {survey_id} not found")

            # Create response
            response_db = SurveyResponse(
                survey_id=survey.id,
                user_id=user_id,
                responses={},
                current_question_id=survey.first_question_id,
            )

            created = await self.response_repository.insert(response_db)
            logger.info("Created survey response: %s", str(created.id))
            return created

        except Exception as e:
            logger.error("Failed to create survey response: %s", str(e), exc_info=True)
            raise ServiceError("Failed to create survey response") from e

    async def add_question_response(
        self, response_id: str, question: Question, response: str
    ) -> QuestionResponse:
        """Add a response to a question in an existing survey response."""
        validated_response = question.get_validated_response(response)
        question_response = QuestionResponse(
            question_id=question.id, question_type=question.type, response_value=validated_response
        )
        next_question_id = question.get_next_question(response)
        logger.info(
            "Current question id: %s, and Next question id: %s", question.id, next_question_id
        )
        question_response.next_question_id = next_question_id

        try:
            # Add response
            updated = await self.response_repository.add_question_response(
                response_id,
                question_response,
                next_question_id=next_question_id,
                is_complete=next_question_id is None,
            )

            if not updated:
                raise ServiceError(f"Failed to update response {response_id}")

            logger.info(
                "Added question response: %s to %s", question_response.question_id, response_id
            )
            logger.info("Updated: %s", updated)
            return updated

        except Exception as e:
            logger.error(
                "Failed to add question response to %s: %s", response_id, str(e), exc_info=True
            )
            raise ServiceError(f"Failed to add question response to {response_id}") from e

    async def get_survey_responses(self, survey_id: str) -> List[SurveyResponse]:
        """Get all responses for a survey."""
        try:
            # Verify survey exists
            survey = await self.survey_repository.find_by_id(survey_id)
            if not survey:
                raise ResourceNotFoundError(f"Survey {survey_id} not found")

            responses = await self.response_repository.find_by_survey(survey_id)
            logger.debug("Retrieved %d responses for survey %s", len(responses), survey_id)
            return responses

        except Exception as e:
            logger.error(
                "Failed to get responses for survey %s: %s", survey_id, str(e), exc_info=True
            )
            raise ServiceError(f"Failed to get responses for survey {survey_id}") from e

    async def get_response(self, response_id: str) -> Optional[SurveyResponse]:
        """Get a specific survey response."""
        try:
            response = await self.response_repository.find_by_id(response_id)
            if not response:
                raise ResourceNotFoundError(f"Survey response {response_id} not found")
            return response

        except Exception as e:
            logger.error("Failed to get response %s: %s", response_id, str(e), exc_info=True)
            raise ServiceError(f"Failed to get response {response_id}") from e

    async def get_response_by_survey_and_user(
        self, survey_id: str, user_id: str
    ) -> Optional[SurveyResponse]:
        """Get a response by survey and user."""
        try:
            response = await self.response_repository.find_by_survey_and_user(survey_id, user_id)
            if len(response) > 0:
                return response[0]
            return None
        except Exception as e:
            logger.error("Failed to get response by survey and user: %s", str(e), exc_info=True)
            raise ServiceError(
                f"Failed to get response by survey and user {survey_id} and {user_id}"
            ) from e
