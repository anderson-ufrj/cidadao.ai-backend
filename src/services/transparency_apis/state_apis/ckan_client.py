"""
CKAN (Comprehensive Knowledge Archive Network) API Client

Generic client for Brazilian state portals using CKAN.
CKAN is an open-source data portal platform used by many Brazilian states.

Supported states:
- São Paulo: https://dadosabertos.sp.gov.br/
- Rio de Janeiro: https://dadosabertos.rj.gov.br/
- Rio Grande do Sul: https://dados.rs.gov.br/
- Santa Catarina: https://dados.sc.gov.br/
- Bahia: https://dados.ba.gov.br/

CKAN API v3 standard endpoints:
- /api/3/action/package_list: List all datasets
- /api/3/action/package_show: Show dataset details
- /api/3/action/datastore_search: Query datastore
- /api/3/action/resource_show: Show resource metadata

Author: Anderson Henrique da Silva
Created: 2025-10-09 14:21:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

from typing import Any, Optional

from ..base import TransparencyAPIClient


class CKANClient(TransparencyAPIClient):
    """
    Generic CKAN API client for Brazilian state portals.

    CKAN is used by multiple Brazilian states for open data.
    This client provides a unified interface to access their data.

    Examples:
        >>> client = CKANClient("https://dadosabertos.sp.gov.br", "SP")
        >>> datasets = await client.list_datasets()
        >>> len(datasets)
        523
    """

    def __init__(self, base_url: str, state_code: str, api_token: Optional[str] = None):
        """
        Initialize CKAN client for a specific state portal.

        Args:
            base_url: Base URL of the CKAN portal (e.g., https://dadosabertos.sp.gov.br)
            state_code: Two-letter state code (e.g., "SP", "RJ")
            api_token: Optional API token for authenticated requests
        """
        super().__init__(
            base_url=base_url,
            name=f"CKAN-{state_code}",
            rate_limit_per_minute=60,
            timeout=30.0,
        )

        self.state_code = state_code
        self.api_token = api_token

    async def test_connection(self) -> bool:
        """
        Test CKAN API connectivity.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Try to list datasets (should always work)
            result = await self._ckan_action("package_list", {"limit": 1})

            self.logger.info(f"CKAN {self.state_code} connection successful")
            return result.get("success", False)

        except Exception as e:
            self.logger.error(f"CKAN {self.state_code} connection failed: {str(e)}")
            return False

    async def list_datasets(self, limit: int = 100, offset: int = 0) -> list[str]:
        """
        List all dataset IDs in the portal.

        Args:
            limit: Maximum number of datasets to return
            offset: Offset for pagination

        Returns:
            List of dataset IDs
        """
        try:
            result = await self._ckan_action(
                "package_list", {"limit": limit, "offset": offset}
            )

            datasets = result.get("result", [])

            self.logger.info(
                f"Found {len(datasets)} datasets in CKAN {self.state_code}"
            )

            return datasets

        except Exception as e:
            self.logger.error(f"Failed to list datasets: {str(e)}")
            return []

    async def get_dataset(self, dataset_id: str) -> Optional[dict[str, Any]]:
        """
        Get detailed information about a dataset.

        Args:
            dataset_id: Dataset identifier

        Returns:
            Dataset metadata dict or None if not found
        """
        try:
            result = await self._ckan_action("package_show", {"id": dataset_id})

            return result.get("result")

        except Exception as e:
            self.logger.error(f"Failed to get dataset {dataset_id}: {str(e)}")
            return None

    async def search_datasets(
        self, query: str, filters: Optional[dict[str, Any]] = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        Search datasets by query.

        Args:
            query: Search query string
            filters: Optional filters (tags, organization, etc.)
            limit: Maximum results

        Returns:
            List of matching datasets
        """
        params = {"q": query, "rows": limit}

        if filters:
            # Add filters as facet queries
            for key, value in filters.items():
                params["fq"] = f"{key}:{value}"

        try:
            result = await self._ckan_action("package_search", params)

            results = result.get("result", {}).get("results", [])

            self.logger.info(
                f"Found {len(results)} datasets matching '{query}' in {self.state_code}"
            )

            return results

        except Exception as e:
            self.logger.error(f"Failed to search datasets: {str(e)}")
            return []

    async def get_contracts(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Search for contract-related datasets.

        CKAN doesn't have a standard contracts endpoint,
        so we search for datasets with contract-related keywords.

        Args:
            start_date: Start date filter (not used in CKAN search)
            end_date: End date filter (not used in CKAN search)
            **kwargs: Additional search parameters

        Returns:
            List of contract-related datasets
        """
        # Search for contract-related datasets
        contract_keywords = ["contratos", "licitações", "compras", "fornecedores"]

        all_results = []

        for keyword in contract_keywords:
            results = await self.search_datasets(
                query=keyword, limit=kwargs.get("limit", 50)
            )
            all_results.extend(results)

        # Deduplicate by ID
        seen_ids = set()
        unique_results = []

        for result in all_results:
            dataset_id = result.get("id")
            if dataset_id and dataset_id not in seen_ids:
                seen_ids.add(dataset_id)
                unique_results.append(result)

        self.logger.info(
            f"Found {len(unique_results)} contract-related datasets in {self.state_code}"
        )

        return unique_results

    async def query_datastore(
        self,
        resource_id: str,
        filters: Optional[dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Query CKAN datastore for a specific resource.

        Args:
            resource_id: Resource ID to query
            filters: SQL-like filters dict
            limit: Maximum records
            offset: Offset for pagination

        Returns:
            List of records from datastore
        """
        params = {"resource_id": resource_id, "limit": limit, "offset": offset}

        if filters:
            params["filters"] = filters

        try:
            result = await self._ckan_action("datastore_search", params)

            records = result.get("result", {}).get("records", [])

            self.logger.info(f"Fetched {len(records)} records from datastore")

            return records

        except Exception as e:
            self.logger.error(f"Failed to query datastore: {str(e)}")
            return []

    async def _ckan_action(
        self, action: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Call a CKAN API action.

        Args:
            action: CKAN action name (e.g., "package_list")
            params: Action parameters

        Returns:
            Action result dict
        """
        endpoint = f"/api/3/action/{action}"

        headers = {}
        if self.api_token:
            headers["Authorization"] = self.api_token

        return await self._make_request(
            method="GET",
            endpoint=endpoint,
            params=params,
            headers=headers if headers else None,
        )
