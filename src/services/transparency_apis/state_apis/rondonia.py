"""
Rondônia State Transparency API Client

API client for Rondônia state transparency portal.
One of the few Brazilian states with a direct REST API without authentication.

API Base: http://portaldatransparencia.ro.gov.br/DadosAbertos
Endpoints:
- /Api/ComprasMateriaisApi: Materials and purchases
- /Api/Contratos: Contracts
- /Api/Despesas: Expenses

No authentication required!

Author: Anderson Henrique da Silva
Created: 2025-10-09 14:19:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

from typing import Any

from ..base import TransparencyAPIClient


class RondoniaAPIClient(TransparencyAPIClient):
    """
    API client for Rondônia state transparency portal.

    Examples:
        >>> client = RondoniaAPIClient()
        >>> await client.test_connection()
        True
        >>> contracts = await client.get_contracts(start_date="2024-01-01")
        >>> len(contracts)
        150
    """

    def __init__(self):
        super().__init__(
            base_url="https://portaldatransparencia.ro.gov.br/DadosAbertos",  # Changed HTTP → HTTPS
            name="Rondônia-State",
            rate_limit_per_minute=60,  # Conservative rate limit
            timeout=30.0,
        )

    async def test_connection(self) -> bool:
        """
        Test API connectivity.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Try to fetch a small dataset
            await self._make_request(
                method="GET", endpoint="/Api/ComprasMateriaisApi", params={"limit": 1}
            )
            self.logger.info("Rondônia API connection successful")
            return True

        except Exception as e:
            self.logger.error(f"Rondônia API connection failed: {str(e)}")
            return False

    async def get_contracts(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get contracts from Rondônia transparency portal.

        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            **kwargs: Additional parameters (limit, offset, etc.)

        Returns:
            List of contract dictionaries with normalized fields
        """
        params = {}

        if start_date:
            params["dataInicio"] = start_date
        if end_date:
            params["dataFim"] = end_date

        # Add any additional parameters
        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/Api/Contratos", params=params
            )

            # Normalize data to common format
            contracts = self._normalize_contracts(raw_data)

            self.logger.info(
                f"Fetched {len(contracts)} contracts from Rondônia",
                start_date=start_date,
                end_date=end_date,
            )

            return contracts

        except Exception as e:
            self.logger.error(f"Failed to fetch contracts: {str(e)}")
            return []

    async def get_expenses(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get government expenses from Rondônia.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            **kwargs: Additional parameters

        Returns:
            List of expense dictionaries
        """
        params = {}

        if start_date:
            params["dataInicio"] = start_date
        if end_date:
            params["dataFim"] = end_date

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/Api/Despesas", params=params
            )

            expenses = self._normalize_expenses(raw_data)

            self.logger.info(f"Fetched {len(expenses)} expenses from Rondônia")

            return expenses

        except Exception as e:
            self.logger.error(f"Failed to fetch expenses: {str(e)}")
            return []

    async def get_purchases(
        self, limit: int = 100, offset: int = 0, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """
        Get materials and purchases data.

        Args:
            limit: Maximum number of records
            offset: Offset for pagination
            **kwargs: Additional parameters

        Returns:
            List of purchase dictionaries
        """
        params = {"limit": limit, "offset": offset}
        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/Api/ComprasMateriaisApi", params=params
            )

            purchases = self._normalize_purchases(raw_data)

            self.logger.info(f"Fetched {len(purchases)} purchases from Rondônia")

            return purchases

        except Exception as e:
            self.logger.error(f"Failed to fetch purchases: {str(e)}")
            return []

    def _normalize_contracts(self, raw_data: Any) -> list[dict[str, Any]]:
        """
        Normalize contract data to common format.

        Args:
            raw_data: Raw API response

        Returns:
            Normalized contract list
        """
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            # Map Rondônia fields to standard fields
            normalized.append(
                {
                    "source": "Rondônia-State",
                    "contract_id": item.get("numeroContrato") or item.get("id"),
                    "supplier_name": item.get("fornecedor") or item.get("contratado"),
                    "supplier_id": item.get("cnpjFornecedor") or item.get("cpfCnpj"),
                    "value": float(item.get("valor", 0) or 0),
                    "date": item.get("dataAssinatura") or item.get("data"),
                    "object": item.get("objeto"),
                    "status": item.get("situacao") or "ativo",
                    "government_unit": item.get("orgao") or "Governo de Rondônia",
                    "raw_data": item,  # Keep original for reference
                }
            )

        return normalized

    def _normalize_expenses(self, raw_data: Any) -> list[dict[str, Any]]:
        """Normalize expense data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append(
                {
                    "source": "Rondônia-State",
                    "expense_id": item.get("id") or item.get("numeroEmpenho"),
                    "value": float(item.get("valor", 0) or 0),
                    "date": item.get("data") or item.get("dataEmpenho"),
                    "description": item.get("descricao") or item.get("historico"),
                    "category": item.get("categoria") or item.get("funcao"),
                    "supplier_name": item.get("favorecido"),
                    "government_unit": item.get("orgao"),
                    "raw_data": item,
                }
            )

        return normalized

    def _normalize_purchases(self, raw_data: Any) -> list[dict[str, Any]]:
        """Normalize purchase data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append(
                {
                    "source": "Rondônia-State",
                    "purchase_id": item.get("id") or item.get("numeroCompra"),
                    "item_description": item.get("descricaoItem")
                    or item.get("material"),
                    "quantity": float(item.get("quantidade", 0) or 0),
                    "unit_price": float(item.get("valorUnitario", 0) or 0),
                    "total_value": float(item.get("valorTotal", 0) or 0),
                    "supplier_name": item.get("fornecedor"),
                    "date": item.get("data"),
                    "raw_data": item,
                }
            )

        return normalized
