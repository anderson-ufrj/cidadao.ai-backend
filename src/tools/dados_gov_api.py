"""
Dados.gov.br API Client

This module provides integration with the Brazilian Open Data Portal (dados.gov.br).
It handles authentication, rate limiting, error handling, and data parsing.
"""

import asyncio
import logging
from typing import Any, Optional

import httpx

from src.core.config import settings
from src.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class DadosGovAPIError(ExternalServiceError):
    """Custom exception for Dados.gov.br API errors"""

    pass


class DadosGovAPIClient:
    """
    Client for interacting with the Dados.gov.br API.

    This client provides methods to search and retrieve open government data
    from the Brazilian Open Data Portal.
    """

    BASE_URL = "https://dados.gov.br/api/v2"
    TIMEOUT = 30.0
    MAX_RETRIES = 3
    RATE_LIMIT_CALLS = 100  # Estimated, adjust based on API documentation
    RATE_LIMIT_PERIOD = 60  # seconds

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Dados.gov.br API client.

        Args:
            api_key: Optional API key for authentication (if required)
        """
        self.api_key = api_key or getattr(settings, "dados_gov_api_key", None)
        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limit_semaphore = asyncio.Semaphore(self.RATE_LIMIT_CALLS)
        self._last_request_time = 0

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client instance"""
        if self._client is None:
            headers = {
                "User-Agent": "Cidadao.AI/1.0 (https://github.com/cidadao-ai)",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            # Add API key if available
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers=headers,
                timeout=httpx.Timeout(self.TIMEOUT),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client

    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the API with retry logic and rate limiting.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json: JSON body data

        Returns:
            JSON response data

        Raises:
            DadosGovAPIError: On API errors
        """
        client = await self._get_client()
        url = endpoint.lstrip("/")

        # Rate limiting
        async with self._rate_limit_semaphore:
            for attempt in range(self.MAX_RETRIES):
                try:
                    logger.debug(f"Making {method} request to {url}")
                    response = await client.request(
                        method,
                        url,
                        params=params,
                        json=json,
                    )

                    # Handle different status codes
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 401:
                        raise DadosGovAPIError(
                            "Authentication failed. Please check your API key.",
                            details={"status_code": 401},
                        )
                    elif response.status_code == 403:
                        raise DadosGovAPIError(
                            "Access forbidden. You may need additional permissions.",
                            details={"status_code": 403},
                        )
                    elif response.status_code == 404:
                        raise DadosGovAPIError(
                            f"Resource not found: {url}",
                            details={"status_code": 404},
                        )
                    elif response.status_code == 429:
                        # Rate limit exceeded, wait and retry
                        retry_after = int(response.headers.get("Retry-After", "60"))
                        logger.warning(
                            f"Rate limit exceeded. Waiting {retry_after}s..."
                        )
                        await asyncio.sleep(retry_after)
                        continue
                    else:
                        response.raise_for_status()

                except httpx.HTTPError as e:
                    logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
                    if attempt == self.MAX_RETRIES - 1:
                        raise DadosGovAPIError(
                            f"Failed to connect to Dados.gov.br API: {str(e)}",
                            details={
                                "original_error": str(e),
                                "error_type": type(e).__name__,
                            },
                        )
                    await asyncio.sleep(2**attempt)  # Exponential backoff

    async def search_datasets(
        self,
        query: Optional[str] = None,
        organization: Optional[str] = None,
        tags: Optional[list[str]] = None,
        format: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Search for datasets in the open data portal.

        Args:
            query: Search query string
            organization: Filter by organization
            tags: Filter by tags
            format: Filter by data format (csv, json, xml, etc.)
            limit: Number of results per page
            offset: Pagination offset

        Returns:
            Search results with datasets
        """
        params = {
            "rows": limit,
            "start": offset,
        }

        if query:
            params["q"] = query
        if organization:
            params["fq"] = f"organization:{organization}"
        if tags:
            params["tags"] = ",".join(tags)
        if format:
            params["res_format"] = format

        return await self._make_request("GET", "/package_search", params=params)

    async def get_dataset(self, dataset_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific dataset.

        Args:
            dataset_id: The dataset identifier

        Returns:
            Dataset details including resources
        """
        params = {"id": dataset_id}
        return await self._make_request("GET", "/package_show", params=params)

    async def get_resource(self, resource_id: str) -> dict[str, Any]:
        """
        Get information about a specific resource within a dataset.

        Args:
            resource_id: The resource identifier

        Returns:
            Resource details
        """
        params = {"id": resource_id}
        return await self._make_request("GET", "/resource_show", params=params)

    async def list_organizations(self, limit: int = 100) -> dict[str, Any]:
        """
        List all organizations that publish data.

        Args:
            limit: Maximum number of organizations to return

        Returns:
            List of organizations
        """
        params = {"all_fields": True, "limit": limit}
        return await self._make_request("GET", "/organization_list", params=params)

    async def get_organization(self, org_id: str) -> dict[str, Any]:
        """
        Get detailed information about an organization.

        Args:
            org_id: The organization identifier

        Returns:
            Organization details including datasets
        """
        params = {"id": org_id, "include_datasets": True}
        return await self._make_request("GET", "/organization_show", params=params)

    async def list_tags(self) -> dict[str, Any]:
        """
        List all available tags in the portal.

        Returns:
            List of tags with usage counts
        """
        return await self._make_request("GET", "/tag_list", params={"all_fields": True})

    async def search_resources(
        self,
        query: Optional[str] = None,
        format: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Search for specific resources across all datasets.

        Args:
            query: Search query for resource names/descriptions
            format: Filter by resource format
            limit: Number of results per page
            offset: Pagination offset

        Returns:
            Search results with resources
        """
        params = {
            "query": query or "*:*",
            "limit": limit,
            "offset": offset,
        }

        if format:
            params["format"] = format

        return await self._make_request("GET", "/resource_search", params=params)
