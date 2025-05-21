"""Common test fixtures."""

from unittest.mock import AsyncMock
import pytest

from app.models.responses import SurveyResponse
from app.models.surveys import Question, Survey
from app.models.types import QuestionType
from app.models.sessions import SessionId


@pytest.fixture
def response_repository():
    """Mock response repository."""
    return AsyncMock()


@pytest.fixture
def survey_repository():
    """Mock survey repository."""
    return AsyncMock()


@pytest.fixture
def mock_question():
    """Mock question."""
    return Question(
        id="q1",
        text="What is your name?",
        type=QuestionType.TEXT,
        is_terminal=False,
        default_next_question_id="q2"
    )


@pytest.fixture
def mock_next_question():
    """Mock next question."""
    return Question(
        id="q2",
        text="How old are you?",
        type=QuestionType.NUMBER,
        is_terminal=False,
        default_next_question_id="q3"
    )


@pytest.fixture
def mock_survey(mock_question, mock_next_question):
    """Mock survey."""
    return Survey(
        id="survey123",
        title="Test Survey",
        description="A test survey",
        first_question_id="q1",
        questions={
            mock_question.id: mock_question,
            mock_next_question.id: mock_next_question
        }
    )


@pytest.fixture
def mock_survey_response():
    """Mock survey response."""
    return SurveyResponse(
        id="response123",
        survey_id="survey123",
        user_id="user123",
        current_question_id="q1",
        responses={}
    )


@pytest.fixture
def session_id():
    """Mock session ID."""
    return SessionId(user_id="user123", survey_id="survey123") 