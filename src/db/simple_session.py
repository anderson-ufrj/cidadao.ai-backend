"""
Simple database session management for SQLite.
"""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

load_dotenv()


def _ensure_async_driver(url: str) -> str:
    """Ensure PostgreSQL URL uses the async driver (asyncpg)."""
    # If it's a PostgreSQL URL without a driver specification, add asyncpg
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        # Replace postgresql:// or postgres:// with postgresql+asyncpg://
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    # If it already has a driver (like postgresql+asyncpg or sqlite+aiosqlite), keep it
    return url


# Get DATABASE_URL from environment and ensure it uses async driver
_raw_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./cidadao_ai.db")
DATABASE_URL = _ensure_async_driver(_raw_url)

# Lazy initialization
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker | None = None


def _get_engine() -> AsyncEngine:
    """Get or create the async engine (lazy initialization)."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
        )
    return _engine


def _get_session_factory() -> async_sessionmaker:
    """Get or create the session factory (lazy initialization)."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            _get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session context manager."""
    factory = _get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Alias for FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session."""
    async with get_db_session() as session:
        yield session
