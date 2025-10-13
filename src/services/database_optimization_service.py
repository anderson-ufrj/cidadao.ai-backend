"""
Module: services.database_optimization_service
Description: Database query optimization and index management
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_logger

logger = get_logger(__name__)


class QueryAnalysis:
    """Analysis result for a database query."""

    def __init__(self, query: str, execution_time: float, plan: dict[str, Any]):
        self.query = query
        self.execution_time = execution_time
        self.plan = plan
        self.suggestions = []
        self.estimated_improvement = 0.0

    def add_suggestion(self, suggestion: str, improvement: float = 0.0):
        """Add optimization suggestion."""
        self.suggestions.append(suggestion)
        self.estimated_improvement += improvement


class DatabaseOptimizationService:
    """Service for database performance optimization."""

    def __init__(self):
        """Initialize database optimization service."""
        self._slow_query_threshold = 1.0  # seconds
        self._index_suggestions = {}
        self._query_stats = {}

    async def analyze_slow_queries(
        self, session: AsyncSession, limit: int = 20
    ) -> list[QueryAnalysis]:
        """Analyze slow queries from PostgreSQL."""
        analyses = []

        try:
            # Get slow queries from pg_stat_statements
            slow_queries_sql = """
            SELECT
                query,
                mean_exec_time / 1000.0 as mean_exec_seconds,
                calls,
                total_exec_time / 1000.0 as total_exec_seconds,
                min_exec_time / 1000.0 as min_exec_seconds,
                max_exec_time / 1000.0 as max_exec_seconds,
                rows
            FROM pg_stat_statements
            WHERE mean_exec_time > :threshold_ms
                AND query NOT LIKE '%pg_stat%'
                AND query NOT LIKE '%information_schema%'
            ORDER BY mean_exec_time DESC
            LIMIT :limit
            """

            result = await session.execute(
                text(slow_queries_sql),
                {"threshold_ms": self._slow_query_threshold * 1000, "limit": limit},
            )

            rows = result.fetchall()

            for row in rows:
                # Analyze each slow query
                analysis = QueryAnalysis(
                    query=row.query,
                    execution_time=row.mean_exec_seconds,
                    plan={
                        "calls": row.calls,
                        "total_time": row.total_exec_seconds,
                        "min_time": row.min_exec_seconds,
                        "max_time": row.max_exec_seconds,
                        "rows": row.rows,
                    },
                )

                # Get query plan
                await self._analyze_query_plan(session, analysis)

                # Generate suggestions
                self._generate_suggestions(analysis)

                analyses.append(analysis)

            logger.info("slow_query_analysis_completed", queries_analyzed=len(analyses))

        except Exception as e:
            logger.error("slow_query_analysis_error", error=str(e), exc_info=True)

        return analyses

    async def _analyze_query_plan(self, session: AsyncSession, analysis: QueryAnalysis):
        """Analyze query execution plan."""
        try:
            # Get EXPLAIN ANALYZE for the query
            explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {analysis.query}"

            result = await session.execute(text(explain_sql))
            plan_data = result.scalar()

            if plan_data:
                analysis.plan["execution_plan"] = plan_data[0]["Plan"]

                # Extract key metrics
                plan = plan_data[0]["Plan"]
                analysis.plan["total_cost"] = plan.get("Total Cost", 0)
                analysis.plan["actual_time"] = plan.get("Actual Total Time", 0)

                # Look for problematic patterns
                self._check_plan_issues(plan, analysis)

        except Exception as e:
            logger.debug(f"Could not analyze plan for query: {e}")

    def _check_plan_issues(self, plan: dict[str, Any], analysis: QueryAnalysis):
        """Check for common plan issues."""
        # Sequential scan on large tables
        if plan.get("Node Type") == "Seq Scan":
            rows = plan.get("Actual Rows", 0)
            if rows > 1000:
                analysis.add_suggestion(
                    f"Sequential scan on {rows} rows. Consider adding an index.",
                    improvement=0.5,
                )

        # Nested loops with high iterations
        if plan.get("Node Type") == "Nested Loop":
            loops = plan.get("Actual Loops", 0)
            if loops > 100:
                analysis.add_suggestion(
                    f"Nested loop with {loops} iterations. Consider query restructuring.",
                    improvement=0.3,
                )

        # Check child nodes recursively
        if "Plans" in plan:
            for child_plan in plan["Plans"]:
                self._check_plan_issues(child_plan, analysis)

    def _generate_suggestions(self, analysis: QueryAnalysis):
        """Generate optimization suggestions for a query."""
        query_lower = analysis.query.lower()

        # Check for missing LIMIT
        if "select" in query_lower and "limit" not in query_lower:
            if analysis.plan.get("rows", 0) > 1000:
                analysis.add_suggestion(
                    "Query returns many rows. Consider adding LIMIT clause.",
                    improvement=0.2,
                )

        # Check for SELECT *
        if "select *" in query_lower:
            analysis.add_suggestion(
                "Avoid SELECT *. Specify only needed columns.", improvement=0.1
            )

        # Check for missing WHERE on large tables
        if "where" not in query_lower and analysis.plan.get("rows", 0) > 10000:
            analysis.add_suggestion(
                "No WHERE clause on large result set. Add filtering.", improvement=0.4
            )

        # Check for IN with many values
        import re

        in_matches = re.findall(r"IN\s*\([^)]+\)", query_lower)
        for match in in_matches:
            values_count = match.count(",") + 1
            if values_count > 10:
                analysis.add_suggestion(
                    f"IN clause with {values_count} values. Consider using JOIN or temp table.",
                    improvement=0.2,
                )

    async def create_missing_indexes(
        self, session: AsyncSession, dry_run: bool = True
    ) -> list[dict[str, Any]]:
        """Create missing indexes based on analysis."""
        index_commands = []

        try:
            # Analyze foreign key columns without indexes
            fk_index_sql = """
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND NOT EXISTS (
                    SELECT 1
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                        AND tablename = tc.table_name
                        AND indexdef LIKE '%' || kcu.column_name || '%'
                )
            """

            result = await session.execute(text(fk_index_sql))
            fk_without_index = result.fetchall()

            for row in fk_without_index:
                index_name = f"idx_{row.table_name}_{row.column_name}"
                index_cmd = (
                    f"CREATE INDEX {index_name} ON {row.table_name} ({row.column_name})"
                )

                index_commands.append(
                    {
                        "type": "foreign_key",
                        "table": row.table_name,
                        "column": row.column_name,
                        "command": index_cmd,
                        "reason": f"Foreign key to {row.foreign_table_name}",
                    }
                )

            # Analyze frequently filtered columns
            filter_columns = await self._analyze_filter_columns(session)

            for table, column, frequency in filter_columns:
                # Check if index already exists
                check_sql = """
                SELECT 1 FROM pg_indexes
                WHERE schemaname = 'public'
                    AND tablename = :table
                    AND indexdef LIKE :pattern
                """

                exists = await session.execute(
                    text(check_sql), {"table": table, "pattern": f"%{column}%"}
                )

                if not exists.scalar():
                    index_name = f"idx_{table}_{column}_filter"
                    index_cmd = f"CREATE INDEX {index_name} ON {table} ({column})"

                    index_commands.append(
                        {
                            "type": "frequent_filter",
                            "table": table,
                            "column": column,
                            "command": index_cmd,
                            "reason": f"Frequently used in WHERE clause ({frequency} times)",
                        }
                    )

            # Execute or return commands
            if not dry_run and index_commands:
                for idx_info in index_commands:
                    try:
                        await session.execute(text(idx_info["command"]))
                        idx_info["status"] = "created"
                        logger.info(
                            "index_created",
                            table=idx_info["table"],
                            column=idx_info["column"],
                        )
                    except Exception as e:
                        idx_info["status"] = "failed"
                        idx_info["error"] = str(e)
                        logger.error(
                            "index_creation_failed",
                            table=idx_info["table"],
                            error=str(e),
                        )

                await session.commit()

        except Exception as e:
            logger.error("create_indexes_error", error=str(e), exc_info=True)

        return index_commands

    async def _analyze_filter_columns(
        self, session: AsyncSession
    ) -> list[tuple[str, str, int]]:
        """Analyze frequently filtered columns from query patterns."""
        filter_columns = []

        try:
            # Parse WHERE clauses from pg_stat_statements
            filter_analysis_sql = """
            SELECT
                query,
                calls
            FROM pg_stat_statements
            WHERE query LIKE '%WHERE%'
                AND query NOT LIKE '%pg_stat%'
                AND calls > 10
            ORDER BY calls DESC
            LIMIT 100
            """

            result = await session.execute(text(filter_analysis_sql))
            queries = result.fetchall()

            # Simple pattern matching for WHERE conditions
            import re

            column_frequency = {}

            for query, calls in queries:
                # Extract table.column or column patterns after WHERE
                where_match = re.search(
                    r"WHERE\s+(.+?)(?:ORDER|GROUP|LIMIT|$)", query, re.IGNORECASE
                )
                if where_match:
                    conditions = where_match.group(1)

                    # Find column references
                    column_patterns = re.findall(
                        r"(\w+)\.(\w+)\s*[=<>]|(\w+)\s*[=<>]", conditions
                    )

                    for pattern in column_patterns:
                        if pattern[0] and pattern[1]:  # table.column format
                            key = (pattern[0], pattern[1])
                        elif pattern[2]:  # column only format
                            # Try to infer table from FROM clause
                            from_match = re.search(
                                r"FROM\s+(\w+)", query, re.IGNORECASE
                            )
                            if from_match:
                                key = (from_match.group(1), pattern[2])
                            else:
                                continue
                        else:
                            continue

                        column_frequency[key] = column_frequency.get(key, 0) + calls

            # Sort by frequency
            for (table, column), frequency in sorted(
                column_frequency.items(), key=lambda x: x[1], reverse=True
            )[:20]:
                filter_columns.append((table, column, frequency))

        except Exception as e:
            logger.error("filter_column_analysis_error", error=str(e), exc_info=True)

        return filter_columns

    async def optimize_table_statistics(
        self, session: AsyncSession, tables: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Update table statistics for query planner."""
        results = {"analyzed": [], "vacuumed": [], "errors": []}

        try:
            # Get all tables if not specified
            if not tables:
                tables_sql = """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                """
                result = await session.execute(text(tables_sql))
                tables = [row[0] for row in result.fetchall()]

            for table in tables:
                try:
                    # ANALYZE table
                    await session.execute(text(f"ANALYZE {table}"))
                    results["analyzed"].append(table)

                    # Check if VACUUM needed
                    vacuum_check_sql = """
                    SELECT
                        n_dead_tup,
                        n_live_tup
                    FROM pg_stat_user_tables
                    WHERE relname = :table
                    """

                    result = await session.execute(
                        text(vacuum_check_sql), {"table": table}
                    )
                    row = result.fetchone()

                    if row and row.n_dead_tup > row.n_live_tup * 0.2:
                        # More than 20% dead tuples, vacuum needed
                        await session.execute(text(f"VACUUM ANALYZE {table}"))
                        results["vacuumed"].append(table)
                        logger.info(
                            "table_vacuumed", table=table, dead_tuples=row.n_dead_tup
                        )

                except Exception as e:
                    results["errors"].append({"table": table, "error": str(e)})
                    logger.error(f"Failed to optimize table {table}: {e}")

            await session.commit()

        except Exception as e:
            logger.error("table_optimization_error", error=str(e), exc_info=True)

        return results

    async def get_database_stats(self, session: AsyncSession) -> dict[str, Any]:
        """Get comprehensive database statistics."""
        stats = {}

        try:
            # Database size
            size_sql = """
            SELECT
                pg_database_size(current_database()) as db_size,
                pg_size_pretty(pg_database_size(current_database())) as db_size_pretty
            """
            result = await session.execute(text(size_sql))
            size_info = result.fetchone()
            stats["database_size"] = {
                "bytes": size_info.db_size,
                "pretty": size_info.db_size_pretty,
            }

            # Table sizes
            table_sizes_sql = """
            SELECT
                schemaname,
                tablename,
                pg_total_relation_size(schemaname||'.'||tablename) as total_size,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size_pretty,
                n_live_tup as row_count
            FROM pg_tables
            JOIN pg_stat_user_tables USING (schemaname, tablename)
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10
            """
            result = await session.execute(text(table_sizes_sql))
            stats["largest_tables"] = [
                {
                    "table": row.tablename,
                    "size_bytes": row.total_size,
                    "size_pretty": row.size_pretty,
                    "row_count": row.row_count,
                }
                for row in result.fetchall()
            ]

            # Index usage
            index_usage_sql = """
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            ORDER BY idx_scan
            LIMIT 20
            """
            result = await session.execute(text(index_usage_sql))
            stats["least_used_indexes"] = [
                {
                    "table": row.tablename,
                    "index": row.indexname,
                    "scans": row.idx_scan,
                    "size": row.index_size,
                }
                for row in result.fetchall()
            ]

            # Cache hit ratio
            cache_sql = """
            SELECT
                sum(heap_blks_read) as heap_read,
                sum(heap_blks_hit) as heap_hit,
                sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0) as cache_hit_ratio
            FROM pg_statio_user_tables
            """
            result = await session.execute(text(cache_sql))
            cache_info = result.fetchone()
            stats["cache_hit_ratio"] = {
                "ratio": float(cache_info.cache_hit_ratio or 0),
                "heap_read": cache_info.heap_read,
                "heap_hit": cache_info.heap_hit,
            }

            # Connection stats
            conn_sql = """
            SELECT
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections,
                count(*) FILTER (WHERE state = 'idle') as idle_connections,
                count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
            FROM pg_stat_activity
            WHERE datname = current_database()
            """
            result = await session.execute(text(conn_sql))
            conn_info = result.fetchone()
            stats["connections"] = {
                "total": conn_info.total_connections,
                "active": conn_info.active_connections,
                "idle": conn_info.idle_connections,
                "idle_in_transaction": conn_info.idle_in_transaction,
            }

        except Exception as e:
            logger.error("database_stats_error", error=str(e), exc_info=True)

        return stats


# Global instance
database_optimization_service = DatabaseOptimizationService()
