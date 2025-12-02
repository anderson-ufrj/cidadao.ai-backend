"""
Query handling for CQRS pattern implementation.

This module provides query definitions and handlers for read operations,
optimized separately from write operations.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from src.core import get_logger
from src.infrastructure.query_cache import query_cache

logger = get_logger(__name__)

T = TypeVar("T")
R = TypeVar("R")


class Query(BaseModel):
    """Base class for all queries."""

    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str | None = None
    use_cache: bool = True
    cache_ttl: int | None = None


class QueryResult(BaseModel, Generic[T]):
    """Result of query execution."""

    success: bool
    query_id: str
    data: T | None = None
    error: str | None = None
    from_cache: bool = False
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


# Investigation Queries
class GetInvestigationByIdQuery(Query):
    """Query to get investigation by ID."""

    investigation_id: str
    include_findings: bool = True
    include_anomalies: bool = True


class SearchInvestigationsQuery(Query):
    """Query to search investigations."""

    filters: dict[str, Any] = Field(default_factory=dict)
    sort_by: str = "created_at"
    sort_order: str = "desc"
    limit: int = 20
    offset: int = 0


class GetInvestigationStatsQuery(Query):
    """Query to get investigation statistics."""

    user_id: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


# Contract Queries
class SearchContractsQuery(Query):
    """Query to search contracts."""

    search_term: str | None = None
    orgao: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    year: int | None = None
    limit: int = 50
    offset: int = 0


# Agent Queries
class GetAgentPerformanceQuery(Query):
    """Query to get agent performance metrics."""

    agent_name: str | None = None
    time_period: str = "1h"  # 1h, 24h, 7d, 30d


class QueryHandler(ABC, Generic[T, R]):
    """
    Base class for query handlers.

    Handles read operations with caching support.
    """

    @abstractmethod
    async def handle(self, query: T) -> QueryResult[R]:
        """
        Handle a query.

        Args:
            query: Query to handle

        Returns:
            Query result
        """
        pass

    @abstractmethod
    def can_handle(self, query: Query) -> bool:
        """
        Check if this handler can handle the query.

        Args:
            query: Query to check

        Returns:
            True if handler can process this query
        """
        pass

    def _get_cache_key(self, query: Query) -> str:
        """Generate cache key for query."""
        import hashlib

        from src.core.json_utils import dumps

        # Create deterministic key from query data
        query_data = query.model_dump(exclude={"query_id", "timestamp", "use_cache"})
        query_str = dumps(query_data)

        return f"query:{query.__class__.__name__}:{hashlib.md5(query_str.encode()).hexdigest()}"


class GetInvestigationByIdHandler(
    QueryHandler[GetInvestigationByIdQuery, dict[str, Any]]
):
    """Handler for getting investigation by ID."""

    async def handle(
        self, query: GetInvestigationByIdQuery
    ) -> QueryResult[dict[str, Any]]:
        """Get investigation by ID."""
        start_time = datetime.now(UTC)

        try:
            # Check cache if enabled
            if query.use_cache:
                cache_key = self._get_cache_key(query)
                cached_result = await query_cache.get_or_fetch(
                    query=cache_key,
                    fetch_func=lambda: self._fetch_investigation(query),
                    ttl=query.cache_ttl or 300,
                )

                if cached_result is not None:
                    execution_time = (
                        datetime.now(UTC) - start_time
                    ).total_seconds() * 1000

                    return QueryResult(
                        success=True,
                        query_id=query.query_id,
                        data=cached_result,
                        from_cache=True,
                        execution_time_ms=execution_time,
                    )

            # Fetch from database
            result = await self._fetch_investigation(query)

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return QueryResult(
                success=True,
                query_id=query.query_id,
                data=result,
                from_cache=False,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return QueryResult(
                success=False,
                query_id=query.query_id,
                error=str(e),
                execution_time_ms=(datetime.now(UTC) - start_time).total_seconds()
                * 1000,
            )

    async def _fetch_investigation(
        self, query: GetInvestigationByIdQuery
    ) -> dict[str, Any]:
        """Fetch investigation from database."""
        # Simulated database fetch
        # In real implementation, this would query the read model
        return {
            "id": query.investigation_id,
            "status": "completed",
            "query": "Sample investigation",
            "confidence_score": 0.85,
            "findings": [] if query.include_findings else None,
            "anomalies": [] if query.include_anomalies else None,
        }

    def can_handle(self, query: Query) -> bool:
        """Check if this handler can handle the query."""
        return isinstance(query, GetInvestigationByIdQuery)


class SearchInvestigationsHandler(
    QueryHandler[SearchInvestigationsQuery, list[dict[str, Any]]]
):
    """Handler for searching investigations."""

    async def handle(
        self, query: SearchInvestigationsQuery
    ) -> QueryResult[list[dict[str, Any]]]:
        """Search investigations."""
        start_time = datetime.now(UTC)

        try:
            # Build query based on filters
            results = await self._search_investigations(query)

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return QueryResult(
                success=True,
                query_id=query.query_id,
                data=results,
                from_cache=False,
                execution_time_ms=execution_time,
                metadata={
                    "total_count": len(results),
                    "has_more": len(results) == query.limit,
                },
            )

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return QueryResult(
                success=False,
                query_id=query.query_id,
                error=str(e),
                execution_time_ms=(datetime.now(UTC) - start_time).total_seconds()
                * 1000,
            )

    async def _search_investigations(
        self, query: SearchInvestigationsQuery
    ) -> list[dict[str, Any]]:
        """Search investigations in database."""
        # Simulated search
        # In real implementation, this would query the read model
        return [
            {
                "id": f"inv-{i}",
                "query": f"Investigation {i}",
                "status": "completed",
                "created_at": datetime.now(UTC).isoformat(),
            }
            for i in range(min(query.limit, 5))
        ]

    def can_handle(self, query: Query) -> bool:
        """Check if this handler can handle the query."""
        return isinstance(query, SearchInvestigationsQuery)


class QueryBus:
    """
    Query bus for routing queries to appropriate handlers.

    Provides a unified interface for all read operations.
    """

    def __init__(self):
        """Initialize query bus."""
        self._handlers: list[QueryHandler] = []
        self._middleware: list[QueryMiddleware] = []

        # Statistics
        self._stats = {
            "queries_processed": 0,
            "queries_succeeded": 0,
            "queries_failed": 0,
            "cache_hits": 0,
            "total_execution_time_ms": 0.0,
        }

        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default query handlers."""
        self.register_handler(GetInvestigationByIdHandler())
        self.register_handler(SearchInvestigationsHandler())

    def register_handler(self, handler: QueryHandler):
        """
        Register a query handler.

        Args:
            handler: Handler to register
        """
        self._handlers.append(handler)
        logger.info(f"Registered query handler: {handler.__class__.__name__}")

    def register_middleware(self, middleware: "QueryMiddleware"):
        """
        Register query middleware.

        Args:
            middleware: Middleware to register
        """
        self._middleware.append(middleware)
        logger.info(f"Registered query middleware: {middleware.__class__.__name__}")

    async def execute(self, query: Query) -> QueryResult:
        """
        Execute a query.

        Args:
            query: Query to execute

        Returns:
            Query result
        """
        self._stats["queries_processed"] += 1

        try:
            # Apply middleware
            for middleware in self._middleware:
                query = await middleware.before_execute(query)

            # Find handler
            handler = None
            for h in self._handlers:
                if h.can_handle(query):
                    handler = h
                    break

            if not handler:
                raise ValueError(f"No handler found for query: {type(query).__name__}")

            # Execute query
            result = await handler.handle(query)

            # Apply middleware to result
            for middleware in reversed(self._middleware):
                result = await middleware.after_execute(query, result)

            # Update statistics
            if result.success:
                self._stats["queries_succeeded"] += 1
                if result.from_cache:
                    self._stats["cache_hits"] += 1
                self._stats["total_execution_time_ms"] += result.execution_time_ms
            else:
                self._stats["queries_failed"] += 1

            return result

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            self._stats["queries_failed"] += 1

            return QueryResult(success=False, query_id=query.query_id, error=str(e))

    def get_stats(self) -> dict[str, Any]:
        """Get query bus statistics."""
        total_queries = self._stats["queries_processed"]

        return {
            **self._stats,
            "handlers_registered": len(self._handlers),
            "middleware_registered": len(self._middleware),
            "success_rate": (
                self._stats["queries_succeeded"] / total_queries
                if total_queries > 0
                else 0
            ),
            "cache_hit_rate": (
                self._stats["cache_hits"] / self._stats["queries_succeeded"]
                if self._stats["queries_succeeded"] > 0
                else 0
            ),
            "avg_execution_time_ms": (
                self._stats["total_execution_time_ms"]
                / self._stats["queries_succeeded"]
                if self._stats["queries_succeeded"] > 0
                else 0
            ),
        }


class QueryMiddleware(ABC):
    """Base class for query middleware."""

    @abstractmethod
    async def before_execute(self, query: Query) -> Query:
        """Process query before execution."""
        pass

    @abstractmethod
    async def after_execute(self, query: Query, result: QueryResult) -> QueryResult:
        """Process result after execution."""
        pass


class PerformanceMiddleware(QueryMiddleware):
    """Middleware for tracking query performance."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.slow_query_threshold_ms = 1000.0

    async def before_execute(self, query: Query) -> Query:
        """Mark query start time."""
        query.metadata = query.metadata or {}
        query.metadata["start_time"] = datetime.now(UTC)
        return query

    async def after_execute(self, query: Query, result: QueryResult) -> QueryResult:
        """Log slow queries."""
        if result.execution_time_ms > self.slow_query_threshold_ms:
            self.logger.warning(
                f"Slow query detected: {query.__class__.__name__} "
                f"took {result.execution_time_ms:.2f}ms"
            )
        return result
