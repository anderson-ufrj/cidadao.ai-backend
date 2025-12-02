"""
Transparency Data Orchestrator

Central orchestration system for all Brazilian government transparency APIs.
Provides intelligent routing, fallback strategies, and unified data aggregation.

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brasil
Created: 2025-10-16 16:15:00 -03:00
License: Proprietary - All rights reserved
"""

from datetime import datetime
from enum import Enum
from typing import Any

from src.core import get_logger
from src.services.transparency_apis.federal_apis.bcb_client import (
    BancoCentralClient as BCBClient,
)
from src.services.transparency_apis.federal_apis.compras_gov_client import (
    ComprasGovClient,
)
from src.services.transparency_apis.federal_apis.pncp_client import PNCPClient
from src.services.transparency_apis.registry import registry
from src.tools.transparency_api import TransparencyAPIClient

logger = get_logger(__name__)


class DataSource(str, Enum):
    """Available data sources."""

    PORTAL_FEDERAL = "portal_federal"
    PNCP = "pncp"
    COMPRAS_GOV = "compras_gov"
    BCB = "bcb"
    TCE = "tce"
    STATE_PORTAL = "state_portal"
    CKAN = "ckan"


class QueryStrategy(str, Enum):
    """Query execution strategies."""

    FASTEST = "fastest"  # Return first successful response
    AGGREGATE = "aggregate"  # Combine all responses
    FALLBACK = "fallback"  # Try in priority order
    PARALLEL = "parallel"  # Execute all in parallel


class TransparencyOrchestrator:
    """
    Central orchestrator for Brazilian transparency data.

    Features:
    - Multi-source data aggregation
    - Intelligent routing by state/data type
    - Automatic fallback between APIs
    - Unified caching layer
    - Performance metrics
    """

    def __init__(self):
        """Initialize orchestrator with all available clients."""
        self.portal_federal = TransparencyAPIClient()
        self.pncp_client: PNCPClient | None = None
        self.compras_gov_client: ComprasGovClient | None = None
        self.bcb_client: BCBClient | None = None

        # Statistics
        self._query_count = 0
        self._source_usage: dict[str, int] = {}
        self._error_count: dict[str, int] = {}

        logger.info(
            "transparency_orchestrator_initialized",
            sources=["portal_federal", "pncp", "compras_gov", "bcb", "tce", "state"],
        )

    async def _get_pncp_client(self) -> PNCPClient:
        """Lazy initialization of PNCP client."""
        if self.pncp_client is None:
            self.pncp_client = PNCPClient()
        return self.pncp_client

    async def _get_compras_client(self) -> ComprasGovClient:
        """Lazy initialization of Compras.gov client."""
        if self.compras_gov_client is None:
            self.compras_gov_client = ComprasGovClient()
        return self.compras_gov_client

    async def _get_bcb_client(self) -> BCBClient:
        """Lazy initialization of BCB client."""
        if self.bcb_client is None:
            self.bcb_client = BCBClient()
        return self.bcb_client

    async def get_contracts(
        self,
        filters: dict | None = None,
        strategy: QueryStrategy = QueryStrategy.FALLBACK,
        sources: list[DataSource] | None = None,
    ) -> dict[str, Any]:
        """
        Get contracts from multiple sources with intelligent routing.

        Args:
            filters: Query filters (ano, estado, valor, etc.)
            strategy: Execution strategy
            sources: Specific sources to query (if None, auto-select)

        Returns:
            Unified contract data with metadata
        """
        self._query_count += 1
        start_time = datetime.now()

        # Auto-select sources if not specified
        if sources is None:
            sources = self._select_sources_for_contracts(filters)

        logger.info(
            "orchestrator_query_started",
            query_type="contracts",
            strategy=strategy,
            sources=[s.value for s in sources],
            filters=filters,
        )

        results = {
            "data": [],
            "sources": [],
            "metadata": {
                "query_id": f"query_{self._query_count}",
                "timestamp": datetime.now().isoformat(),
                "strategy": strategy,
                "sources_attempted": len(sources),
            },
        }

        # Execute strategy
        if strategy == QueryStrategy.FALLBACK:
            results = await self._execute_fallback(sources, "contracts", filters)
        elif strategy == QueryStrategy.AGGREGATE:
            results = await self._execute_aggregate(sources, "contracts", filters)
        elif strategy == QueryStrategy.FASTEST:
            results = await self._execute_fastest(sources, "contracts", filters)
        elif strategy == QueryStrategy.PARALLEL:
            results = await self._execute_parallel(sources, "contracts", filters)

        # Add performance metadata
        duration = (datetime.now() - start_time).total_seconds()
        results["metadata"]["duration_seconds"] = duration

        logger.info(
            "orchestrator_query_completed",
            query_id=results["metadata"]["query_id"],
            total_records=len(results["data"]),
            sources_used=len(results["sources"]),
            duration=duration,
        )

        return results

    def _select_sources_for_contracts(self, filters: dict | None) -> list[DataSource]:
        """
        Intelligently select best sources for contract query.

        Priority logic:
        1. If state specified → Try state TCE first, then federal
        2. If federal contract → Portal Federal, PNCP, Compras.gov
        3. Default → Portal Federal
        """
        sources = []

        if not filters:
            # Default: federal sources
            return [DataSource.PORTAL_FEDERAL, DataSource.PNCP]

        # Check if state-specific query
        state_code = filters.get("estado") or filters.get("uf")

        if state_code:
            # Try state sources first
            sources.append(DataSource.TCE)

        # Always include federal as fallback
        sources.extend([DataSource.PORTAL_FEDERAL, DataSource.PNCP])

        return sources

    async def _execute_fallback(
        self,
        sources: list[DataSource],
        data_type: str,
        filters: dict | None,
    ) -> dict[str, Any]:
        """
        Execute query with fallback strategy.

        Try sources in order until one succeeds.
        """
        for source in sources:
            try:
                logger.info(
                    "trying_source",
                    source=source.value,
                    data_type=data_type,
                )

                result = await self._query_source(source, data_type, filters)

                if result and len(result.get("data", [])) > 0:
                    # Success!
                    self._record_success(source)

                    return {
                        "data": result["data"],
                        "sources": [source.value],
                        "metadata": {
                            "primary_source": source.value,
                            "fallback_used": sources.index(source) > 0,
                        },
                    }

            except Exception as e:
                logger.warning(
                    "source_failed",
                    source=source.value,
                    error=str(e),
                )
                self._record_error(source)
                continue

        # All sources failed
        logger.error(
            "all_sources_failed",
            sources=[s.value for s in sources],
            data_type=data_type,
        )

        return {
            "data": [],
            "sources": [],
            "metadata": {"error": "All sources failed"},
        }

    async def _execute_aggregate(
        self,
        sources: list[DataSource],
        data_type: str,
        filters: dict | None,
    ) -> dict[str, Any]:
        """
        Execute query with aggregation strategy.

        Query all sources and combine results.
        """
        all_data = []
        successful_sources = []

        for source in sources:
            try:
                result = await self._query_source(source, data_type, filters)

                if result and result.get("data"):
                    all_data.extend(result["data"])
                    successful_sources.append(source.value)
                    self._record_success(source)

            except Exception as e:
                logger.warning(
                    "source_failed_in_aggregation",
                    source=source.value,
                    error=str(e),
                )
                self._record_error(source)

        # Deduplicate data (by ID if available)
        unique_data = self._deduplicate_records(all_data)

        return {
            "data": unique_data,
            "sources": successful_sources,
            "metadata": {
                "aggregated": True,
                "total_sources": len(sources),
                "successful_sources": len(successful_sources),
                "records_before_dedup": len(all_data),
                "records_after_dedup": len(unique_data),
            },
        }

    async def _execute_fastest(
        self,
        sources: list[DataSource],
        data_type: str,
        filters: dict | None,
    ) -> dict[str, Any]:
        """
        Execute query with fastest-first strategy.

        Return first successful response (race condition).
        """
        import asyncio

        tasks = [self._query_source(source, data_type, filters) for source in sources]

        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                if result and result.get("data"):
                    source_idx = tasks.index(coro)
                    source = sources[source_idx]
                    self._record_success(source)

                    return {
                        "data": result["data"],
                        "sources": [source.value],
                        "metadata": {"fastest_source": source.value},
                    }

            except Exception as e:
                logger.warning("fastest_source_failed", error=str(e))

        return {"data": [], "sources": [], "metadata": {"error": "All sources failed"}}

    async def _execute_parallel(
        self,
        sources: list[DataSource],
        data_type: str,
        filters: dict | None,
    ) -> dict[str, Any]:
        """
        Execute query in parallel (same as aggregate but async).
        """
        import asyncio

        tasks = [self._query_source(source, data_type, filters) for source in sources]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_data = []
        successful_sources = []

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                self._record_error(sources[idx])
                continue

            if result and result.get("data"):
                all_data.extend(result["data"])
                successful_sources.append(sources[idx].value)
                self._record_success(sources[idx])

        unique_data = self._deduplicate_records(all_data)

        return {
            "data": unique_data,
            "sources": successful_sources,
            "metadata": {
                "parallel": True,
                "total_sources": len(sources),
                "successful_sources": len(successful_sources),
            },
        }

    async def _query_source(
        self,
        source: DataSource,
        data_type: str,
        filters: dict | None,
    ) -> dict[str, Any]:
        """
        Query a specific data source.

        Routes to appropriate client based on source type.
        """
        if source == DataSource.PORTAL_FEDERAL:
            response = await self.portal_federal.get_contracts(filters)
            return {"data": response.data}

        elif source == DataSource.PNCP:
            client = await self._get_pncp_client()
            response = await client.get_contracts(filters)
            return {"data": response}

        elif source == DataSource.COMPRAS_GOV:
            client = await self._get_compras_client()
            response = await client.search_bids(filters)
            return {"data": response}

        elif source == DataSource.TCE:
            # Try to find appropriate TCE based on state
            state_code = filters.get("estado") or filters.get("uf") if filters else None
            if state_code:
                return await self._query_tce(state_code, data_type, filters)

        return {"data": []}

    async def _query_tce(
        self, state_code: str, data_type: str, filters: dict | None
    ) -> dict[str, Any]:
        """Query state TCE (Tribunal de Contas Estadual)."""
        tce_key = f"{state_code.upper()}-tce"
        client = registry.get_client(tce_key)

        if not client:
            logger.warning("tce_not_available", state=state_code)
            return {"data": []}

        # Query TCE (implementation depends on TCE client interface)
        try:
            # Most TCEs have similar methods
            if hasattr(client, "get_contracts"):
                result = await client.get_contracts(filters)
                return {"data": result if isinstance(result, list) else [result]}
        except Exception as e:
            logger.error("tce_query_failed", state=state_code, error=str(e))

        return {"data": []}

    def _deduplicate_records(self, records: list[dict]) -> list[dict]:
        """
        Deduplicate records based on ID or content hash.

        Args:
            records: List of records to deduplicate

        Returns:
            Deduplicated list
        """
        seen = set()
        unique = []

        for record in records:
            # Try to use ID field
            record_id = (
                record.get("id")
                or record.get("numero_contrato")
                or record.get("numeroContrato")
            )

            if not record_id:
                # Fallback: use hash of record
                import hashlib
                import json

                record_str = json.dumps(record, sort_keys=True)
                record_id = hashlib.md5(record_str.encode()).hexdigest()

            if record_id not in seen:
                seen.add(record_id)
                unique.append(record)

        return unique

    def _record_success(self, source: DataSource) -> None:
        """Record successful query from source."""
        source_key = source.value
        self._source_usage[source_key] = self._source_usage.get(source_key, 0) + 1

    def _record_error(self, source: DataSource) -> None:
        """Record error from source."""
        source_key = source.value
        self._error_count[source_key] = self._error_count.get(source_key, 0) + 1

    def get_statistics(self) -> dict[str, Any]:
        """
        Get orchestrator statistics.

        Returns:
            Dict with usage and performance metrics
        """
        return {
            "total_queries": self._query_count,
            "source_usage": self._source_usage,
            "error_count": self._error_count,
            "success_rate_by_source": {
                source: (
                    self._source_usage.get(source, 0)
                    / max(
                        1,
                        self._source_usage.get(source, 0)
                        + self._error_count.get(source, 0),
                    )
                )
                for source in set(
                    list(self._source_usage.keys()) + list(self._error_count.keys())
                )
            },
        }


# Global orchestrator instance
orchestrator = TransparencyOrchestrator()
