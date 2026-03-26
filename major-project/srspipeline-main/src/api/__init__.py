"""API Module - FastAPI endpoints for SRS generation."""

from .routes import router
from .models import (
    GenerateSRSRequest,
    GenerateSRSResponse,
    ValidateSRSRequest,
    ValidateSRSResponse,
    TemplateInfo,
    TemplateListResponse
)

__all__ = [
    "router",
    "GenerateSRSRequest",
    "GenerateSRSResponse",
    "ValidateSRSRequest",
    "ValidateSRSResponse",
    "TemplateInfo",
    "TemplateListResponse"
]
