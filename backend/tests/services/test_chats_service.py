"""Tests for ChatsService"""

from unittest.mock import AsyncMock
import pytest

from app.services.chats_service import ChatsService
from app.models.sessions import Session
from app.models.responses import SurveyResponse
from app.core.exceptions import BusinessRuleError
from tests.utils.mock_fixtures import (
    response_repository,
    survey_repository,
    mock_question,
    mock_next_question,
    mock_survey,
    mock_survey_response,
    session_id
)


@pytest.fixture
def session_service():
    """Mock session service."""
    return AsyncMock()


@pytest.fixture
def response_service():
    """Mock response service."""
    return AsyncMock()


@pytest.fixture
def survey_service():
    """Mock survey service."""
    return AsyncMock()


@pytest.fixture
def chats_service(survey_service, response_service, session_service):
    """Create a chats service."""
    return ChatsService(survey_service, response_service, session_service)


@pytest.fixture
def mock_session(mock_survey, mock_survey_response, session_id):
    """Mock session."""
    return Session(
        id=session_id,
        survey=mock_survey,
        response=mock_survey_response
    )


async def test_handle_message_success(
    chats_service,
    session_id,
    mock_session,
    mock_question,
    mock_next_question,
    session_service,
    response_service
):
    """Test successful message handling."""
    # Setup
    session_service.get_active_session.return_value = mock_session
    response_service.add_question_response.return_value = SurveyResponse(
        id="response123",
        survey_id="survey123",
        user_id="user123",
        current_question_id="q2",
        responses={"q1": "John"}
    )

    # Execute
    result = await chats_service.handle_message(session_id, "John")

    # Assert
    assert result.id == "q2"
    session_service.get_active_session.assert_called_once_with(session_id)
    response_service.add_question_response.assert_called_once_with(
        mock_session.response.id,
        mock_question,
        "John"
    )
    session_service.update_session.assert_called_once()


async def test_handle_message_survey_complete(
    chats_service,
    session_id,
    mock_session,
    mock_question,
    session_service,
    response_service
):
    """Test handling of completed survey."""
    # Setup
    session_service.get_active_session.return_value = mock_session
    response_service.add_question_response.return_value = SurveyResponse(
        id="response123",
        survey_id="survey123",
        user_id="user123",
        current_question_id=None,  # Indicates survey completion
        responses={"q1": "John"}
    )

    # Execute
    result = await chats_service.handle_message(session_id, "John")

    # Assert
    assert result is None
    session_service.delete_session.assert_called_once_with(session_id)


async def test_handle_message_invalid_response(
    chats_service,
    session_id,
    mock_session,
    mock_question,
    session_service,
    response_service
):
    """Test handling of invalid response."""
    # Setup
    session_service.get_active_session.return_value = mock_session
    response_service.add_question_response.side_effect = BusinessRuleError("Invalid response")

    # Execute and Assert
    with pytest.raises(BusinessRuleError, match="Invalid response"):
        await chats_service.handle_message(session_id, "invalid")


async def test_handle_message_session_not_found(
    chats_service,
    session_id,
    session_service
):
    """Test handling of missing session."""
    # Setup
    session_service.get_active_session.return_value = None

    # Execute and Assert
    with pytest.raises(BusinessRuleError, match="Session not found"):
        await chats_service.handle_message(session_id, "test")
