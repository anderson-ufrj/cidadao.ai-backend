"""
Data Service for Government Transparency Data

Central service for accessing Brazilian government transparency data
from multiple sources with intelligent routing and caching.

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brasil
Updated: 2025-10-16 16:30:00 -03:00
License: Proprietary - All rights reserved
"""

from datetime import datetime
from typing import Any

from src.core import get_logger
from src.services.transparency_orchestrator import (
    DataSource,
    QueryStrategy,
    orchestrator,
)
from src.tools.transparency_api import TransparencyAPIClient, TransparencyAPIFilter

logger = get_logger(__name__)


class DataService:
    """Service for data operations and management."""

    def __init__(self):
        self._contract_cache: dict[str, dict] = {}
        self._expense_cache: dict[str, dict] = {}
        self._last_updated = None
        self._api_client: TransparencyAPIClient | None = None

    async def _get_api_client(self) -> TransparencyAPIClient:
        """Get or create API client instance."""
        if self._api_client is None:
            self._api_client = TransparencyAPIClient()
        return self._api_client

    async def fetch_contracts(self, filters: dict | None = None) -> list[dict]:
        """
        Fetch government contracts data from Portal da Transparência.

        Args:
            filters: Filter parameters (ano, mes, codigo_orgao, etc.)

        Returns:
            List of contracts
        """
        try:
            client = await self._get_api_client()

            # Convert dict filters to TransparencyAPIFilter if provided
            api_filter = None
            if filters:
                api_filter = TransparencyAPIFilter(**filters)

            response = await client.get_contracts(api_filter)

            # Update internal cache with fetched contracts
            for contract in response.data:
                # Generate cache key from contract data
                contract_id = self._generate_contract_id(contract)
                self._contract_cache[contract_id] = contract

            logger.info(
                "contracts_fetched",
                count=len(response.data),
                cached=len(self._contract_cache),
            )

            return response.data

        except Exception as e:
            logger.error("fetch_contracts_failed", error=str(e))
            return []

    async def get_contract(self, contract_id: str) -> dict | None:
        """
        Get a specific contract by ID.

        Since Portal da Transparência doesn't have a direct get-by-id endpoint,
        this method uses a smart caching strategy:
        1. Check internal cache first
        2. If not found, fetch recent contracts and populate cache
        3. Return contract if found

        Args:
            contract_id: Contract identifier

        Returns:
            Contract data or None if not found
        """
        # Check cache first
        if contract_id in self._contract_cache:
            logger.info("contract_cache_hit", contract_id=contract_id)
            return self._contract_cache[contract_id]

        # If not in cache, fetch recent contracts to populate cache
        try:
            logger.info(
                "contract_cache_miss_fetching_recent",
                contract_id=contract_id,
            )

            # Fetch recent contracts (current year)
            current_year = datetime.now().year

            # Use a diverse set of organizations for better coverage
            # Pick based on contract_id hash for consistency
            org_codes = ["26000", "25000", "36000", "57000", "44000", "20000"]
            org_index = hash(contract_id) % len(org_codes)
            selected_org = org_codes[org_index]

            await self.fetch_contracts(
                {
                    "ano": current_year,
                    "tamanho_pagina": 100,
                    "codigo_orgao": selected_org,  # Organization based on contract_id
                }
            )

            # Check cache again
            if contract_id in self._contract_cache:
                logger.info("contract_found_after_fetch", contract_id=contract_id)
                return self._contract_cache[contract_id]

            logger.warning("contract_not_found", contract_id=contract_id)
            return None

        except Exception as e:
            logger.error(
                "get_contract_failed",
                contract_id=contract_id,
                error=str(e),
            )
            return None

    def _generate_contract_id(self, contract: dict) -> str:
        """
        Generate a unique contract ID from contract data.

        Uses combination of available fields to create unique identifier.
        """
        # Try to use official ID fields first
        if "id" in contract:
            return str(contract["id"])
        if "numero_contrato" in contract:
            return str(contract["numero_contrato"])
        if "numeroContrato" in contract:
            return str(contract["numeroContrato"])

        # Fallback: generate from combination of fields
        parts = []
        for field in ["codigoOrgao", "ano", "numero"]:
            if field in contract:
                parts.append(str(contract[field]))

        if parts:
            return "-".join(parts)

        # Last resort: use hash of contract data
        import hashlib
        import json

        contract_str = json.dumps(contract, sort_keys=True)
        return hashlib.md5(contract_str.encode()).hexdigest()[:12]

    async def get_recent_contract_ids(self, limit: int = 20) -> list[str]:
        """
        Get IDs of recent contracts for cache warming.

        Args:
            limit: Maximum number of contract IDs to return

        Returns:
            List of contract IDs
        """
        try:
            # Fetch recent contracts if cache is empty or small
            if len(self._contract_cache) < limit:
                current_year = datetime.now().year

                # Rotate through important government organizations
                # This provides diverse data for cache warming
                org_codes = [
                    "26000",  # Ministério da Saúde
                    "25000",  # Ministério da Educação
                    "36000",  # Ministério da Defesa
                    "57000",  # Ministério dos Transportes
                    "44000",  # Ministério do Meio Ambiente
                    "20000",  # Presidência da República
                    "30000",  # Ministério da Justiça
                    "39000",  # Ministério da Fazenda
                    "22000",  # Ministério da Agricultura
                    "42000",  # Ministério da Cultura
                ]

                # Rotate through organizations using hash of current time
                import hashlib

                time_hash = int(
                    hashlib.md5(str(datetime.now().hour).encode()).hexdigest()[:8], 16
                )
                selected_org = org_codes[time_hash % len(org_codes)]

                logger.info(
                    "cache_warming_org_selected",
                    codigo_orgao=selected_org,
                    org_index=time_hash % len(org_codes),
                )

                await self.fetch_contracts(
                    {
                        "ano": current_year,
                        "tamanho_pagina": limit,
                        "codigo_orgao": selected_org,  # Rotating organization
                    }
                )

            # Return IDs from cache
            contract_ids = list(self._contract_cache.keys())[:limit]
            logger.info("recent_contract_ids_retrieved", count=len(contract_ids))
            return contract_ids

        except Exception as e:
            logger.error("get_recent_contract_ids_failed", error=str(e))
            return []

    async def fetch_expenses(self, filters: dict | None = None) -> list[dict]:
        """Fetch government expenses data."""
        try:
            client = await self._get_api_client()
            api_filter = TransparencyAPIFilter(**filters) if filters else None
            response = await client.get_expenses(api_filter)
            return response.data
        except Exception as e:
            logger.error("fetch_expenses_failed", error=str(e))
            return []

    async def fetch_agreements(self, filters: dict | None = None) -> list[dict]:
        """Fetch government agreements data."""
        try:
            client = await self._get_api_client()
            api_filter = TransparencyAPIFilter(**filters) if filters else None
            response = await client.get_agreements(api_filter)
            return response.data
        except Exception as e:
            logger.error("fetch_agreements_failed", error=str(e))
            return []

    async def search_entities(self, query: str) -> list[dict]:
        """Search for government entities."""
        # TODO: Implement entity search when endpoint is available
        return []

    async def get_data_summary(self, data_type: str) -> dict:
        """Get summary statistics for data type."""
        return {
            "type": data_type,
            "total_records": 0,
            "last_updated": self._last_updated,
            "status": "implemented" if data_type == "contracts" else "stub",
            "cached_contracts": len(self._contract_cache),
        }

    def clear_cache(self) -> None:
        """Clear service cache."""
        self._contract_cache.clear()
        self._expense_cache.clear()
        self._last_updated = datetime.now()
        logger.info("data_service_cache_cleared")

    # Multi-Source Query Methods (using Orchestrator)

    async def get_contracts_multi_source(
        self,
        filters: dict | None = None,
        strategy: QueryStrategy = QueryStrategy.FALLBACK,
        sources: list[DataSource] | None = None,
    ) -> dict[str, Any]:
        """
        Get contracts from multiple sources using orchestrator.

        This method provides access to all available government data sources
        with intelligent routing and fallback strategies.

        Args:
            filters: Query filters (ano, estado, valor, etc.)
            strategy: Execution strategy (FALLBACK, AGGREGATE, FASTEST, PARALLEL)
            sources: Specific sources to query (auto-selected if None)

        Returns:
            Dict with data, sources used, and metadata

        Examples:
            # Get contracts with automatic fallback
            result = await data_service.get_contracts_multi_source(
                filters={"ano": 2024, "estado": "MG"}
            )

            # Aggregate from all sources
            result = await data_service.get_contracts_multi_source(
                filters={"ano": 2024"},
                strategy=QueryStrategy.AGGREGATE
            )

            # Query specific sources only
            result = await data_service.get_contracts_multi_source(
                filters={"ano": 2024"},
                sources=[DataSource.PORTAL_FEDERAL, DataSource.PNCP]
            )
        """
        return await orchestrator.get_contracts(
            filters=filters,
            strategy=strategy,
            sources=sources,
        )

    async def get_state_contracts(
        self,
        state_code: str,
        filters: dict | None = None,
        include_federal: bool = True,
    ) -> dict[str, Any]:
        """
        Get contracts for a specific state from all available sources.

        Automatically queries:
        1. State TCE (if available)
        2. State Portal (if available)
        3. Federal Portal with state filter (if include_federal=True)

        Args:
            state_code: Two-letter state code (MG, SP, RJ, etc.)
            filters: Additional filters
            include_federal: Include federal portal with state filter

        Returns:
            Aggregated results from all state sources
        """
        # Add state to filters
        if filters is None:
            filters = {}
        filters["estado"] = state_code.upper()

        # Auto-select state sources
        sources = [DataSource.TCE, DataSource.STATE_PORTAL]
        if include_federal:
            sources.append(DataSource.PORTAL_FEDERAL)

        return await orchestrator.get_contracts(
            filters=filters,
            strategy=QueryStrategy.AGGREGATE,
            sources=sources,
        )

    async def search_contracts_fastest(
        self,
        filters: dict | None = None,
    ) -> dict[str, Any]:
        """
        Get contracts using fastest-first strategy.

        Returns as soon as first source responds successfully.
        Useful for quick lookups when any source is acceptable.

        Args:
            filters: Query filters

        Returns:
            First successful result
        """
        return await orchestrator.get_contracts(
            filters=filters,
            strategy=QueryStrategy.FASTEST,
        )

    def get_orchestrator_stats(self) -> dict[str, Any]:
        """
        Get orchestrator statistics.

        Returns:
            Performance metrics and source usage statistics
        """
        return orchestrator.get_statistics()

    async def close(self) -> None:
        """Close API client connections."""
        if self._api_client:
            await self._api_client.close()
            logger.info("api_client_closed")


# Create singleton instance
data_service = DataService()
