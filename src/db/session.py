"""
Module: db.session
Description: Database session management with connection pooling
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.connection_pool_service import connection_pool_service
from src.core import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def get_session(
    read_only: bool = False
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session with connection pooling.
    
    Args:
        read_only: Use read replica if available
        
    Yields:
        AsyncSession instance or None if no database available
    """
    async with connection_pool_service.get_db_session(
        pool_name="main",
        read_only=read_only
    ) as session:
        yield session


# Alias for compatibility
get_db = get_session


async def init_database():
    """Initialize database connection pools for Railway deployment."""
    try:
        await connection_pool_service.initialize()
        logger.info("Database connection pools initialized successfully (Railway + Supabase)")
    except Exception as e:
        logger.error(
            "Failed to initialize database pools",
            error=str(e),
            exc_info=True
        )
        # Don't raise - allow app to start without database
        logger.warning("Running without database connection - some features may be limited")


async def close_database():
    """Close database connection pools."""
    try:
        await connection_pool_service.cleanup()
        logger.info("Database connection pools closed")
    except Exception as e:
        logger.error(
            "Failed to close database pools",
            error=str(e),
            exc_info=True
        )