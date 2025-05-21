"""Models for sessions"""

from typing import Optional

from pydantic import BaseModel

from .surveys import Survey
from .responses import SurveyResponse


class SessionId(BaseModel):
    """Session ID model."""

    user_id: str
    survey_id: str

    def __hash__(self) -> int:
        """Hash the session ID by combining the user ID and survey ID."""
        return hash((self.user_id, self.survey_id))


class Session(BaseModel):
    """Session model."""

    id: SessionId
    survey: Optional[Survey] = None
    response: Optional[SurveyResponse] = None
