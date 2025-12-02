"""
Supabase integration service for direct database access.

This service provides a bridge between the backend and Supabase PostgreSQL,
allowing investigations to be stored centrally for frontend consumption.
"""

import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from asyncpg import Pool, create_pool
from pydantic import BaseModel, Field

from src.core import get_logger
from src.core.exceptions import CidadaoAIError

logger = get_logger(__name__)


class SupabaseConfig(BaseModel):
    """Supabase connection configuration."""

    url: str = Field(..., description="Supabase PostgreSQL connection URL")
    anon_key: str | None = Field(
        None, description="Supabase anon key (for Row Level Security)"
    )
    service_role_key: str | None = Field(
        None, description="Supabase service role key (bypasses RLS)"
    )
    min_connections: int = Field(default=5, description="Minimum pool connections")
    max_connections: int = Field(default=20, description="Maximum pool connections")

    @classmethod
    def from_env(cls) -> "SupabaseConfig":
        """Load configuration from environment variables."""
        supabase_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")

        if not supabase_url:
            raise ValueError(
                "SUPABASE_DB_URL or DATABASE_URL environment variable required. "
                "Get it from: Supabase Dashboard > Settings > Database > Connection string (URI)"
            )

        return cls(
            url=supabase_url,
            anon_key=os.getenv("SUPABASE_ANON_KEY"),
            service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
            min_connections=int(os.getenv("SUPABASE_MIN_CONNECTIONS", "5")),
            max_connections=int(os.getenv("SUPABASE_MAX_CONNECTIONS", "20")),
        )


class SupabaseService:
    """
    Service for interacting with Supabase PostgreSQL.

    Provides connection pooling and CRUD operations for investigations.
    """

    def __init__(self, config: SupabaseConfig | None = None):
        """
        Initialize Supabase service.

        Args:
            config: Supabase configuration (loads from env if None)
        """
        self.config = config or SupabaseConfig.from_env()
        self._pool: Pool | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize connection pool."""
        if self._initialized:
            logger.warning("Supabase service already initialized")
            return

        try:
            logger.info("Initializing Supabase connection pool")

            self._pool = await create_pool(
                dsn=self.config.url,
                min_size=self.config.min_connections,
                max_size=self.config.max_connections,
                command_timeout=30,
                server_settings={
                    "application_name": "cidadao-ai-backend",
                    "timezone": "UTC",
                },
            )

            # Test connection
            async with self._pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                logger.info(f"Connected to Supabase PostgreSQL: {version[:50]}...")

            self._initialized = True
            logger.info("Supabase service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Supabase service: {e}", exc_info=True)
            raise CidadaoAIError(f"Supabase initialization failed: {e}")

    async def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._initialized = False
            logger.info("Supabase connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """
        Get a database connection from the pool.

        Yields:
            Connection instance
        """
        if not self._initialized:
            await self.initialize()

        async with self._pool.acquire() as conn:
            yield conn

    async def create_investigation(
        self,
        user_id: str,
        query: str,
        data_source: str,
        filters: dict[str, Any] | None = None,
        anomaly_types: list[str] | None = None,
        session_id: str | None = None,
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
        async with self.get_connection() as conn:
            import json

            row = await conn.fetchrow(
                """
                INSERT INTO investigations (
                    user_id, session_id, query, data_source,
                    status, filters, anomaly_types, progress,
                    created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7::jsonb, $8, $9, $10)
                RETURNING *
                """,
                user_id,
                session_id,
                query,
                data_source,
                "pending",
                json.dumps(filters or {}),
                json.dumps(anomaly_types or []),
                0.0,
                datetime.now(UTC),
                datetime.now(UTC),
            )

            logger.info(f"Created investigation {row['id']} in Supabase")
            return dict(row)

    async def get_investigation(self, investigation_id: str) -> dict[str, Any] | None:
        """
        Get investigation by ID.

        Args:
            investigation_id: Investigation UUID

        Returns:
            Investigation dict or None
        """
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM investigations WHERE id = $1", investigation_id
            )

            return dict(row) if row else None

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
        import json

        # JSONB fields that need special handling
        jsonb_fields = {"results", "filters", "anomaly_types"}

        # Build dynamic UPDATE query
        set_clauses = []
        values = []
        param_index = 1

        for key, value in updates.items():
            if key in jsonb_fields and isinstance(value, (dict, list)):
                set_clauses.append(f"{key} = ${param_index}::jsonb")
                values.append(json.dumps(value))
            else:
                set_clauses.append(f"{key} = ${param_index}")
                values.append(value)
            param_index += 1

        # Always update updated_at
        set_clauses.append(f"updated_at = ${param_index}")
        values.append(datetime.now(UTC))
        param_index += 1

        # Add investigation_id as last parameter
        values.append(investigation_id)

        query = f"""
            UPDATE investigations
            SET {', '.join(set_clauses)}
            WHERE id = ${param_index}
            RETURNING *
        """

        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, *values)

            if not row:
                raise ValueError(f"Investigation {investigation_id} not found")

            logger.debug(f"Updated investigation {investigation_id}")
            return dict(row)

    async def update_progress(
        self,
        investigation_id: str,
        progress: float,
        current_phase: str,
        records_processed: int | None = None,
        anomalies_found: int | None = None,
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
            completed_at=datetime.now(UTC),
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
            completed_at=datetime.now(UTC),
        )

    async def list_user_investigations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
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
        async with self.get_connection() as conn:
            query = """
                SELECT * FROM investigations
                WHERE user_id = $1
            """
            params = [user_id]

            if status:
                query += " AND status = $2"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT $" + str(len(params) + 1)
            params.append(limit)

            query += " OFFSET $" + str(len(params) + 1)
            params.append(offset)

            rows = await conn.fetch(query, *params)

            return [dict(row) for row in rows]

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
        async with self.get_connection() as conn:
            result = await conn.execute(
                """
                UPDATE investigations
                SET status = 'cancelled', completed_at = $1
                WHERE id = $2 AND user_id = $3
                """,
                datetime.now(UTC),
                investigation_id,
                user_id,
            )

            # Extract number of rows affected
            rows_affected = int(result.split()[-1])

            if rows_affected > 0:
                logger.info(f"Cancelled investigation {investigation_id}")
                return True

            return False

    async def health_check(self) -> dict[str, Any]:
        """
        Check Supabase connection health.

        Returns:
            Health status dict
        """
        try:
            async with self.get_connection() as conn:
                # Simple query to test connection
                result = await conn.fetchval("SELECT 1")
                pool_size = self._pool.get_size()
                pool_free = self._pool.get_idle_size()

                return {
                    "status": "healthy",
                    "connected": True,
                    "pool_size": pool_size,
                    "pool_free": pool_free,
                    "pool_used": pool_size - pool_free,
                }
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
            }


# Global service instance
supabase_service = SupabaseService()


async def get_supabase_service() -> SupabaseService:
    """Get the global Supabase service instance."""
    if not supabase_service._initialized:
        await supabase_service.initialize()
    return supabase_service
