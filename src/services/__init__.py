"""Service layer for Cidadão.AI business logic.

This module provides service interfaces for:
- External API integrations
- Business logic orchestration
- Data processing services

Status: Stub implementation - Full services planned for production phase.
"""

from .data_service import DataService
from .analysis_service import AnalysisService
from .notification_service import NotificationService

__all__ = [
    "DataService",
    "AnalysisService",
    "NotificationService"
]