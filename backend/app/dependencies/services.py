"""Dependencies for services"""

from typing import Annotated

from fastapi import Depends

from ..services.survey_service import SurveyService
from ..services.response_service import ResponseService
from ..services.session_service import SessionService
from ..services.chats_service import ChatsService
from .repositories import (
    SurveyRepositoryDep,
    ResponseRepositoryDep,
    SessionRepositoryDep,
)


async def get_survey_service(repository: SurveyRepositoryDep) -> SurveyService:
    """Get survey service instance."""
    return SurveyService(repository)


async def get_response_service(
    response_repository: ResponseRepositoryDep, survey_repository: SurveyRepositoryDep
) -> ResponseService:
    """Get response service instance."""
    return ResponseService(response_repository, survey_repository)


SurveyServiceDep = Annotated[SurveyService, Depends(get_survey_service)]
ResponseServiceDep = Annotated[ResponseService, Depends(get_response_service)]


async def get_session_service(
    session_repository: SessionRepositoryDep,
    survey_service: SurveyServiceDep,
    response_service: ResponseServiceDep,
) -> SessionService:
    """Get session service instance."""
    return SessionService(session_repository, survey_service, response_service)


SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]


async def get_chats_service(
    survey_service: SurveyServiceDep,
    response_service: ResponseServiceDep,
    session_service: SessionServiceDep,
) -> ChatsService:
    """Get chats service instance."""
    return ChatsService(survey_service, response_service, session_service)


ChatsServiceDep = Annotated[ChatsService, Depends(get_chats_service)]
