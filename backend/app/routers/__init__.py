"""FastAPI router definitions."""

from .surveys_router import surveys_router as surveys
from .health_router import health_router as health
from .chats_router import chats_router as chats

__all__ = ["surveys", "health", "chats"]
