"""
Investigation service for managing investigations with database persistence.

This module provides a service layer for investigation operations,
abstracting the database and agent interactions.
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select

from src.agents import MasterAgent, get_agent_pool
from src.agents.deodoro import AgentContext
from src.core import get_logger
from src.db.simple_session import get_db_session
from src.models.investigation import Investigation

logger = get_logger(__name__)


class InvestigationService:
    """
    Service for managing investigations with SQLite/PostgreSQL persistence.
    """

    def __init__(self):
        """Initialize investigation service."""
        pass

    async def create(
        self,
        user_id: str,
        query: str,
        data_source: str = "contracts",
        filters: dict[str, Any] | None = None,
        anomaly_types: list[str] | None = None,
        session_id: str | None = None,
    ) -> Investigation:
        """
        Create a new investigation in the database.

        Args:
            user_id: User ID
            query: Investigation query
            data_source: Data source to investigate
            filters: Query filters
            anomaly_types: Types of anomalies to detect
            session_id: Optional session ID

        Returns:
            Created investigation
        """
        async with get_db_session() as db:
            investigation = Investigation(
                user_id=user_id,
                session_id=session_id,
                query=query,
                data_source=data_source,
                status="pending",
                filters=filters or {},
                anomaly_types=anomaly_types or [],
                progress=0.0,
            )

            db.add(investigation)
            await db.commit()
            await db.refresh(investigation)

            logger.info(f"Created investigation {investigation.id} for user {user_id}")
            return investigation

    async def update_status(
        self,
        investigation_id: str,
        status: str,
        progress: float | None = None,
        current_phase: str | None = None,
        **kwargs,
    ) -> Investigation:
        """Update investigation status and progress."""
        async with get_db_session() as db:
            result = await db.execute(
                select(Investigation).where(Investigation.id == investigation_id)
            )
            investigation = result.scalar_one_or_none()

            if not investigation:
                raise ValueError(f"Investigation {investigation_id} not found")

            investigation.status = status
            if progress is not None:
                investigation.progress = progress
            if current_phase is not None:
                investigation.current_phase = current_phase

            # Update other fields, converting timezone-aware datetimes to naive
            # PostgreSQL TIMESTAMP WITHOUT TIME ZONE doesn't accept timezone-aware datetimes
            for key, value in kwargs.items():
                if hasattr(investigation, key):
                    # Convert timezone-aware datetime to naive (UTC)
                    if isinstance(value, datetime) and value.tzinfo is not None:
                        value = value.replace(tzinfo=None)
                    setattr(investigation, key, value)

            await db.commit()
            await db.refresh(investigation)

            return investigation

    async def _execute_investigation(self, investigation: Investigation):
        """Execute investigation using agents."""
        try:
            start_time = datetime.now(UTC)
            investigation.status = "processing"

            # Get agent pool
            pool = await get_agent_pool()

            # Create agent context
            context = AgentContext(
                investigation_id=investigation.id,
                user_id=investigation.user_id,
                data_sources=investigation.metadata.get("data_sources", []),
            )

            # Execute with master agent
            async with pool.acquire(MasterAgent, context) as master:
                result = await master._investigate(
                    {"query": investigation.query}, context
                )

            # Update investigation
            investigation.status = "completed"
            investigation.confidence_score = result.confidence_score
            investigation.completed_at = datetime.now(UTC)
            investigation.processing_time_ms = (
                investigation.completed_at - start_time
            ).total_seconds() * 1000

            logger.info(f"Investigation {investigation.id} completed")

        except Exception as e:
            logger.error(f"Investigation {investigation.id} failed: {e}")
            investigation.status = "failed"
            investigation.completed_at = datetime.now(UTC)

    async def get_by_id(self, investigation_id: str) -> Investigation | None:
        """Get investigation by ID from database."""
        async with get_db_session() as db:
            result = await db.execute(
                select(Investigation).where(Investigation.id == investigation_id)
            )
            return result.scalar_one_or_none()

    async def search(
        self,
        user_id: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Investigation]:
        """Search investigations with filters."""
        async with get_db_session() as db:
            query = select(Investigation)

            if user_id:
                query = query.where(Investigation.user_id == user_id)
            if status:
                query = query.where(Investigation.status == status)

            query = query.order_by(Investigation.created_at.desc())
            query = query.limit(limit).offset(offset)

            result = await db.execute(query)
            return list(result.scalars().all())

    async def cancel(self, investigation_id: str, user_id: str) -> Investigation:
        """Cancel an investigation."""
        async with get_db_session() as db:
            result = await db.execute(
                select(Investigation).where(Investigation.id == investigation_id)
            )
            investigation = result.scalar_one_or_none()

            if not investigation:
                raise ValueError(f"Investigation {investigation_id} not found")

            if investigation.user_id != user_id:
                raise ValueError("Unauthorized")

            if investigation.status in ["completed", "failed", "cancelled"]:
                raise ValueError(
                    f"Cannot cancel investigation in {investigation.status} status"
                )

            investigation.status = "cancelled"
            investigation.completed_at = datetime.now(UTC)

            await db.commit()
            await db.refresh(investigation)

            logger.info(f"Investigation {investigation_id} cancelled by user {user_id}")
            return investigation

    async def get_user_investigations(
        self, user_id: str, limit: int = 10
    ) -> list[Investigation]:
        """Get investigations for a user."""
        return await self.search(user_id=user_id, limit=limit)


# Global service instance
investigation_service = InvestigationService()
