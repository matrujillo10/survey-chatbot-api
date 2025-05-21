"""Base models for survey responses."""

from typing import Any, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from .types import QuestionType
from ..core.constants import UTC
from ..core.exceptions import BusinessRuleError


class QuestionResponse(BaseModel):
    """Base model for an individual question response."""

    question_id: str
    question_type: QuestionType
    response_value: Any
    next_question_id: Optional[str] = None


class SurveyResponse(BaseModel):
    """Base model for survey responses with common fields."""

    id: Optional[str] = Field(default=None, alias="_id")
    survey_id: str
    user_id: str = None
    current_question_id: Optional[str] = None  # Track progress through survey
    is_complete: bool = False
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None
    last_updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    answers: Optional[List[QuestionResponse]] = None

    model_config = ConfigDict(populate_by_name=True)
