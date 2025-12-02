"""
Query analyzer for database performance optimization.

This module provides tools to analyze slow queries and suggest optimizations.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_logger
from src.infrastructure.database import get_async_session

logger = get_logger(__name__)


@dataclass
class QueryStats:
    """Statistics for a database query."""

    query: str
    calls: int
    total_time: float
    mean_time: float
    max_time: float
    min_time: float
    rows_returned: int
    database: str


@dataclass
class IndexSuggestion:
    """Suggestion for a database index."""

    table: str
    columns: list[str]
    index_type: str
    reason: str
    estimated_improvement: str


class QueryAnalyzer:
    """
    Analyzes database queries for performance optimization.

    Features:
    - Identify slow queries
    - Suggest missing indexes
    - Analyze query patterns
    - Monitor query performance
    """

    def __init__(self, slow_query_threshold_ms: float = 100.0):
        """
        Initialize query analyzer.

        Args:
            slow_query_threshold_ms: Threshold for slow queries in milliseconds
        """
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self._query_cache: dict[str, QueryStats] = {}

    async def analyze_pg_stat_statements(
        self, session: AsyncSession, limit: int = 20
    ) -> list[QueryStats]:
        """
        Analyze PostgreSQL pg_stat_statements for slow queries.

        Requires pg_stat_statements extension to be enabled.
        """
        try:
            # Check if extension is available
            result = await session.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'")
            )
            if not result.scalar():
                logger.warning("pg_stat_statements extension not available")
                return []

            # Get slow queries
            query = text(
                """
                SELECT
                    query,
                    calls,
                    total_exec_time,
                    mean_exec_time,
                    max_exec_time,
                    min_exec_time,
                    rows,
                    datname
                FROM pg_stat_statements
                JOIN pg_database ON pg_database.oid = dbid
                WHERE mean_exec_time > :threshold
                    AND query NOT LIKE '%pg_stat_statements%'
                    AND query NOT LIKE 'COMMIT%'
                    AND query NOT LIKE 'BEGIN%'
                ORDER BY mean_exec_time DESC
                LIMIT :limit
            """
            )

            result = await session.execute(
                query, {"threshold": self.slow_query_threshold_ms, "limit": limit}
            )

            stats = []
            for row in result:
                stats.append(
                    QueryStats(
                        query=row[0],
                        calls=row[1],
                        total_time=row[2],
                        mean_time=row[3],
                        max_time=row[4],
                        min_time=row[5],
                        rows_returned=row[6],
                        database=row[7],
                    )
                )

            logger.info(f"Found {len(stats)} slow queries")
            return stats

        except Exception as e:
            logger.error(f"Error analyzing pg_stat_statements: {e}")
            return []

    async def analyze_missing_indexes(
        self, session: AsyncSession
    ) -> list[IndexSuggestion]:
        """
        Analyze tables for missing indexes based on query patterns.
        """
        suggestions = []

        try:
            # Find tables with sequential scans
            query = text(
                """
                SELECT
                    schemaname,
                    tablename,
                    seq_scan,
                    seq_tup_read,
                    idx_scan,
                    n_tup_ins + n_tup_upd + n_tup_del as write_activity
                FROM pg_stat_user_tables
                WHERE seq_scan > idx_scan
                    AND seq_tup_read > 100000
                    AND schemaname = 'public'
                ORDER BY seq_tup_read DESC
            """
            )

            result = await session.execute(query)

            for row in result:
                table = row[1]
                seq_scans = row[2]
                seq_rows = row[3]
                idx_scans = row[4]

                # Suggest index if high sequential scan ratio
                if seq_scans > 0 and idx_scans > 0:
                    scan_ratio = seq_scans / (seq_scans + idx_scans)
                    if scan_ratio > 0.5:
                        suggestions.append(
                            await self._suggest_index_for_table(
                                session, table, "High sequential scan ratio"
                            )
                        )

            # Check for foreign keys without indexes
            fk_query = text(
                """
                SELECT
                    tc.table_name,
                    kcu.column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = 'public'
                    AND NOT EXISTS (
                        SELECT 1
                        FROM pg_indexes
                        WHERE tablename = tc.table_name
                            AND indexdef LIKE '%' || kcu.column_name || '%'
                    )
            """
            )

            fk_result = await session.execute(fk_query)

            for row in fk_result:
                suggestions.append(
                    IndexSuggestion(
                        table=row[0],
                        columns=[row[1]],
                        index_type="btree",
                        reason="Foreign key without index",
                        estimated_improvement="Faster joins and referential integrity checks",
                    )
                )

            return suggestions

        except Exception as e:
            logger.error(f"Error analyzing missing indexes: {e}")
            return []

    async def _suggest_index_for_table(
        self, session: AsyncSession, table: str, reason: str
    ) -> IndexSuggestion:
        """Suggest index for a specific table based on query patterns."""
        # Simplified suggestion - in production, analyze actual query patterns
        return IndexSuggestion(
            table=table,
            columns=["created_at", "status"],  # Common columns
            index_type="btree",
            reason=reason,
            estimated_improvement="Reduce sequential scans by 50-80%",
        )

    async def analyze_query_plan(
        self, session: AsyncSession, query: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Analyze execution plan for a specific query.
        """
        try:
            # Get query plan
            explain_query = text(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}")

            if params:
                result = await session.execute(explain_query, params)
            else:
                result = await session.execute(explain_query)

            plan = result.scalar()

            # Analyze plan for issues
            issues = []
            suggestions = []

            if plan:
                plan_data = plan[0]["Plan"]

                # Check for sequential scans
                if "Seq Scan" in str(plan_data):
                    issues.append("Sequential scan detected")
                    suggestions.append("Consider adding an index")

                # Check for high cost
                total_cost = plan_data.get("Total Cost", 0)
                if total_cost > 1000:
                    issues.append(f"High query cost: {total_cost}")
                    suggestions.append("Optimize query or add indexes")

                # Check execution time
                exec_time = plan[0].get("Execution Time", 0)
                if exec_time > self.slow_query_threshold_ms:
                    issues.append(f"Slow execution: {exec_time}ms")

            return {
                "plan": plan,
                "issues": issues,
                "suggestions": suggestions,
                "execution_time": plan[0].get("Execution Time", 0) if plan else 0,
            }

        except Exception as e:
            logger.error(f"Error analyzing query plan: {e}")
            return {
                "error": str(e),
                "issues": ["Failed to analyze query"],
                "suggestions": ["Check query syntax"],
            }

    async def get_table_statistics(
        self, session: AsyncSession, table: str
    ) -> dict[str, Any]:
        """Get statistics for a specific table."""
        try:
            stats_query = text(
                """
                SELECT
                    n_live_tup as row_count,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                WHERE tablename = :table
            """
            )

            result = await session.execute(stats_query, {"table": table})
            row = result.first()

            if row:
                return {
                    "table": table,
                    "row_count": row[0],
                    "dead_rows": row[1],
                    "last_vacuum": row[2],
                    "last_autovacuum": row[3],
                    "last_analyze": row[4],
                    "last_autoanalyze": row[5],
                    "bloat_ratio": row[1] / row[0] if row[0] > 0 else 0,
                }

            return {"table": table, "error": "Table not found"}

        except Exception as e:
            logger.error(f"Error getting table statistics: {e}")
            return {"table": table, "error": str(e)}

    async def suggest_query_optimizations(self, query: str) -> list[str]:
        """
        Suggest optimizations for a query based on common patterns.
        """
        suggestions = []
        query_lower = query.lower()

        # Check for SELECT *
        if "select *" in query_lower:
            suggestions.append("Avoid SELECT *, specify only needed columns")

        # Check for missing WHERE clause
        if "where" not in query_lower and (
            "update" in query_lower or "delete" in query_lower
        ):
            suggestions.append(
                "⚠️ No WHERE clause in UPDATE/DELETE - this affects all rows!"
            )

        # Check for LIKE with leading wildcard
        if "like '%%" in query_lower:
            suggestions.append("Leading wildcard in LIKE prevents index usage")

        # Check for NOT IN with subquery
        if "not in (select" in query_lower:
            suggestions.append("Replace NOT IN with NOT EXISTS for better performance")

        # Check for ORDER BY without LIMIT
        if "order by" in query_lower and "limit" not in query_lower:
            suggestions.append("Consider adding LIMIT when using ORDER BY")

        # Check for multiple OR conditions
        or_count = query_lower.count(" or ")
        if or_count > 3:
            suggestions.append(
                "Many OR conditions - consider using IN or restructuring"
            )

        return suggestions


# Global analyzer instance
query_analyzer = QueryAnalyzer()


async def analyze_database_performance():
    """Run a complete database performance analysis."""
    async for session in get_async_session():
        try:
            logger.info("Starting database performance analysis")

            # Analyze slow queries
            slow_queries = await query_analyzer.analyze_pg_stat_statements(session)

            # Get missing indexes
            index_suggestions = await query_analyzer.analyze_missing_indexes(session)

            # Get table statistics
            tables = ["investigations", "contracts", "anomalies", "agent_messages"]
            table_stats = []

            for table in tables:
                stats = await query_analyzer.get_table_statistics(session, table)
                table_stats.append(stats)

            report = {
                "timestamp": datetime.now(UTC),
                "slow_queries": [
                    {
                        "query": (
                            q.query[:200] + "..." if len(q.query) > 200 else q.query
                        ),
                        "mean_time_ms": q.mean_time,
                        "calls": q.calls,
                        "total_time_ms": q.total_time,
                    }
                    for q in slow_queries[:10]
                ],
                "index_suggestions": [
                    {
                        "table": s.table,
                        "columns": s.columns,
                        "reason": s.reason,
                        "improvement": s.estimated_improvement,
                    }
                    for s in index_suggestions
                ],
                "table_statistics": table_stats,
            }

            logger.info("Database performance analysis completed")
            return report

        except Exception as e:
            logger.error(f"Error in performance analysis: {e}")
            return {"error": str(e)}
