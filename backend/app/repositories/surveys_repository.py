"""Surveys repository"""

from typing import List, Optional, Protocol

from ..models.surveys import SurveyDB


class SurveyRepository(Protocol):
    """Interface for survey repository."""

    async def insert(self, survey: SurveyDB) -> SurveyDB:
        """Insert a new survey."""

    async def find_by_id(self, survey_id: str) -> Optional[SurveyDB]:
        """Find a survey by ID."""

    async def find_active(self) -> List[SurveyDB]:
        """Find all active surveys."""

    async def update(self, survey_id: str, update_dict: dict) -> Optional[SurveyDB]:
        """Update a survey."""

    async def soft_delete(self, survey_id: str) -> bool:
        """Soft delete a survey."""
