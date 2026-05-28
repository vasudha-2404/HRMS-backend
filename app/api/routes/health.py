"""Health check routes."""

from fastapi import APIRouter

from app.core.config import settings
from app.utils.response import success_response

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return success_response(
        {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        },
        "Service is healthy",
    )
