"""
Supabase integration service using REST API (works on HuggingFace Spaces).

This service uses Supabase's REST API via HTTP/HTTPS instead of direct
PostgreSQL connections, making it compatible with restricted environments
like HuggingFace Spaces that block direct database connections.
"""

import os
from datetime import UTC, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field
from supabase import Client, create_client

from src.core import get_logger
from src.core.exceptions import CidadaoAIError

logger = get_logger(__name__)


class SupabaseConfig(BaseModel):
    """Supabase connection configuration."""

    url: str = Field(..., description="Supabase project URL")
    key: str = Field(..., description="Supabase service role key (for backend)")
    anon_key: Optional[str] = Field(
        None, description="Supabase anon key (for frontend)"
    )

    @classmethod
    def from_env(cls) -> "SupabaseConfig":
        """Load configuration from environment variables."""
        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not service_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables required. "
                "Get them from: Supabase Dashboard > Settings > API"
            )

        return cls(
            url=supabase_url,
            key=service_key,
            anon_key=os.getenv("SUPABASE_ANON_KEY"),
        )


class SupabaseServiceRest:
    """
    Service for interacting with Supabase via REST API.

    Uses HTTP/HTTPS which works in restricted environments like HuggingFace Spaces
    where direct PostgreSQL connections are blocked.
    """

    def __init__(self, config: Optional[SupabaseConfig] = None):
        """
        Initialize Supabase service.

        Args:
            config: Supabase configuration (loads from env if None)
        """
        self._config = config
        self._client: Optional[Client] = None
        self._initialized = False

    @property
    def config(self) -> SupabaseConfig:
        """Lazy load configuration."""
        if self._config is None:
            self._config = SupabaseConfig.from_env()
        return self._config

    async def initialize(self) -> None:
        """Initialize Supabase client."""
        if self._initialized:
            logger.warning("Supabase REST service already initialized")
            return

        try:
            logger.info("Initializing Supabase REST client")

            self._client = create_client(
                supabase_url=self.config.url,
                supabase_key=self.config.key,
            )

            # Test connection with a simple query
            result = (
                self._client.table("investigations").select("id").limit(1).execute()
            )

            self._initialized = True
            logger.info("Supabase REST service initialized successfully")

        except Exception as e:
            logger.error(
                f"Failed to initialize Supabase REST service: {e}", exc_info=True
            )
            raise CidadaoAIError(f"Supabase REST initialization failed: {e}")

    def _ensure_client(self) -> Client:
        """Ensure client is initialized."""
        if not self._initialized or not self._client:
            # Synchronous initialization for backwards compatibility
            import asyncio

            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if not self._initialized:
                loop.run_until_complete(self.initialize())

        return self._client

    async def create_investigation(
        self,
        user_id: str,
        query: str,
        data_source: str,
        filters: Optional[dict[str, Any]] = None,
        anomaly_types: Optional[list[str]] = None,
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create a new investigation in Supabase.

        Args:
            user_id: User ID
            query: Investigation query
            data_source: Data source to investigate
            filters: Query filters
            anomaly_types: Types of anomalies to detect
            session_id: Optional session ID

        Returns:
            Created investigation as dict
        """
        client = self._ensure_client()

        data = {
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "data_source": data_source,
            "status": "pending",
            "filters": filters or {},
            "anomaly_types": anomaly_types or [],
            "progress": 0.0,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }

        result = client.table("investigations").insert(data).execute()

        if not result.data or len(result.data) == 0:
            raise CidadaoAIError("Failed to create investigation")

        investigation = result.data[0]
        logger.info(f"Created investigation {investigation['id']} via REST API")
        return investigation

    async def get_investigation(
        self, investigation_id: str
    ) -> Optional[dict[str, Any]]:
        """
        Get investigation by ID.

        Args:
            investigation_id: Investigation UUID

        Returns:
            Investigation dict or None
        """
        client = self._ensure_client()

        result = (
            client.table("investigations")
            .select("*")
            .eq("id", investigation_id)
            .execute()
        )

        if not result.data or len(result.data) == 0:
            return None

        return result.data[0]

    async def update_investigation(
        self, investigation_id: str, **updates
    ) -> dict[str, Any]:
        """
        Update investigation fields.

        Args:
            investigation_id: Investigation UUID
            **updates: Fields to update

        Returns:
            Updated investigation dict
        """
        client = self._ensure_client()

        # Always update updated_at
        updates["updated_at"] = datetime.now(UTC).isoformat()

        result = (
            client.table("investigations")
            .update(updates)
            .eq("id", investigation_id)
            .execute()
        )

        if not result.data or len(result.data) == 0:
            raise ValueError(f"Investigation {investigation_id} not found")

        logger.debug(f"Updated investigation {investigation_id} via REST API")
        return result.data[0]

    async def update_progress(
        self,
        investigation_id: str,
        progress: float,
        current_phase: str,
        records_processed: Optional[int] = None,
        anomalies_found: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Update investigation progress.

        Args:
            investigation_id: Investigation UUID
            progress: Progress percentage (0.0 to 1.0)
            current_phase: Current processing phase
            records_processed: Number of records processed
            anomalies_found: Number of anomalies detected

        Returns:
            Updated investigation dict
        """
        updates = {
            "progress": progress,
            "current_phase": current_phase,
        }

        if records_processed is not None:
            updates["total_records_analyzed"] = records_processed

        if anomalies_found is not None:
            updates["anomalies_found"] = anomalies_found

        return await self.update_investigation(investigation_id, **updates)

    async def complete_investigation(
        self,
        investigation_id: str,
        results: list[dict[str, Any]],
        summary: str,
        confidence_score: float,
        total_records: int,
        anomalies_found: int,
    ) -> dict[str, Any]:
        """
        Mark investigation as completed with results.

        Args:
            investigation_id: Investigation UUID
            results: List of anomaly results
            summary: Investigation summary
            confidence_score: Overall confidence
            total_records: Total records analyzed
            anomalies_found: Total anomalies found

        Returns:
            Updated investigation dict
        """
        return await self.update_investigation(
            investigation_id,
            status="completed",
            progress=1.0,
            current_phase="completed",
            results=results,
            summary=summary,
            confidence_score=confidence_score,
            total_records_analyzed=total_records,
            anomalies_found=anomalies_found,
            completed_at=datetime.now(UTC).isoformat(),
        )

    async def fail_investigation(
        self,
        investigation_id: str,
        error_message: str,
    ) -> dict[str, Any]:
        """
        Mark investigation as failed.

        Args:
            investigation_id: Investigation UUID
            error_message: Error description

        Returns:
            Updated investigation dict
        """
        return await self.update_investigation(
            investigation_id,
            status="failed",
            current_phase="failed",
            error_message=error_message,
            completed_at=datetime.now(UTC).isoformat(),
        )

    async def list_user_investigations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        List investigations for a user.

        Args:
            user_id: User ID
            limit: Maximum results
            offset: Pagination offset
            status: Filter by status

        Returns:
            List of investigation dicts
        """
        client = self._ensure_client()

        query = client.table("investigations").select("*").eq("user_id", user_id)

        if status:
            query = query.eq("status", status)

        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

        result = query.execute()

        return result.data if result.data else []

    async def delete_investigation(
        self,
        investigation_id: str,
        user_id: str,
    ) -> bool:
        """
        Delete an investigation (soft delete by marking as cancelled).

        Args:
            investigation_id: Investigation UUID
            user_id: User ID (for authorization)

        Returns:
            True if deleted, False if not found
        """
        client = self._ensure_client()

        result = (
            client.table("investigations")
            .update(
                {
                    "status": "cancelled",
                    "completed_at": datetime.now(UTC).isoformat(),
                }
            )
            .eq("id", investigation_id)
            .eq("user_id", user_id)
            .execute()
        )

        if result.data and len(result.data) > 0:
            logger.info(f"Cancelled investigation {investigation_id} via REST API")
            return True

        return False

    async def health_check(self) -> dict[str, Any]:
        """
        Check Supabase connection health.

        Returns:
            Health status dict
        """
        try:
            client = self._ensure_client()

            # Simple query to test connection
            result = client.table("investigations").select("id").limit(1).execute()

            return {
                "status": "healthy",
                "connected": True,
                "api_version": "rest",
            }
        except Exception as e:
            logger.error(f"Supabase REST health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
            }


# Global service instance
supabase_service_rest = SupabaseServiceRest()


async def get_supabase_service_rest() -> SupabaseServiceRest:
    """Get the global Supabase REST service instance."""
    if not supabase_service_rest._initialized:
        await supabase_service_rest.initialize()
    return supabase_service_rest
