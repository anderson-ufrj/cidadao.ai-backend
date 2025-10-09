"""
Smart Investigation Service Selector.

Automatically selects the correct investigation service implementation based on environment:
- HuggingFace Spaces: Uses REST API (HTTP/HTTPS)
- Local/VPS with PostgreSQL: Uses direct connection

This allows the same code to work in both environments without modification.
"""

import os
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.services.investigation_service import InvestigationService

# Detect environment
def _is_huggingface_spaces() -> bool:
    """Detect if running on HuggingFace Spaces."""
    return os.getenv("SPACE_ID") is not None or os.getenv("SPACE_AUTHOR_NAME") is not None


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
        Investigation service instance (REST API or direct PostgreSQL)
    """
    # Priority 1: HuggingFace Spaces MUST use REST API
    if _is_huggingface_spaces():
        if not _has_supabase_rest_config():
            raise RuntimeError(
                "HuggingFace Spaces detected but SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY not configured. "
                "Add these to your Space secrets: https://huggingface.co/spaces/YOUR_SPACE/settings"
            )

        logger.info("🚀 Using Supabase REST service for investigations (HuggingFace Spaces)")
        from src.services.investigation_service_supabase_rest import investigation_service_supabase_rest
        return investigation_service_supabase_rest

    # Priority 2: If REST API config available, prefer it (more portable)
    if _has_supabase_rest_config():
        logger.info("🚀 Using Supabase REST service for investigations (Railway/VPS)")
        from src.services.investigation_service_supabase_rest import investigation_service_supabase_rest
        return investigation_service_supabase_rest

    # Priority 3: If PostgreSQL config available, use direct connection
    if _has_postgres_config():
        logger.info("🔌 Using Supabase direct PostgreSQL connection for investigations")
        from src.services.investigation_service_supabase import investigation_service_supabase
        return investigation_service_supabase

    # Fallback: Use in-memory service (no persistence)
    logger.warning("⚠️  Using IN-MEMORY investigation service (no persistence!) - Configure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY for persistence")
    from src.services.investigation_service import investigation_service
    return investigation_service


# Global service instance - automatically selected
investigation_service = get_investigation_service()
