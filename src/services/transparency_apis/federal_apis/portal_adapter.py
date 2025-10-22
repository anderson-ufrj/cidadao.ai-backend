"""
Portal da Transparência Federal Adapter

Adapts PortalTransparenciaService to work with TransparencyAPIRegistry.
Enables integration of federal government contract data into the unified
transparency data collection system.

Author: Anderson Henrique da Silva
Created: 2025-10-22
"""

from datetime import date
from typing import Any, Optional

from src.core import get_logger
from src.services.portal_transparencia_service import portal_transparencia

from ..base import TransparencyAPIClient

logger = get_logger(__name__)


class PortalTransparenciaAdapter(TransparencyAPIClient):
    """
    Adapter for Portal da Transparência Federal API.

    Bridges the PortalTransparenciaService with the TransparencyAPIRegistry
    interface, allowing federal government data to be collected alongside
    state and municipal sources.
    """

    def __init__(self):
        """Initialize Portal da Transparência adapter."""
        # Initialize parent class with Portal da Transparência details
        super().__init__(
            base_url="https://api.portaldatransparencia.gov.br",
            name="Portal da Transparência Federal",
            rate_limit_per_minute=90,  # Portal has lower rate limit
            timeout=30.0,
            max_retries=3,
        )

        self.portal_service = portal_transparencia
        self.api_type = "federal"
        self.coverage = "national"

    async def test_connection(self) -> bool:
        """
        Test if Portal da Transparência API is accessible.

        Returns:
            True if API is responding, False otherwise
        """
        try:
            # Try to fetch a single contract to test connectivity
            result = await self.portal_service.search_contracts(page=1, size=1)

            # Check if we got data (not demo mode)
            has_data = bool(result.get("contratos"))
            is_demo = result.get("demo_mode", False)

            # API is healthy if it returns data and is not in demo mode
            is_healthy = has_data and not is_demo

            logger.info(
                f"Portal da Transparência connection test: {'OK' if is_healthy else 'DEGRADED'}",
                extra={"has_data": has_data, "demo_mode": is_demo},
            )

            return is_healthy

        except Exception as e:
            logger.error(f"Portal da Transparência connection test failed: {e}")
            return False

    async def get_contracts(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        year: Optional[int] = None,
        municipality_code: Optional[str] = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """
        Get contracts from Portal da Transparência.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            year: Filter by year (converted to date range)
            municipality_code: Not used by federal API
            **kwargs: Additional parameters (orgao, cnpj_fornecedor, etc.)

        Returns:
            List of contract dictionaries
        """
        try:
            # Convert year to date range if provided
            if year and not start_date:
                start_date = f"{year}-01-01"
            if year and not end_date:
                end_date = f"{year}-12-31"

            # Convert string dates to date objects
            data_inicial = None
            data_final = None
            if start_date:
                data_inicial = date.fromisoformat(start_date)
            if end_date:
                data_final = date.fromisoformat(end_date)

            # Extract Portal-specific parameters
            orgao = kwargs.get("codigoOrgao") or kwargs.get("orgao")
            cnpj_fornecedor = kwargs.get("cnpj_fornecedor")
            valor_minimo = kwargs.get("valor_minimo")
            valor_maximo = kwargs.get("valor_maximo")

            # Call Portal service
            result = await self.portal_service.search_contracts(
                orgao=orgao,
                cnpj_fornecedor=cnpj_fornecedor,
                data_inicial=data_inicial,
                data_final=data_final,
                valor_minimo=valor_minimo,
                valor_maximo=valor_maximo,
                page=kwargs.get("page", 1),
                size=kwargs.get("size", 100),
            )

            # Return contracts list
            contracts = result.get("contratos", [])

            logger.info(
                f"Portal da Transparência returned {len(contracts)} contracts",
                extra={
                    "source": "FEDERAL-portal",
                    "count": len(contracts),
                    "demo_mode": result.get("demo_mode", False),
                },
            )

            return contracts

        except Exception as e:
            logger.error(
                f"Error fetching contracts from Portal da Transparência: {e}",
                extra={"error": str(e)},
            )
            return []

    async def get_expenses(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        year: Optional[int] = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """
        Get expenses from Portal da Transparência.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            year: Filter by year
            **kwargs: Additional parameters

        Returns:
            List of expense dictionaries
        """
        try:
            # Convert dates
            data_inicial = None
            data_final = None
            if start_date:
                data_inicial = date.fromisoformat(start_date)
            if end_date:
                data_final = date.fromisoformat(end_date)
            if year and not data_inicial:
                data_inicial = date(year, 1, 1)
            if year and not data_final:
                data_final = date(year, 12, 31)

            # Call Portal service
            result = await self.portal_service.search_expenses(
                data_inicial=data_inicial,
                data_final=data_final,
                orgao=kwargs.get("orgao"),
                page=kwargs.get("page", 1),
                size=kwargs.get("size", 100),
            )

            return result.get("despesas", [])

        except Exception as e:
            logger.error(f"Error fetching expenses from Portal: {e}")
            return []

    async def get_suppliers(
        self, cnpj: Optional[str] = None, **kwargs
    ) -> list[dict[str, Any]]:
        """
        Get suppliers/fornecedores from Portal da Transparência.

        Args:
            cnpj: Supplier CNPJ
            **kwargs: Additional parameters

        Returns:
            List of supplier dictionaries
        """
        try:
            result = await self.portal_service.search_suppliers(
                cnpj=cnpj, page=kwargs.get("page", 1), size=kwargs.get("size", 100)
            )

            return result.get("fornecedores", [])

        except Exception as e:
            logger.error(f"Error fetching suppliers from Portal: {e}")
            return []

    async def health_check(self) -> bool:
        """
        Check if Portal da Transparência API is accessible.

        Returns:
            True if API is responding, False otherwise
        """
        try:
            # Try to fetch a single contract
            result = await self.portal_service.search_contracts(page=1, size=1)

            # Check if we got data (not demo mode)
            has_data = bool(result.get("contratos"))
            is_demo = result.get("demo_mode", False)

            # API is healthy if it returns data and is not in demo mode
            is_healthy = has_data and not is_demo

            logger.info(
                f"Portal da Transparência health check: {'OK' if is_healthy else 'DEGRADED'}",
                extra={"has_data": has_data, "demo_mode": is_demo},
            )

            return is_healthy

        except Exception as e:
            logger.error(f"Portal da Transparência health check failed: {e}")
            return False

    def get_metadata(self) -> dict[str, Any]:
        """
        Get metadata about this API.

        Returns:
            Dictionary with API information
        """
        return {
            "name": self.name,
            "type": self.api_type,
            "coverage": self.coverage,
            "base_url": "https://api.portaldatransparencia.gov.br",
            "has_api_key": bool(self.portal_service.api_key),
            "endpoints": [
                "contracts",
                "expenses",
                "suppliers",
                "servants",
                "travels",
            ],
        }
