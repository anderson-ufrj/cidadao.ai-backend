"""
Smart Investigation Service Selector.

Automatically selects the correct investigation service implementation based on environment:
- HuggingFace Spaces: Uses REST API (HTTP/HTTPS)
- Local/VPS with PostgreSQL: Uses direct connection

This allows the same code to work in both environments without modification.
"""

import logging
import os
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.services.investigation_service import InvestigationService


# Detect environment
def _is_huggingface_spaces() -> bool:
    """Detect if running on HuggingFace Spaces."""
    return (
        os.getenv("SPACE_ID") is not None or os.getenv("SPACE_AUTHOR_NAME") is not None
    )


def _has_supabase_rest_config() -> bool:
    """Check if Supabase REST API configuration is available."""
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


def _has_postgres_config() -> bool:
    """Check if PostgreSQL direct connection configuration is available."""
    return bool(os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL"))


def get_investigation_service() -> "InvestigationService":
    """
    Get the appropriate investigation service for the current environment.

    Returns:
        Investigation service instance (PostgreSQL direct or in-memory)
    """
    # Priority 1: PostgreSQL direct connection (Railway, VPS, Local)
    if _has_postgres_config():
        logger.info(
            "🐘 Using PostgreSQL direct connection for investigations (Railway/VPS)"
        )
        from src.services.investigation_service import investigation_service

        return investigation_service

    # Priority 2: HuggingFace Spaces - use Supabase REST API if available
    if _is_huggingface_spaces():
        if not _has_supabase_rest_config():
            logger.warning(
                "⚠️  HuggingFace Spaces detected but no database configured. "
                "Using in-memory storage (data will be lost on restart). "
                "Add SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY for persistence."
            )
            from src.services.investigation_service import investigation_service

            return investigation_service

        logger.info(
            "🚀 Using Supabase REST service for investigations (HuggingFace Spaces)"
        )
        from src.services.investigation_service_supabase_rest import (
            investigation_service_supabase_rest,
        )

        return investigation_service_supabase_rest

    # Fallback: Use in-memory service (no persistence)
    logger.warning(
        "⚠️  Using IN-MEMORY investigation service (no persistence!) - Configure DATABASE_URL for persistence"
    )
    from src.services.investigation_service import investigation_service

    return investigation_service


# Global service instance - automatically selected
investigation_service = get_investigation_service()
