"""
Dados.gov.br tool for agent usage.

This tool allows agents to search and analyze data from the Brazilian
Open Data Portal (dados.gov.br) to enhance their investigations.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from src.services.dados_gov_service import DadosGovService
from src.tools.dados_gov_api import DadosGovAPIError

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    data: Any
    error: Optional[str] = None


class DadosGovTool:
    """
    Tool for accessing Brazilian Open Data Portal (dados.gov.br).

    This tool enables agents to search for government datasets,
    analyze data availability, and find specific types of public data.
    """

    name = "dados_gov_search"
    description = (
        "Search and analyze Brazilian government open data from dados.gov.br. "
        "Use this to find datasets about government spending, contracts, "
        "education, health, and other public data."
    )

    def __init__(self):
        """Initialize the dados.gov.br tool"""
        self.service = DadosGovService()

    async def execute(
        self,
        query: Optional[str] = None,
        action: str = "search",
        topic: Optional[str] = None,
        organization: Optional[str] = None,
        dataset_id: Optional[str] = None,
        year: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 10,
        **kwargs
    ) -> ToolResult:
        """
        Execute dados.gov.br operations.
        
        Args:
            query: Search query string
            action: Action to perform (search, analyze, get_dataset, find_spending, find_procurement)
            topic: Topic for analysis (e.g., "educação", "saúde")
            organization: Filter by organization
            dataset_id: Specific dataset ID to retrieve
            year: Filter by year
            state: Filter by state
            limit: Maximum number of results
            **kwargs: Additional parameters
            
        Returns:
            ToolResult with the operation results
        """
        try:
            if action == "search":
                return await self._search_datasets(
                    query=query,
                    organization=organization,
                    limit=limit,
                )
                
            elif action == "analyze":
                if not topic:
                    return ToolResult(
                        success=False,
                        error="Topic is required for analysis action",
                    )
                return await self._analyze_topic(topic)
                
            elif action == "get_dataset":
                if not dataset_id:
                    return ToolResult(
                        success=False,
                        error="Dataset ID is required for get_dataset action",
                    )
                return await self._get_dataset(dataset_id)
                
            elif action == "find_spending":
                return await self._find_spending_data(
                    year=year,
                    state=state,
                    limit=limit,
                )
                
            elif action == "find_procurement":
                return await self._find_procurement_data(
                    organization=organization,
                    limit=limit,
                )
                
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown action: {action}. Valid actions are: search, analyze, get_dataset, find_spending, find_procurement",
                )
                
        except DadosGovAPIError as e:
            logger.error(f"dados.gov.br API error: {e}")
            return ToolResult(
                success=False,
                error=f"API error: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Unexpected error in dados.gov.br tool: {e}")
            return ToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
            )
        finally:
            await self.service.close()
            
    async def _search_datasets(
        self,
        query: Optional[str],
        organization: Optional[str],
        limit: int,
    ) -> ToolResult:
        """Search for datasets"""
        keywords = []
        if query:
            # Split query into keywords
            keywords = [k.strip() for k in query.split(",") if k.strip()]
            
        result = await self.service.search_transparency_datasets(
            keywords=keywords if keywords else None,
            organization=organization,
            limit=limit,
        )
        
        # Format results for agent consumption
        datasets = []
        for dataset in result.results:
            dataset_info = {
                "id": dataset.id,
                "title": dataset.title,
                "organization": dataset.organization.title if dataset.organization else "Unknown",
                "description": dataset.notes[:200] + "..." if dataset.notes and len(dataset.notes) > 200 else dataset.notes,
                "resources": [
                    {
                        "name": res.name,
                        "format": res.format,
                        "url": res.url,
                    }
                    for res in dataset.resources[:3]  # Limit to first 3 resources
                ],
                "tags": [tag.name for tag in dataset.tags],
            }
            datasets.append(dataset_info)
            
        return ToolResult(
            success=True,
            data={
                "total_results": result.count,
                "datasets": datasets,
                "query": query,
                "organization": organization,
            },
        )
        
    async def _analyze_topic(self, topic: str) -> ToolResult:
        """Analyze data availability for a topic"""
        analysis = await self.service.analyze_data_availability(topic)
        
        # Summarize key findings
        summary = {
            "topic": topic,
            "total_datasets": analysis["total_datasets"],
            "top_organizations": dict(list(analysis["organizations"].items())[:5]),
            "available_formats": list(analysis["formats"].keys()),
            "years_covered": analysis["years_covered"],
            "coverage": {
                "federal": f"{analysis['geographic_coverage']['federal']} datasets",
                "state": f"{analysis['geographic_coverage']['state']} datasets",
                "municipal": f"{analysis['geographic_coverage']['municipal']} datasets",
            },
            "update_frequency": analysis["update_frequency"],
        }
        
        return ToolResult(
            success=True,
            data=summary,
        )
        
    async def _get_dataset(self, dataset_id: str) -> ToolResult:
        """Get detailed dataset information"""
        dataset = await self.service.get_dataset_with_resources(dataset_id)
        
        # Format dataset details
        details = {
            "id": dataset.id,
            "title": dataset.title,
            "organization": dataset.organization.title if dataset.organization else "Unknown",
            "description": dataset.notes,
            "license": dataset.license_id,
            "author": dataset.author,
            "maintainer": dataset.maintainer,
            "created": dataset.metadata_created.isoformat() if dataset.metadata_created else None,
            "modified": dataset.metadata_modified.isoformat() if dataset.metadata_modified else None,
            "resources": [
                {
                    "id": res.id,
                    "name": res.name,
                    "description": res.description,
                    "format": res.format,
                    "url": res.url,
                    "size": res.size,
                    "last_modified": res.last_modified.isoformat() if res.last_modified else None,
                }
                for res in dataset.resources
            ],
            "tags": [tag.name for tag in dataset.tags],
        }
        
        return ToolResult(
            success=True,
            data=details,
        )
        
    async def _find_spending_data(
        self,
        year: Optional[int],
        state: Optional[str],
        limit: int,
    ) -> ToolResult:
        """Find government spending datasets"""
        datasets = await self.service.find_government_spending_data(
            year=year,
            state=state,
        )
        
        # Format spending datasets
        spending_data = []
        for dataset in datasets[:limit]:
            spending_data.append({
                "id": dataset.id,
                "title": dataset.title,
                "organization": dataset.organization.title if dataset.organization else "Unknown",
                "description": dataset.notes[:200] + "..." if dataset.notes and len(dataset.notes) > 200 else dataset.notes,
                "resources_count": len(dataset.resources),
                "formats": list(set(res.format for res in dataset.resources if res.format)),
            })
            
        return ToolResult(
            success=True,
            data={
                "total_found": len(datasets),
                "datasets": spending_data,
                "filters": {
                    "year": year,
                    "state": state,
                },
            },
        )
        
    async def _find_procurement_data(
        self,
        organization: Optional[str],
        limit: int,
    ) -> ToolResult:
        """Find procurement/contract datasets"""
        datasets = await self.service.find_procurement_data(
            organization=organization,
        )
        
        # Format procurement datasets
        procurement_data = []
        for dataset in datasets[:limit]:
            procurement_data.append({
                "id": dataset.id,
                "title": dataset.title,
                "organization": dataset.organization.title if dataset.organization else "Unknown",
                "description": dataset.notes[:200] + "..." if dataset.notes and len(dataset.notes) > 200 else dataset.notes,
                "resources_count": len(dataset.resources),
                "formats": list(set(res.format for res in dataset.resources if res.format)),
            })
            
        return ToolResult(
            success=True,
            data={
                "total_found": len(datasets),
                "datasets": procurement_data,
                "organization_filter": organization,
            },
        )
        
    def get_usage_instructions(self) -> str:
        """Get usage instructions for agents"""
        return """
        Dados.gov.br Tool Usage:
        
        1. Search datasets:
           - action: "search"
           - query: "educação básica, censo escolar"
           - organization: "inep" (optional)
           - limit: 10
           
        2. Analyze topic availability:
           - action: "analyze"
           - topic: "saúde"
           
        3. Get dataset details:
           - action: "get_dataset"
           - dataset_id: "dataset-uuid-here"
           
        4. Find government spending data:
           - action: "find_spending"
           - year: 2023 (optional)
           - state: "SP" (optional)
           
        5. Find procurement/contract data:
           - action: "find_procurement"
           - organization: "ministério-da-saúde" (optional)
           
        Examples:
        - To find education datasets: {"action": "search", "query": "educação"}
        - To analyze health data availability: {"action": "analyze", "topic": "saúde"}
        - To find 2023 spending in São Paulo: {"action": "find_spending", "year": 2023, "state": "SP"}
        """