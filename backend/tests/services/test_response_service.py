"""Tests for ResponseService"""

import pytest

from app.services.response_service import ResponseService
from app.models.responses import SurveyResponse
from app.models.types import QuestionType
from app.core.exceptions import ServiceError, BusinessRuleError
from tests.utils.mock_fixtures import (
    response_repository,
    survey_repository,
    mock_question,
    mock_survey_response
)


@pytest.fixture
def response_service(response_repository, survey_repository):
    """Create a response service."""
    return ResponseService(response_repository, survey_repository)


async def test_add_question_response_success(
    response_service,
    response_repository,
    mock_question,
    mock_survey_response
):
    """Test successful question response addition."""
    # Setup
    response_text = "John Doe"
    expected_next_question_id = "q2"
    
    response_repository.add_question_response.return_value = SurveyResponse(
        id="response123",
        survey_id="survey123",
        user_id="user123",
        current_question_id=expected_next_question_id,
        responses={"q1": response_text}
    )

    # Execute
    result = await response_service.add_question_response(
        mock_survey_response.id,
        mock_question,
        response_text
    )

    # Assert
    assert result.current_question_id == expected_next_question_id
    response_repository.add_question_response.assert_called_once()
    call_args = response_repository.add_question_response.call_args[0]  # Get positional args
    assert call_args[0] == mock_survey_response.id  # First arg is response_id
    kwargs = response_repository.add_question_response.call_args[1]  # Get keyword args
    assert kwargs["next_question_id"] == expected_next_question_id
    assert kwargs["is_complete"] is False


async def test_add_question_response_terminal_question(
    response_service,
    response_repository,
    mock_question
):
    """Test adding response to terminal question."""
    # Setup
    mock_question.is_terminal = True
    response_text = "John Doe"
    
    response_repository.add_question_response.return_value = SurveyResponse(
        id="response123",
        survey_id="survey123",
        user_id="user123",
        current_question_id=None,  # Terminal question
        responses={"q1": response_text},
        is_complete=True
    )

    # Execute
    result = await response_service.add_question_response(
        "response123",
        mock_question,
        response_text
    )

    # Assert
    assert result.current_question_id is None
    assert result.is_complete is True
    response_repository.add_question_response.assert_called_once()
    call_args = response_repository.add_question_response.call_args[1]
    assert call_args["next_question_id"] is None
    assert call_args["is_complete"] is True


async def test_add_question_response_invalid_input(
    response_service,
    mock_question
):
    """Test handling of invalid input."""
    # Setup
    mock_question.type = QuestionType.NUMBER
    invalid_response = "not a number"

    # Execute and Assert
    with pytest.raises(BusinessRuleError):
        await response_service.add_question_response(
            "response123",
            mock_question,
            invalid_response
        )


async def test_add_question_response_repository_error(
    response_service,
    response_repository,
    mock_question
):
    """Test handling of repository errors."""
    # Setup
    response_repository.add_question_response.return_value = None  # Simulating repository failure

    # Execute and Assert
    with pytest.raises(ServiceError, match="Failed to add question response"):
        await response_service.add_question_response(
            "response123",
            mock_question,
            "John Doe"
        )