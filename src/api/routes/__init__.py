"""
Module: api.routes
Description: API route modules for Cidadao.AI transparency platform
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from . import (
    analysis,
    chaos,
    chat,
    cqrs,
    health,
    investigations,
    monitoring,
    notifications,
    observability,
    reports,
    resilience,
    websocket_chat,
)

__all__ = [
    "health",
    "investigations",
    "analysis",
    "reports",
    "chat",
    "websocket_chat",
    "cqrs",
    "resilience",
    "observability",
    "monitoring",
    "chaos",
    "notifications",
]
