"""Chats router"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException, status

from ..dependencies.services import ChatsServiceDep
from ..models.sessions import SessionId
from ..models.surveys import Question
from ..models.types import QuestionType
from ..core.exceptions import BusinessRuleError
from ..core.logging import get_logger


chats_router = APIRouter(
    prefix="/respond",
    tags=["respond"],
)


logger = get_logger(__name__)


def _format_question(question: Question) -> str:
    formatted = question.text + "\n"

    match question.type:
        case QuestionType.MULTIPLE_CHOICE | QuestionType.RATING:
            if question.options:
                formatted += "\nChoose one of:\n"
                for i, option in enumerate(question.options, 1):
                    formatted += f"{i}. {option.text}\n"
            else:
                formatted += "\n(No options available)"

        case QuestionType.BOOLEAN:
            formatted += "\nPlease answer with 'yes' or 'no'"

        case QuestionType.DATE:
            formatted += "\nPlease enter a date (YYYY-MM-DD)"

    return formatted.strip()


def _goodbye_message() -> str:
    return "Thank you for your time. That were all the questions!"


def _error_message(error: BusinessRuleError) -> str:
    return f"Error: {error.message}"


def _welcome_message() -> str:
    return "Welcome to the survey! Please answer the following questions."


@chats_router.websocket("/survey/{survey_id}/user/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    survey_id: str,
    chats_service: ChatsServiceDep,
):
    """Web socket endpoint for chat interactions."""
    try:
        session_id = SessionId(user_id=user_id, survey_id=survey_id)
        question = await chats_service.connect(session_id)
        await websocket.accept()

        await websocket.send_text(_welcome_message())

        while True:
            await websocket.send_text(_format_question(question))
            message = await websocket.receive_text()
            try:
                question = await chats_service.handle_message(session_id, message)

                if question is None:
                    await websocket.send_text(_goodbye_message())
                    await websocket.close()
                    break

            except BusinessRuleError as e:
                await websocket.send_text(_error_message(e))
                continue

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except BusinessRuleError as e:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=e.message) from e
    finally:
        await chats_service.disconnect(session_id)
