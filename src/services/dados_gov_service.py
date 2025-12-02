"""
High-level service for interacting with dados.gov.br API.

This service provides business logic and data transformation
for the Brazilian Open Data Portal integration.
"""

import logging
from typing import Any

from src.services.cache_service import CacheService, CacheTTL
from src.tools.dados_gov_api import DadosGovAPIClient, DadosGovAPIError
from src.tools.dados_gov_models import (
    Dataset,
    DatasetSearchResult,
    Organization,
    Resource,
)

logger = logging.getLogger(__name__)


class DadosGovService:
    """
    Service for accessing and analyzing data from dados.gov.br.

    This service provides high-level methods for searching datasets,
    analyzing data availability, and retrieving government open data.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize the dados.gov.br service.

        Args:
            api_key: Optional API key for authentication
        """
        self.client = DadosGovAPIClient(api_key=api_key)
        self.cache = CacheService()

    async def close(self):
        """Close service connections"""
        await self.client.close()

    async def search_transparency_datasets(
        self,
        keywords: list[str] | None = None,
        organization: str | None = None,
        data_format: str | None = None,
        limit: int = 20,
    ) -> DatasetSearchResult:
        """
        Search for transparency-related datasets.

        Args:
            keywords: Keywords to search for (e.g., ["transparência", "gastos", "contratos"])
            organization: Filter by specific organization
            data_format: Preferred data format (csv, json, xml)
            limit: Maximum number of results

        Returns:
            Search results with relevant datasets
        """
        # Build search query
        query_parts = []
        if keywords:
            query_parts.extend(keywords)
        else:
            # Default transparency-related keywords
            query_parts.extend(
                [
                    "transparência",
                    "gastos públicos",
                    "contratos",
                    "licitações",
                    "servidores",
                ]
            )

        query = " OR ".join(query_parts)

        # Check cache
        cache_key = f"dados_gov:search:{query}:{organization}:{data_format}:{limit}"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return DatasetSearchResult(**cached_result)

        try:
            # Search datasets
            result = await self.client.search_datasets(
                query=query,
                organization=organization,
                format=data_format,
                limit=limit,
            )

            # Parse response
            search_result = DatasetSearchResult(
                count=result.get("count", 0),
                results=[Dataset(**ds) for ds in result.get("results", [])],
                facets=result.get("facets", {}),
                search_facets=result.get("search_facets", {}),
            )

            # Cache result
            await self.cache.set(
                cache_key,
                search_result.model_dump(),
                ttl=CacheTTL.MEDIUM.value,
            )

            return search_result

        except DadosGovAPIError as e:
            logger.error(f"Error searching datasets: {e}")
            raise

    async def get_dataset_with_resources(self, dataset_id: str) -> Dataset:
        """
        Get complete dataset information including all resources.

        Args:
            dataset_id: Dataset identifier

        Returns:
            Complete dataset with resources
        """
        # Check cache
        cache_key = f"dados_gov:dataset:{dataset_id}"
        cached_dataset = await self.cache.get(cache_key)
        if cached_dataset:
            return Dataset(**cached_dataset)

        try:
            # Get dataset details
            result = await self.client.get_dataset(dataset_id)
            dataset = Dataset(**result.get("result", {}))

            # Cache result
            await self.cache.set(
                cache_key,
                dataset.model_dump(),
                ttl=CacheTTL.LONG.value,
            )

            return dataset

        except DadosGovAPIError as e:
            logger.error(f"Error getting dataset {dataset_id}: {e}")
            raise

    async def find_government_spending_data(
        self,
        year: int | None = None,
        state: str | None = None,
        city: str | None = None,
    ) -> list[Dataset]:
        """
        Find datasets related to government spending.

        Args:
            year: Filter by specific year
            state: Filter by state (e.g., "SP", "RJ")
            city: Filter by city name

        Returns:
            List of relevant datasets
        """
        # Build search query
        query_parts = ["gastos", "despesas", "pagamentos", "execução orçamentária"]

        if year:
            query_parts.append(str(year))
        if state:
            query_parts.append(state)
        if city:
            query_parts.append(city)

        query = " ".join(query_parts)

        # Search for datasets
        result = await self.search_transparency_datasets(
            keywords=[query],
            data_format="csv",  # Prefer CSV for analysis
            limit=50,
        )

        # Filter results by relevance
        relevant_datasets = []
        for dataset in result.results:
            # Check if dataset is relevant based on title and description
            title_lower = dataset.title.lower()
            notes_lower = (dataset.notes or "").lower()

            if any(
                term in title_lower or term in notes_lower
                for term in ["gasto", "despesa", "pagamento", "execução"]
            ):
                relevant_datasets.append(dataset)

        return relevant_datasets

    async def find_procurement_data(
        self,
        organization: str | None = None,
        modality: str | None = None,
    ) -> list[Dataset]:
        """
        Find datasets related to public procurement and contracts.

        Args:
            organization: Filter by organization
            modality: Procurement modality (e.g., "pregão", "concorrência")

        Returns:
            List of procurement-related datasets
        """
        keywords = ["licitação", "contratos", "pregão", "compras públicas"]
        if modality:
            keywords.append(modality)

        result = await self.search_transparency_datasets(
            keywords=keywords,
            organization=organization,
            limit=30,
        )

        return result.results

    async def analyze_data_availability(
        self,
        topic: str,
    ) -> dict[str, Any]:
        """
        Analyze what data is available for a specific topic.

        Args:
            topic: Topic to analyze (e.g., "educação", "saúde", "segurança")

        Returns:
            Analysis of available data including formats, organizations, and coverage
        """
        # Search for topic-related datasets
        result = await self.search_transparency_datasets(
            keywords=[topic],
            limit=100,
        )

        # Analyze results
        analysis = {
            "topic": topic,
            "total_datasets": result.count,
            "analyzed_datasets": len(result.results),
            "organizations": {},
            "formats": {},
            "years_covered": set(),
            "geographic_coverage": {
                "federal": 0,
                "state": 0,
                "municipal": 0,
            },
            "update_frequency": {
                "daily": 0,
                "monthly": 0,
                "yearly": 0,
                "unknown": 0,
            },
        }

        # Process each dataset
        for dataset in result.results:
            # Count by organization
            if dataset.organization:
                org_name = dataset.organization.title
                analysis["organizations"][org_name] = (
                    analysis["organizations"].get(org_name, 0) + 1
                )

            # Count by format
            for resource in dataset.resources:
                if resource.format:
                    fmt = resource.format.upper()
                    analysis["formats"][fmt] = analysis["formats"].get(fmt, 0) + 1

            # Extract years from title/description
            import re

            text = f"{dataset.title} {dataset.notes or ''}"
            years = re.findall(r"\b(19|20)\d{2}\b", text)
            analysis["years_covered"].update(years)

            # Detect geographic coverage
            text_lower = text.lower()
            if any(term in text_lower for term in ["federal", "brasil", "nacional"]):
                analysis["geographic_coverage"]["federal"] += 1
            elif any(term in text_lower for term in ["estado", "estadual", "uf"]):
                analysis["geographic_coverage"]["state"] += 1
            elif any(
                term in text_lower for term in ["município", "municipal", "cidade"]
            ):
                analysis["geographic_coverage"]["municipal"] += 1

            # Detect update frequency
            if any(term in text_lower for term in ["diário", "diariamente"]):
                analysis["update_frequency"]["daily"] += 1
            elif any(term in text_lower for term in ["mensal", "mensalmente"]):
                analysis["update_frequency"]["monthly"] += 1
            elif any(term in text_lower for term in ["anual", "anualmente"]):
                analysis["update_frequency"]["yearly"] += 1
            else:
                analysis["update_frequency"]["unknown"] += 1

        # Convert years set to sorted list
        analysis["years_covered"] = sorted(list(analysis["years_covered"]))

        # Sort organizations by dataset count
        analysis["organizations"] = dict(
            sorted(
                analysis["organizations"].items(),
                key=lambda x: x[1],
                reverse=True,
            )[
                :10
            ]  # Top 10 organizations
        )

        return analysis

    async def get_resource_download_url(self, resource_id: str) -> str:
        """
        Get the download URL for a specific resource.

        Args:
            resource_id: Resource identifier

        Returns:
            Direct download URL
        """
        try:
            result = await self.client.get_resource(resource_id)
            resource = Resource(**result.get("result", {}))
            return resource.url
        except DadosGovAPIError as e:
            logger.error(f"Error getting resource {resource_id}: {e}")
            raise

    async def list_government_organizations(self) -> list[Organization]:
        """
        List all government organizations that publish open data.

        Returns:
            List of organizations sorted by dataset count
        """
        # Check cache
        cache_key = "dados_gov:organizations"
        cached_orgs = await self.cache.get(cache_key)
        if cached_orgs:
            return [Organization(**org) for org in cached_orgs]

        try:
            # Get organizations
            result = await self.client.list_organizations()
            organizations = [Organization(**org) for org in result.get("result", [])]

            # Sort by package count
            organizations.sort(
                key=lambda x: x.package_count or 0,
                reverse=True,
            )

            # Cache result
            await self.cache.set(
                cache_key,
                [org.model_dump() for org in organizations],
                ttl=CacheTTL.LONG.value,
            )

            return organizations

        except DadosGovAPIError as e:
            logger.error(f"Error listing organizations: {e}")
            raise
