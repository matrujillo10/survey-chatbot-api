"""Main module for the survey API."""

from fastapi import FastAPI

from .core.logging import setup_logging
from .routers import surveys, health, chats

# Initialize logging
setup_logging()

app = FastAPI(
    title="Survey API", description="API for managing surveys and responses", version="1.0.0"
)

# Include routers
app.include_router(surveys, prefix="/api/v1")
app.include_router(health, prefix="/api/v1")
app.include_router(chats, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
