"""Models for types"""

from enum import Enum


class QuestionType(str, Enum):
    """Model for a question type"""

    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    RATING = "rating"


class ConditionOperator(str, Enum):
    """Model for a condition operator"""

    EQUALS = "equals"
