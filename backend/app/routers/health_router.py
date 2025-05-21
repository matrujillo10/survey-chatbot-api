"""Health router"""

from typing import Dict

from fastapi import APIRouter

health_router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@health_router.get("/")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.

    Returns:
        Dict with status of the application.
    """
    return {"status": "ok"}
