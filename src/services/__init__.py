"""Service layer for Cidadao.AI business logic.

This module provides service interfaces for:
- External API integrations
- Business logic orchestration
- Data processing services

Status: Stub implementation - Full services planned for production phase.
"""

from .data_service import DataService
from .analysis_service import AnalysisService
from .notification_service import NotificationService
from .maritaca_client import MaritacaClient, MaritacaModel, create_maritaca_client

__all__ = [
    "DataService",
    "AnalysisService",
    "NotificationService",
    "MaritacaClient",
    "MaritacaModel",
    "create_maritaca_client"
]