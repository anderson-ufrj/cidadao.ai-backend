"""
TCE Rio de Janeiro API Client

API client for Rio de Janeiro State Audit Court (Tribunal de Contas do Estado).
TCE-RJ provides fiscal oversight data for Rio de Janeiro state and municipalities.

API Base: https://www.tcerj.tc.br/portaldados/api
Formats: JSON
Schema: RESTful endpoints with query parameters

Available endpoints:
- /contratos: Contracts
- /licitacoes: Bidding processes
- /despesas: Expenses
- /receitas: Revenue
- /fornecedores: Suppliers

Note: TCE-RJ uses RESTful API with standard HTTP methods.

Author: Anderson Henrique da Silva
Created: 2025-10-09 14:45:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

from typing import Any, Optional

from ..base import TransparencyAPIClient


class TCERioDeJaneiroClient(TransparencyAPIClient):
    """
    API client for TCE Rio de Janeiro (Tribunal de Contas do Estado do Rio de Janeiro).

    Examples:
        >>> client = TCERioDeJaneiroClient()
        >>> contracts = await client.get_contracts(year=2024)
        >>> suppliers = await client.get_suppliers()
    """

    def __init__(self):
        super().__init__(
            base_url="https://www.tcerj.tc.br/portaldados/api",
            name="TCE-RJ",
            rate_limit_per_minute=60,
            timeout=30.0,
        )

    async def test_connection(self) -> bool:
        """
        Test TCE-RJ API connectivity.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Try to fetch contracts list (limited)
            result = await self._make_request(
                method="GET", endpoint="/contratos", params={"limit": 1}
            )

            is_success = result is not None

            if is_success:
                self.logger.info("TCE-RJ connection successful")
            else:
                self.logger.warning("TCE-RJ returned empty response")

            return is_success

        except Exception as e:
            self.logger.error(f"TCE-RJ connection failed: {str(e)}")
            return False

    async def get_contracts(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        year: Optional[int] = None,
        municipality_code: Optional[str] = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get contracts from TCE-RJ.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of contract dictionaries
        """
        params = {}

        if year:
            params["ano"] = year
        if municipality_code:
            params["municipio"] = municipality_code
        if start_date:
            params["data_inicio"] = start_date
        if end_date:
            params["data_fim"] = end_date

        # Add custom filters
        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/contratos", params=params if params else None
            )

            contracts = self._normalize_contracts(raw_data)

            self.logger.info(f"Fetched {len(contracts)} contracts from TCE-RJ")

            return contracts

        except Exception as e:
            self.logger.error(f"Failed to fetch contracts: {str(e)}")
            return []

    async def get_suppliers(
        self, municipality_code: Optional[str] = None, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """
        Get suppliers (fornecedores) from TCE-RJ.

        Args:
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of supplier dictionaries
        """
        params = {}

        if municipality_code:
            params["municipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET",
                endpoint="/fornecedores",
                params=params if params else None,
            )

            suppliers = self._normalize_suppliers(raw_data)

            self.logger.info(f"Fetched {len(suppliers)} suppliers from TCE-RJ")

            return suppliers

        except Exception as e:
            self.logger.error(f"Failed to fetch suppliers: {str(e)}")
            return []

    async def get_bidding_processes(
        self,
        year: Optional[int] = None,
        municipality_code: Optional[str] = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get bidding processes (licitações) from TCE-RJ.

        Args:
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of bidding process dictionaries
        """
        params = {}

        if year:
            params["ano"] = year
        if municipality_code:
            params["municipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/licitacoes", params=params if params else None
            )

            biddings = self._normalize_bidding_processes(raw_data)

            self.logger.info(f"Fetched {len(biddings)} bidding processes from TCE-RJ")

            return biddings

        except Exception as e:
            self.logger.error(f"Failed to fetch bidding processes: {str(e)}")
            return []

    async def get_expenses(
        self,
        year: Optional[int] = None,
        municipality_code: Optional[str] = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get expenses (despesas) from TCE-RJ.

        Args:
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of expense dictionaries
        """
        params = {}

        if year:
            params["ano"] = year
        if municipality_code:
            params["municipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/despesas", params=params if params else None
            )

            expenses = self._normalize_expenses(raw_data)

            self.logger.info(f"Fetched {len(expenses)} expenses from TCE-RJ")

            return expenses

        except Exception as e:
            self.logger.error(f"Failed to fetch expenses: {str(e)}")
            return []

    async def get_revenue(
        self,
        year: Optional[int] = None,
        municipality_code: Optional[str] = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get revenue (receitas) from TCE-RJ.

        Args:
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of revenue dictionaries
        """
        params = {}

        if year:
            params["ano"] = year
        if municipality_code:
            params["municipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/receitas", params=params if params else None
            )

            revenue = self._normalize_revenue(raw_data)

            self.logger.info(f"Fetched {len(revenue)} revenue records from TCE-RJ")

            return revenue

        except Exception as e:
            self.logger.error(f"Failed to fetch revenue: {str(e)}")
            return []

    def _normalize_contracts(self, raw_data: Any) -> list[dict[str, Any]]:
        """Normalize contract data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append(
                {
                    "source": "TCE-RJ",
                    "contract_id": item.get("numero") or item.get("numeroContrato"),
                    "supplier_name": item.get("contratado") or item.get("fornecedor"),
                    "supplier_id": item.get("cpfCnpj") or item.get("documento"),
                    "value": float(
                        item.get("valor", 0) or item.get("valorContrato", 0) or 0
                    ),
                    "date": item.get("data") or item.get("dataAssinatura"),
                    "object": item.get("objeto"),
                    "status": item.get("situacao") or item.get("status"),
                    "municipality": item.get("municipio") or item.get("nomeMunicipio"),
                    "municipality_code": item.get("codigoMunicipio")
                    or item.get("ibge"),
                    "government_unit": item.get("orgao") or item.get("unidade"),
                    "raw_data": item,
                }
            )

        return normalized

    def _normalize_suppliers(self, raw_data: Any) -> list[dict[str, Any]]:
        """Normalize supplier data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append(
                {
                    "source": "TCE-RJ",
                    "supplier_id": item.get("cpfCnpj") or item.get("documento"),
                    "supplier_name": item.get("nome") or item.get("razaoSocial"),
                    "municipality": item.get("municipio"),
                    "municipality_code": item.get("codigoMunicipio")
                    or item.get("ibge"),
                    "raw_data": item,
                }
            )

        return normalized

    def _normalize_bidding_processes(self, raw_data: Any) -> list[dict[str, Any]]:
        """Normalize bidding process data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append(
                {
                    "source": "TCE-RJ",
                    "bidding_id": item.get("numero") or item.get("numeroLicitacao"),
                    "modality": item.get("modalidade"),
                    "object": item.get("objeto"),
                    "value": float(
                        item.get("valor", 0) or item.get("valorEstimado", 0) or 0
                    ),
                    "date": item.get("data") or item.get("dataAbertura"),
                    "status": item.get("situacao") or item.get("status"),
                    "municipality": item.get("municipio"),
                    "municipality_code": item.get("codigoMunicipio")
                    or item.get("ibge"),
                    "government_unit": item.get("orgao") or item.get("unidade"),
                    "raw_data": item,
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
                    "source": "TCE-RJ",
                    "expense_id": item.get("numero") or item.get("numeroEmpenho"),
                    "value": float(item.get("valor", 0) or 0),
                    "date": item.get("data") or item.get("dataEmpenho"),
                    "description": item.get("descricao") or item.get("historico"),
                    "category": item.get("categoria") or item.get("funcao"),
                    "supplier_name": item.get("favorecido") or item.get("credor"),
                    "supplier_id": item.get("cpfCnpjFavorecido")
                    or item.get("documento"),
                    "municipality": item.get("municipio"),
                    "municipality_code": item.get("codigoMunicipio")
                    or item.get("ibge"),
                    "government_unit": item.get("orgao") or item.get("unidade"),
                    "raw_data": item,
                }
            )

        return normalized

    def _normalize_revenue(self, raw_data: Any) -> list[dict[str, Any]]:
        """Normalize revenue data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append(
                {
                    "source": "TCE-RJ",
                    "revenue_id": item.get("numero") or item.get("id"),
                    "value": float(item.get("valor", 0) or 0),
                    "date": item.get("data") or item.get("dataArrecadacao"),
                    "description": item.get("descricao") or item.get("fonte"),
                    "category": item.get("categoria") or item.get("tipo"),
                    "municipality": item.get("municipio"),
                    "municipality_code": item.get("codigoMunicipio")
                    or item.get("ibge"),
                    "government_unit": item.get("orgao") or item.get("unidade"),
                    "raw_data": item,
                }
            )

        return normalized
