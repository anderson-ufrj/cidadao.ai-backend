"""
TCE Pernambuco API Client

API client for Pernambuco State Audit Court (Tribunal de Contas do Estado).
TCE-PE provides fiscal oversight data for Pernambuco state and municipalities.

API Base: https://sistemas.tce.pe.gov.br/DadosAbertos/
Formats: XML, JSON, HTML
Schema: https://sistemas.tce.pe.gov.br/DadosAbertos/<Entidade>!<formato>?<filtros>

Endpoints:
- Fornecedores: Suppliers data
- Licitacoes: Bidding processes
- Contratos: Contracts
- Folha: Payroll
- Receitas: Revenue
- Despesas: Expenses

Note: HTTP 200 always returned (error in body if request fails)

Author: Anderson Henrique da Silva
Created: 2025-10-09 14:23:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

from typing import Any

from ..base import TransparencyAPIClient


class TCEPernambucoClient(TransparencyAPIClient):
    """
    API client for TCE Pernambuco (Tribunal de Contas do Estado de Pernambuco).

    Examples:
        >>> client = TCEPernambucoClient()
        >>> contracts = await client.get_contracts(year=2024)
        >>> suppliers = await client.get_suppliers()
    """

    def __init__(self):
        super().__init__(
            base_url="https://sistemas.tce.pe.gov.br/DadosAbertos",
            name="TCE-PE",
            rate_limit_per_minute=60,  # Conservative rate limit
            timeout=30.0,
        )

    async def test_connection(self) -> bool:
        """
        Test TCE-PE API connectivity.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Try to fetch suppliers (small dataset)
            result = await self._tce_request("Fornecedores", "JSON", limit=1)

            # TCE-PE always returns 200, check for actual data
            is_success = result is not None and len(str(result)) > 10

            if is_success:
                self.logger.info("TCE-PE connection successful")
            else:
                self.logger.warning("TCE-PE returned empty response")

            return is_success

        except Exception as e:
            self.logger.error(f"TCE-PE connection failed: {str(e)}")
            return False

    async def get_contracts(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        year: int | None = None,
        municipality_code: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get contracts from TCE-PE.

        Args:
            start_date: Start date (DD/MM/YYYY format for TCE-PE)
            end_date: End date (DD/MM/YYYY format)
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of contract dictionaries
        """
        filters = {}

        if year:
            filters["ano"] = year
        if municipality_code:
            filters["codigoMunicipio"] = municipality_code

        # Add custom filters
        filters.update(kwargs)

        try:
            raw_data = await self._tce_request("Contratos", "JSON", **filters)

            contracts = self._normalize_contracts(raw_data)

            self.logger.info(f"Fetched {len(contracts)} contracts from TCE-PE")

            return contracts

        except Exception as e:
            self.logger.error(f"Failed to fetch contracts: {str(e)}")
            return []

    async def get_suppliers(
        self, municipality_code: str | None = None, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """
        Get suppliers (fornecedores) from TCE-PE.

        Args:
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of supplier dictionaries
        """
        filters = {}

        if municipality_code:
            filters["codigoMunicipio"] = municipality_code

        filters.update(kwargs)

        try:
            raw_data = await self._tce_request("Fornecedores", "JSON", **filters)

            suppliers = self._normalize_suppliers(raw_data)

            self.logger.info(f"Fetched {len(suppliers)} suppliers from TCE-PE")

            return suppliers

        except Exception as e:
            self.logger.error(f"Failed to fetch suppliers: {str(e)}")
            return []

    async def get_bidding_processes(
        self,
        year: int | None = None,
        municipality_code: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get bidding processes (licitações) from TCE-PE.

        Args:
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of bidding process dictionaries
        """
        filters = {}

        if year:
            filters["ano"] = year
        if municipality_code:
            filters["codigoMunicipio"] = municipality_code

        filters.update(kwargs)

        try:
            raw_data = await self._tce_request("Licitacoes", "JSON", **filters)

            biddings = self._normalize_bidding_processes(raw_data)

            self.logger.info(f"Fetched {len(biddings)} bidding processes from TCE-PE")

            return biddings

        except Exception as e:
            self.logger.error(f"Failed to fetch bidding processes: {str(e)}")
            return []

    async def get_expenses(
        self,
        year: int | None = None,
        municipality_code: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get expenses (despesas) from TCE-PE.

        Args:
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of expense dictionaries
        """
        filters = {}

        if year:
            filters["ano"] = year
        if municipality_code:
            filters["codigoMunicipio"] = municipality_code

        filters.update(kwargs)

        try:
            raw_data = await self._tce_request("Despesas", "JSON", **filters)

            expenses = self._normalize_expenses(raw_data)

            self.logger.info(f"Fetched {len(expenses)} expenses from TCE-PE")

            return expenses

        except Exception as e:
            self.logger.error(f"Failed to fetch expenses: {str(e)}")
            return []

    async def _tce_request(
        self, entity: str, format: str = "JSON", **filters: Any
    ) -> Any:
        """
        Make request to TCE-PE API.

        TCE-PE uses a specific URL schema:
        /DadosAbertos/<Entity>!<Format>?<filters>

        Args:
            entity: Entity name (Contratos, Fornecedores, etc.)
            format: Response format (JSON, XML, HTML)
            **filters: Query filters

        Returns:
            Raw API response
        """
        endpoint = f"/{entity}!{format}"

        return await self._make_request(
            method="GET", endpoint=endpoint, params=filters if filters else None
        )

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
                    "source": "TCE-PE",
                    "contract_id": item.get("numeroContrato"),
                    "supplier_name": item.get("nomeContratado"),
                    "supplier_id": item.get("cpfCnpjContratado"),
                    "value": float(item.get("valorContrato", 0) or 0),
                    "date": item.get("dataAssinatura"),
                    "object": item.get("objetoContrato"),
                    "status": item.get("situacao"),
                    "municipality": item.get("nomeMunicipio"),
                    "municipality_code": item.get("codigoMunicipio"),
                    "government_unit": item.get("nomeOrgao"),
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
                    "source": "TCE-PE",
                    "supplier_id": item.get("cpfCnpj"),
                    "supplier_name": item.get("nome"),
                    "municipality": item.get("nomeMunicipio"),
                    "municipality_code": item.get("codigoMunicipio"),
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
                    "source": "TCE-PE",
                    "bidding_id": item.get("numeroLicitacao"),
                    "modality": item.get("modalidade"),
                    "object": item.get("objeto"),
                    "value": float(item.get("valorEstimado", 0) or 0),
                    "date": item.get("dataAbertura"),
                    "status": item.get("situacao"),
                    "municipality": item.get("nomeMunicipio"),
                    "municipality_code": item.get("codigoMunicipio"),
                    "government_unit": item.get("nomeOrgao"),
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
                    "source": "TCE-PE",
                    "expense_id": item.get("numeroEmpenho"),
                    "value": float(item.get("valor", 0) or 0),
                    "date": item.get("dataEmpenho"),
                    "description": item.get("descricao") or item.get("historico"),
                    "category": item.get("funcao"),
                    "supplier_name": item.get("nomeFavorecido"),
                    "supplier_id": item.get("cpfCnpjFavorecido"),
                    "municipality": item.get("nomeMunicipio"),
                    "municipality_code": item.get("codigoMunicipio"),
                    "government_unit": item.get("nomeOrgao"),
                    "raw_data": item,
                }
            )

        return normalized
