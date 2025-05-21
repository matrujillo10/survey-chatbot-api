"""Common response definitions for API endpoints."""

from typing import Any, Dict

from fastapi import status


# Not Found
def not_found_response(resource: str = "Item") -> Dict[int, Dict[str, Any]]:
    """Generate a 404 response for a specific resource type."""
    return {
        status.HTTP_404_NOT_FOUND: {
            "description": f"{resource} not found",
            "content": {"application/json": {"example": {"detail": f"{resource} not found"}}},
        }
    }


# Validation Errors
validation_responses = {
    status.HTTP_400_BAD_REQUEST: {
        "description": "Bad Request",
        "content": {"application/json": {"example": {"detail": "Invalid request data"}}},
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "loc": ["body", "field_name"],
                            "msg": "field required",
                            "type": "value_error.missing",
                        }
                    ]
                }
            }
        },
    },
}

# Server Errors
server_error_responses = {
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
        "content": {"application/json": {"example": {"detail": "An unexpected error occurred"}}},
    }
}

# Service Health
service_unavailable_responses = {
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        "description": "Service Unavailable",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Service is not available",
                    "details": {"database": "down", "cache": "up"},
                }
            }
        },
    }
}


# Conflict Responses
def conflict_response(message: str) -> Dict[int, Dict[str, Any]]:
    """Generate a 409 response with a custom message."""
    return {
        status.HTTP_409_CONFLICT: {
            "description": "Conflict",
            "content": {"application/json": {"example": {"detail": message}}},
        }
    }


# Common Response Combinations
standard_get_responses = {**server_error_responses}

standard_write_responses = {**validation_responses, **server_error_responses}


# Helper to combine responses
def combine_responses(*responses: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """Combine multiple response dictionaries."""
    combined = {}
    for response in responses:
        combined.update(response)
    return combined
