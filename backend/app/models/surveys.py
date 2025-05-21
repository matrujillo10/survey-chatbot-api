"""Models for surveys"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from .types import QuestionType, ConditionOperator
from ..core.exceptions import BusinessRuleError


class NextQuestionCondition(BaseModel):
    """Model for a next question condition"""

    operator: ConditionOperator
    value: Any
    next_question_id: str


class QuestionOption(BaseModel):
    """Model for a question option"""

    id: str
    text: str
    next_question_id: Optional[str] = None
    conditions: Optional[List[NextQuestionCondition]] = None

    model_config = ConfigDict(
        json_schema_extra={"example": {"id": "opt1", "text": "Yes", "next_question_id": "q2"}}
    )


class Question(BaseModel):
    """Model for a question"""

    id: str
    type: QuestionType
    text: str
    options: Optional[List[QuestionOption]] = []
    default_next_question_id: Optional[str] = None
    conditional_next: Optional[List[NextQuestionCondition]] = []
    is_terminal: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "multiple_choice",
                "text": "Do you use our product regularly?",
                "options": [
                    {"id": "yes", "text": "Yes", "next_question_id": "q2"},
                    {"id": "no", "text": "No", "next_question_id": "q3"},
                ],
                "is_terminal": False,
            }
        }
    )

    def validate_options(self) -> bool:
        """Validate that multiple choice questions have options"""
        if self.type == QuestionType.MULTIPLE_CHOICE:
            if not self.options or len(self.options) == 0:
                raise BusinessRuleError("Multiple choice questions must have options")
        return True

    def validate_next_questions(self, available_questions: set[str]) -> bool:
        """Validate that all referenced next questions exist"""
        if self.default_next_question_id and not self.is_terminal:
            if self.default_next_question_id not in available_questions:
                raise BusinessRuleError(f"Question {self.default_next_question_id} not found")

        if self.options:
            for option in self.options:
                if option.next_question_id and option.next_question_id not in available_questions:
                    raise BusinessRuleError(f"Question {option.next_question_id} not found")
                if option.conditions:
                    for condition in option.conditions:
                        if condition.next_question_id not in available_questions:
                            raise BusinessRuleError(
                                f"Question {condition.next_question_id} not found"
                            )

        if self.conditional_next:
            for condition in self.conditional_next:
                if condition.next_question_id not in available_questions:
                    raise BusinessRuleError(f"Question {condition.next_question_id} not found")

        return True

    def get_validated_response(self, response: str) -> Any:
        """Validate the response against the question conditions"""
        match self.type:
            case QuestionType.MULTIPLE_CHOICE | QuestionType.RATING:
                if response not in [option.id for option in self.options]:
                    raise BusinessRuleError("Invalid option")
                return response
            case QuestionType.BOOLEAN:
                if response not in ["yes", "no"]:
                    raise BusinessRuleError("Boolean response must be 'yes' or 'no'")
                return True
            case QuestionType.DATE:
                try:
                    datetime.strptime(response, "%Y-%m-%d")
                except ValueError as e:
                    raise BusinessRuleError("Invalid date format") from e
                return datetime.strptime(response, "%Y-%m-%d")
            case QuestionType.NUMBER:
                if not response.isdigit() and not response.replace(".", "").isdigit():
                    raise BusinessRuleError("Number must be a valid integer or float")
                return float(response)
            case QuestionType.TEXT:
                return response
            case _:
                raise BusinessRuleError("Invalid question type")

    def get_next_question(self, response: str) -> "Question":
        """Get the next question based on the response"""
        if self.is_terminal:
            return None

        if self.type in [QuestionType.MULTIPLE_CHOICE, QuestionType.RATING, QuestionType.BOOLEAN]:
            for option in self.options:
                if option.id == response:
                    return option.next_question_id
            return None

        if self.conditional_next and len(self.conditional_next) > 0:
            for condition in self.conditional_next:
                if (
                    condition.operator == ConditionOperator.EQUALS
                    and condition.value == self.get_validated_response(response)
                ):
                    return condition.next_question_id
            return None

        return self.default_next_question_id


class Survey(BaseModel):
    """Model for a survey"""

    id: Optional[str] = Field(default=None, alias="_id")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    first_question_id: str
    questions: Dict[str, Question]

    model_config = ConfigDict(populate_by_name=True)

    def get_question(self, question_id: str) -> Question:
        """Get a question by its id"""
        if question_id not in self.questions:
            raise BusinessRuleError(f"Question {question_id} not found")
        return self.questions[question_id]

    def validate_survey_flow(self) -> bool:
        """Validate the survey flow:

        1. All questions exist
        2. No circular references
        3. All question types are valid
        4. Multiple choice questions have options
        """
        if self.first_question_id not in self.questions:
            raise BusinessRuleError("First question not found in questions list")

        question_ids = set(self.questions.keys())

        for _, question in self.questions.items():
            question.validate_options()
            question.validate_next_questions(question_ids)

        # Check for circular references
        visited = set()
        path = set()

        def check_circular(question_id: str):
            if question_id in path:
                raise BusinessRuleError(f"Circular reference detected at question {question_id}")
            if question_id in visited:
                return

            visited.add(question_id)
            path.add(question_id)

            question = self.questions[question_id]
            if question.is_terminal:
                path.remove(question_id)
                return

            # Check all possible next questions
            if question.default_next_question_id:
                check_circular(question.default_next_question_id)

            if question.options:
                for option in question.options:
                    if option.next_question_id:
                        check_circular(option.next_question_id)

            if question.conditional_next:
                for condition in question.conditional_next:
                    check_circular(condition.next_question_id)

            path.remove(question_id)

        check_circular(self.first_question_id)
        return True


class SurveyUpdate(BaseModel):
    """Model for updating an existing survey"""

    title: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[Dict[str, Question]] = None

    def validate_partial_update(self, current_survey: Survey) -> bool:
        """Validate that a partial update maintains survey integrity"""
        if self.questions is not None:
            # Create a merged view of the survey
            merged_questions = {**current_survey.questions, **self.questions}
            temp_survey = Survey(
                title=current_survey.title,
                description=current_survey.description,
                first_question_id=current_survey.first_question_id,
                questions=merged_questions,
            )
            # Validate the merged survey
            return temp_survey.validate_survey_flow()
        return True


class SurveyDB(Survey):
    """Database model for surveys"""

    is_active: bool = True
