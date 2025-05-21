"""Surveys router"""

from typing import List

from fastapi import APIRouter, HTTPException, status

from ..models.surveys import Survey, SurveyUpdate
from ..dependencies.services import SurveyServiceDep
from ..core.exceptions import (
    ServiceError,
    ResourceNotFoundError,
    ResourceConflictError,
    BusinessRuleError,
)
from ..core.common_responses import (
    not_found_response,
    validation_responses,
    server_error_responses,
    conflict_response,
    combine_responses,
)

surveys_router = APIRouter(prefix="/surveys", tags=["surveys"], responses=server_error_responses)


@surveys_router.post(
    "/",
    response_model=Survey,
    responses=combine_responses(
        validation_responses, conflict_response("Survey with this title already exists")
    ),
    status_code=status.HTTP_201_CREATED,
)
async def create_survey(survey: Survey, service: SurveyServiceDep):
    """
    Create a new survey.

    Raises:
        400: Invalid survey data
        409: Survey already exists
        500: Internal server error
    """
    try:
        return await service.create_survey(survey)
    except ResourceConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message) from e
    except BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e
    except ServiceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@surveys_router.get("/", response_model=List[Survey])
async def list_surveys(service: SurveyServiceDep):
    """
    List all surveys.

    Only returns active surveys.

    Raises:
        500: Internal server error
    """
    try:
        return await service.list_surveys()
    except ServiceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@surveys_router.get("/{survey_id}", response_model=Survey, responses=not_found_response("Survey"))
async def get_survey(survey_id: str, service: SurveyServiceDep):
    """
    Get a specific survey by ID.

    Raises:
        404: Survey not found
        400: Invalid survey ID
        500: Internal server error
    """
    try:
        return await service.get_survey(survey_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e
    except ServiceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@surveys_router.put(
    "/{survey_id}",
    response_model=Survey,
    responses=combine_responses(not_found_response("Survey"), validation_responses),
)
async def update_survey(survey_id: str, survey: SurveyUpdate, service: SurveyServiceDep):
    """
    Update a survey.

    Raises:
        404: Survey not found
        400: Invalid update data or survey ID
        500: Internal server error
    """
    try:
        return await service.update_survey(survey_id, survey)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e
    except ServiceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@surveys_router.delete(
    "/{survey_id}",
    responses=combine_responses(
        not_found_response("Survey"),
        conflict_response("Cannot delete survey with active responses"),
    ),
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_survey(survey_id: str, service: SurveyServiceDep):
    """
    Delete a survey.

    Raises:
        404: Survey not found
        400: Invalid survey ID
        500: Internal server error
    """
    try:
        await service.delete_survey(survey_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e
    except ServiceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
