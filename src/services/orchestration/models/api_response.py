"""
API Response Models

Data models for API responses.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class APIStatus(str, Enum):
    """API call status."""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CACHED = "cached"


class APIResponse(BaseModel):
    """Response from an API call."""

    api_name: str
    status: APIStatus
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    duration_seconds: float = 0.0
    cached: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)
