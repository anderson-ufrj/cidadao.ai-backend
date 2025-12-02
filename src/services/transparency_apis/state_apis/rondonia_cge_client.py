"""
Rondônia CGE (Controladoria Geral do Estado) API Client

Full REST API client for Rondônia's transparency platform with 8 endpoints:
- Contracts (10,697 records)
- Agreements
- Expenses
- Budget allocation
- Blocked suppliers
- Supplier payments
- Revenue
- Public servant salaries

API Documentation: https://transparencia.api.ro.gov.br/swagger/index.html

Author: Anderson Henrique da Silva
Created: 2025-10-23
"""

from typing import Any

from ..base import TransparencyAPIClient


class RondoniaCGEClient(TransparencyAPIClient):
    """
    Client for Rondônia CGE transparency API.

    Provides access to 8 specialized endpoints with paginated responses.
    All endpoints use PageSize=100 (min and max) and Page starting from 1.

    Examples:
        >>> client = RondoniaCGEClient()
        >>> contracts = await client.get_contracts(page=1)
        >>> contracts["totalElementos"]
        10697
    """

    def __init__(self, timeout: float = 30.0):
        """
        Initialize Rondônia CGE API client.

        Args:
            timeout: Request timeout in seconds (default: 30.0)
        """
        super().__init__(
            base_url="https://transparencia.api.ro.gov.br",
            name="Rondônia-CGE",
            rate_limit_per_minute=60,
            timeout=timeout,
        )

    async def test_connection(self) -> bool:
        """
        Test API connectivity by fetching first page of contracts.

        Returns:
            True if API is accessible and returns valid data, False otherwise
        """
        try:
            result = await self.get_contracts(page=1)

            # Check if response has expected structure
            if (
                isinstance(result, dict)
                and "resultados" in result
                and "totalElementos" in result
            ):
                self.logger.info(
                    f"Rondônia CGE connection successful - {result['totalElementos']} contracts available"
                )
                return True

            return False

        except Exception as e:
            self.logger.error(f"Rondônia CGE connection failed: {str(e)}")
            return False

    async def get_contracts(
        self, page: int = 1, page_size: int = 100, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Fetch government contracts with pagination.

        Args:
            page: Page number (starting from 1)
            page_size: Records per page (must be 100)
            **kwargs: Additional query parameters

        Returns:
            Dict with structure:
            {
                "pagina": 1,
                "registrosPorPagina": 100,
                "totalElementos": 10697,
                "totalDePaginas": 107,
                "ultimaPagina": false,
                "resultados": [...]
            }

        Raises:
            Exception: If page_size != 100 or API returns error
        """
        if page_size != 100:
            raise ValueError("PageSize must be exactly 100 for Rondônia CGE API")

        return await self._make_request(
            method="GET",
            endpoint="/api/v1/contratos",
            params={"PageSize": page_size, "Page": page, **kwargs},
        )

    async def get_agreements(
        self, page: int = 1, page_size: int = 100, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Fetch government agreements (convênios) with pagination.

        Agreements include federal/state partnerships, transfers, etc.

        Args:
            page: Page number (starting from 1)
            page_size: Records per page (must be 100)
            **kwargs: Additional query parameters

        Returns:
            Paginated dict of agreements
        """
        if page_size != 100:
            raise ValueError("PageSize must be exactly 100 for Rondônia CGE API")

        return await self._make_request(
            method="GET",
            endpoint="/api/v1/convenios",
            params={"PageSize": page_size, "Page": page, **kwargs},
        )

    async def get_expenses(
        self, page: int = 1, page_size: int = 100, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Fetch government expenses with pagination.

        Includes detailed expense tracking with budget allocation.

        Args:
            page: Page number (starting from 1)
            page_size: Records per page (must be 100)
            **kwargs: Additional query parameters

        Returns:
            Paginated dict of expenses
        """
        if page_size != 100:
            raise ValueError("PageSize must be exactly 100 for Rondônia CGE API")

        return await self._make_request(
            method="GET",
            endpoint="/api/v1/despesas",
            params={"PageSize": page_size, "Page": page, **kwargs},
        )

    async def get_budget_allocation(
        self, page: int = 1, page_size: int = 100, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Fetch initial budget allocation (dotação inicial).

        Shows planned budget distribution by department.

        Args:
            page: Page number (starting from 1)
            page_size: Records per page (must be 100)
            **kwargs: Additional query parameters

        Returns:
            Paginated dict of budget allocations
        """
        if page_size != 100:
            raise ValueError("PageSize must be exactly 100 for Rondônia CGE API")

        return await self._make_request(
            method="GET",
            endpoint="/api/v1/despesas/dotacao-inicial",
            params={"PageSize": page_size, "Page": page, **kwargs},
        )

    async def get_blocked_suppliers(
        self, page: int = 1, page_size: int = 100, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Fetch list of blocked suppliers (fornecedores impedidos).

        Suppliers blocked due to fraud, sanctions, or contract violations.
        Critical data for fraud detection.

        Args:
            page: Page number (starting from 1)
            page_size: Records per page (must be 100)
            **kwargs: Additional query parameters

        Returns:
            Paginated dict of blocked suppliers with reasons
        """
        if page_size != 100:
            raise ValueError("PageSize must be exactly 100 for Rondônia CGE API")

        return await self._make_request(
            method="GET",
            endpoint="/api/v1/fornecedores-impedidos",
            params={"PageSize": page_size, "Page": page, **kwargs},
        )

    async def get_supplier_payments(
        self, page: int = 1, page_size: int = 100, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Fetch supplier payment records.

        Tracks actual payments to suppliers with dates, amounts, invoices.

        Args:
            page: Page number (starting from 1)
            page_size: Records per page (must be 100)
            **kwargs: Additional query parameters

        Returns:
            Paginated dict of payment records
        """
        if page_size != 100:
            raise ValueError("PageSize must be exactly 100 for Rondônia CGE API")

        return await self._make_request(
            method="GET",
            endpoint="/api/v1/pagamento-fornecedor",
            params={"PageSize": page_size, "Page": page, **kwargs},
        )

    async def get_revenue(
        self, page: int = 1, page_size: int = 100, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Fetch government revenue records.

        Includes taxes, federal transfers, state revenue sources.

        Args:
            page: Page number (starting from 1)
            page_size: Records per page (must be 100)
            **kwargs: Additional query parameters

        Returns:
            Paginated dict of revenue records
        """
        if page_size != 100:
            raise ValueError("PageSize must be exactly 100 for Rondônia CGE API")

        return await self._make_request(
            method="GET",
            endpoint="/api/v1/receitas",
            params={"PageSize": page_size, "Page": page, **kwargs},
        )

    async def get_public_servants(
        self, page: int = 1, page_size: int = 100, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Fetch public servant salary data.

        Transparency requirement: all public servant salaries must be disclosed.

        Args:
            page: Page number (starting from 1)
            page_size: Records per page (must be 100)
            **kwargs: Additional query parameters

        Returns:
            Paginated dict of public servant records
        """
        if page_size != 100:
            raise ValueError("PageSize must be exactly 100 for Rondônia CGE API")

        return await self._make_request(
            method="GET",
            endpoint="/api/v1/remuneracao-servidor",
            params={"PageSize": page_size, "Page": page, **kwargs},
        )

    async def get_all_pages(
        self, endpoint_method: str, max_pages: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Fetch all pages from a specific endpoint.

        WARNING: Some endpoints may have 100+ pages. Use max_pages to limit.

        Args:
            endpoint_method: Method name (e.g., "get_contracts")
            max_pages: Maximum number of pages to fetch (None = all pages)

        Returns:
            List of all records from all pages

        Example:
            >>> all_contracts = await client.get_all_pages("get_contracts", max_pages=10)
        """
        method = getattr(self, endpoint_method)
        all_results = []
        page = 1

        while True:
            response = await method(page=page)

            if not response or "resultados" not in response:
                break

            all_results.extend(response["resultados"])

            # Check if this is the last page
            if response.get("ultimaPagina", True):
                break

            # Check if we've reached max_pages
            if max_pages and page >= max_pages:
                self.logger.info(
                    f"Reached max_pages limit ({max_pages}) for {endpoint_method}"
                )
                break

            page += 1

        self.logger.info(
            f"Fetched {len(all_results)} total records from {endpoint_method}"
        )
        return all_results
