"""Exceptions used throughout the application."""

from typing import Any, Optional


# Base Exceptions
class AppError(Exception):
    """Base class for application exceptions."""

    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


# Repository Exceptions
class RepositoryError(AppError):
    """Base class for repository exceptions."""


class InvalidSurveyIdError(RepositoryError):
    """Raised when a survey ID is not in valid format."""


# Service Exceptions
class ServiceError(AppError):
    """Base class for service exceptions."""


class ValidationError(ServiceError):
    """Raised when service validation fails."""


class ResourceNotFoundError(ServiceError):
    """Raised when a requested resource is not found."""


class ResourceConflictError(ServiceError):
    """Raised when there's a conflict with existing resource."""


class BusinessRuleError(ServiceError):
    """Raised when a business rule is violated."""


class SurveyNotFoundError(RepositoryError):
    """Raised when a survey is not found."""


class SurveyIntegrityError(RepositoryError):
    """Raised when a survey update would break survey integrity."""
