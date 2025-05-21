"""Service for managing surveys."""

from typing import List

from ..repositories.surveys_repository import SurveyRepository
from ..models.surveys import Survey, SurveyUpdate, SurveyDB
from ..core.exceptions import (
    RepositoryError,
    InvalidSurveyIdError,
    ResourceNotFoundError,
    BusinessRuleError,
    ServiceError,
)
from ..core.logging import get_logger

logger = get_logger(__name__)


class SurveyService:
    """Service for managing surveys."""

    def __init__(self, repository: SurveyRepository):
        self.repository = repository

    async def create_survey(self, survey: Survey) -> Survey:
        """Create a new survey."""
        try:
            logger.info("Creating new survey: %s", survey.title)
            survey_db = SurveyDB(**survey.model_dump())
            created = await self.repository.insert(survey_db)
            return Survey.model_validate(created)
        except RepositoryError as e:
            logger.error("Failed to create survey: %s", e.message, exc_info=True)
            raise ServiceError("Failed to create survey") from e

    async def get_survey(self, survey_id: str) -> Survey:
        """Get a survey by ID."""
        try:
            survey = await self.repository.find_by_id(survey_id)
            if not survey:
                msg = f"Survey not found: {survey_id}"
                logger.debug(msg)
                raise ResourceNotFoundError(msg)
            return Survey.model_validate(survey)
        except InvalidSurveyIdError as e:
            logger.warning("Invalid survey ID: %s", e.message)
            raise BusinessRuleError(e.message) from e
        except RepositoryError as e:
            logger.error("Failed to get survey: %s", e.message, exc_info=True)
            raise ServiceError("Failed to get survey") from e

    async def list_surveys(self) -> List[Survey]:
        """List all surveys."""
        try:
            surveys = await self.repository.find_active()
            logger.debug("Retrieved %d active surveys", len(surveys))
            return [Survey.model_validate(survey) for survey in surveys]
        except RepositoryError as e:
            logger.error("Failed to list surveys: %s", e.message, exc_info=True)
            raise ServiceError("Failed to list surveys") from e

    async def update_survey(self, survey_id: str, survey: SurveyUpdate) -> Survey:
        """Update a survey."""
        try:
            logger.info("Updating survey: %s", survey_id)

            # Get current survey to validate update
            current = await self.repository.find_by_id(survey_id)
            if not current:
                msg = f"Survey not found: {survey_id}"
                logger.debug(msg)
                raise ResourceNotFoundError(msg)

            # Validate the update maintains survey integrity
            if not survey.validate_partial_update(current):
                msg = "Update would break survey flow integrity"
                logger.warning("Survey integrity error: %s", msg)
                raise BusinessRuleError(msg)

            # Prepare and perform update
            update_dict = survey.model_dump(exclude_unset=True)
            updated = await self.repository.update(survey_id, update_dict)
            if not updated:
                msg = f"Survey not found: {survey_id}"
                logger.debug(msg)
                raise ResourceNotFoundError(msg)

            return Survey.model_validate(updated)

        except InvalidSurveyIdError as e:
            logger.warning("Invalid survey ID: %s", e.message)
            raise BusinessRuleError(e.message) from e
        except RepositoryError as e:
            logger.error("Failed to update survey: %s", e.message, exc_info=True)
            raise ServiceError("Failed to update survey") from e

    async def delete_survey(self, survey_id: str) -> None:
        """Delete a survey."""
        try:
            logger.info("Deleting survey: %s", survey_id)
            deleted = await self.repository.soft_delete(survey_id)
            if not deleted:
                msg = f"Survey not found: {survey_id}"
                logger.debug(msg)
                raise ResourceNotFoundError(msg)
            logger.info("Successfully deleted survey: %s", survey_id)
        except InvalidSurveyIdError as e:
            logger.warning("Invalid survey ID: %s", e.message)
            raise BusinessRuleError(e.message) from e
        except RepositoryError as e:
            logger.error("Failed to delete survey: %s", e.message, exc_info=True)
            raise ServiceError("Failed to delete survey") from e
