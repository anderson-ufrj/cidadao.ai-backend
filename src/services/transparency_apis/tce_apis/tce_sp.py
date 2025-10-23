"""
TCE São Paulo API Client

API client for São Paulo State Audit Court (Tribunal de Contas do Estado).
TCE-SP provides fiscal oversight data for São Paulo state municipalities.

API Base: https://transparencia.tce.sp.gov.br/api
Formats: JSON
Schema: RESTful API with query parameters

Available endpoints:
- /contratos: Contracts and agreements
- /despesas: Expenses and commitments
- /licitacoes: Bidding processes
- /fornecedores: Suppliers/contractors
- /orgaos: Government entities
- /municipios: Municipality list

Note: TCE-SP covers 645 municipalities in São Paulo state.

Author: Anderson Henrique da Silva
Created: 2025-10-09 14:50:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

from typing import Any, Optional

from ..base import TransparencyAPIClient


class TCESaoPauloClient(TransparencyAPIClient):
    """
    API client for TCE São Paulo (Tribunal de Contas do Estado de São Paulo).

    Provides access to fiscal data for 645 municipalities in São Paulo state.

    Examples:
        >>> client = TCESaoPauloClient()
        >>> contracts = await client.get_contracts(year=2024)
        >>> municipalities = await client.get_municipalities()
    """

    def __init__(self):
        super().__init__(
            base_url="https://transparencia.tce.sp.gov.br/api",
            name="TCE-SP",
            rate_limit_per_minute=60,
            timeout=30.0,
        )

    async def test_connection(self) -> bool:
        """
        Test TCE-SP API connectivity.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # TCE-SP requires format in path: /json/municipios or /xml/municipios
            result = await self._make_request(
                method="GET", endpoint="/json/municipios", params=None
            )

            is_success = result is not None and isinstance(result, list)

            if is_success:
                self.logger.info("TCE-SP connection successful")
            else:
                self.logger.warning("TCE-SP returned empty response")

            return is_success

        except Exception as e:
            self.logger.error(f"TCE-SP connection failed: {str(e)}")
            return False

    async def get_municipalities(self) -> list[dict[str, Any]]:
        """
        Get list of São Paulo municipalities.

        Returns:
            List of municipality dictionaries with IBGE codes
        """
        try:
            # TCE-SP requires format in path: /json/municipios
            raw_data = await self._make_request(
                method="GET", endpoint="/json/municipios", params=None
            )

            municipalities = self._normalize_municipalities(raw_data)

            self.logger.info(
                f"Fetched {len(municipalities)} municipalities from TCE-SP"
            )

            return municipalities

        except Exception as e:
            self.logger.error(f"Failed to fetch municipalities: {str(e)}")
            return []

    async def get_contracts(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        year: Optional[int] = None,
        municipality_code: Optional[str] = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get contracts from TCE-SP.

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
            params["ano_exercicio"] = year
        if municipality_code:
            params["cd_municipio"] = municipality_code
        if start_date:
            params["dt_inicio"] = start_date
        if end_date:
            params["dt_fim"] = end_date

        # Add custom filters
        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/contratos", params=params if params else None
            )

            contracts = self._normalize_contracts(raw_data)

            self.logger.info(f"Fetched {len(contracts)} contracts from TCE-SP")

            return contracts

        except Exception as e:
            self.logger.error(f"Failed to fetch contracts: {str(e)}")
            return []

    async def get_suppliers(
        self, municipality_code: Optional[str] = None, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """
        Get suppliers (fornecedores) from TCE-SP.

        Args:
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of supplier dictionaries
        """
        params = {}

        if municipality_code:
            params["cd_municipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET",
                endpoint="/fornecedores",
                params=params if params else None,
            )

            suppliers = self._normalize_suppliers(raw_data)

            self.logger.info(f"Fetched {len(suppliers)} suppliers from TCE-SP")

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
        Get bidding processes (licitações) from TCE-SP.

        Args:
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of bidding process dictionaries
        """
        params = {}

        if year:
            params["ano_exercicio"] = year
        if municipality_code:
            params["cd_municipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/licitacoes", params=params if params else None
            )

            biddings = self._normalize_bidding_processes(raw_data)

            self.logger.info(f"Fetched {len(biddings)} bidding processes from TCE-SP")

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
        Get expenses (despesas) from TCE-SP.

        Args:
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of expense dictionaries
        """
        params = {}

        if year:
            params["ano_exercicio"] = year
        if municipality_code:
            params["cd_municipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/despesas", params=params if params else None
            )

            expenses = self._normalize_expenses(raw_data)

            self.logger.info(f"Fetched {len(expenses)} expenses from TCE-SP")

            return expenses

        except Exception as e:
            self.logger.error(f"Failed to fetch expenses: {str(e)}")
            return []

    async def get_government_entities(
        self, municipality_code: Optional[str] = None, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """
        Get government entities (órgãos) from TCE-SP.

        Args:
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of government entity dictionaries
        """
        params = {}

        if municipality_code:
            params["cd_municipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/orgaos", params=params if params else None
            )

            entities = self._normalize_government_entities(raw_data)

            self.logger.info(f"Fetched {len(entities)} government entities from TCE-SP")

            return entities

        except Exception as e:
            self.logger.error(f"Failed to fetch government entities: {str(e)}")
            return []

    def _normalize_municipalities(self, raw_data: Any) -> list[dict[str, Any]]:
        """Normalize municipality data."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append(
                {
                    "source": "TCE-SP",
                    "municipality_code": item.get("cd_municipio")
                    or item.get("codigo_ibge"),
                    "municipality_name": item.get("nm_municipio") or item.get("nome"),
                    "state": "SP",
                    "raw_data": item,
                }
            )

        return normalized

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
                    "source": "TCE-SP",
                    "contract_id": item.get("nr_contrato") or item.get("numero"),
                    "supplier_name": item.get("nm_contratado")
                    or item.get("fornecedor"),
                    "supplier_id": item.get("nr_cpf_cnpj") or item.get("documento"),
                    "value": float(item.get("vl_contrato", 0) or 0),
                    "date": item.get("dt_assinatura") or item.get("data"),
                    "object": item.get("ds_objeto") or item.get("objeto"),
                    "status": item.get("tp_situacao") or item.get("situacao"),
                    "municipality": item.get("nm_municipio"),
                    "municipality_code": item.get("cd_municipio"),
                    "government_unit": item.get("nm_orgao") or item.get("orgao"),
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
                    "source": "TCE-SP",
                    "supplier_id": item.get("nr_cpf_cnpj") or item.get("documento"),
                    "supplier_name": item.get("nm_fornecedor") or item.get("nome"),
                    "municipality": item.get("nm_municipio"),
                    "municipality_code": item.get("cd_municipio"),
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
                    "source": "TCE-SP",
                    "bidding_id": item.get("nr_licitacao") or item.get("numero"),
                    "modality": item.get("tp_modalidade") or item.get("modalidade"),
                    "object": item.get("ds_objeto") or item.get("objeto"),
                    "value": float(item.get("vl_estimado", 0) or 0),
                    "date": item.get("dt_abertura") or item.get("data"),
                    "status": item.get("tp_situacao") or item.get("situacao"),
                    "municipality": item.get("nm_municipio"),
                    "municipality_code": item.get("cd_municipio"),
                    "government_unit": item.get("nm_orgao") or item.get("orgao"),
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
                    "source": "TCE-SP",
                    "expense_id": item.get("nr_empenho") or item.get("numero"),
                    "value": float(item.get("vl_empenho", 0) or 0),
                    "date": item.get("dt_empenho") or item.get("data"),
                    "description": item.get("ds_historico") or item.get("descricao"),
                    "category": item.get("ds_funcao") or item.get("categoria"),
                    "supplier_name": item.get("nm_favorecido")
                    or item.get("fornecedor"),
                    "supplier_id": item.get("nr_cpf_cnpj") or item.get("documento"),
                    "municipality": item.get("nm_municipio"),
                    "municipality_code": item.get("cd_municipio"),
                    "government_unit": item.get("nm_orgao") or item.get("orgao"),
                    "raw_data": item,
                }
            )

        return normalized

    def _normalize_government_entities(self, raw_data: Any) -> list[dict[str, Any]]:
        """Normalize government entity data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append(
                {
                    "source": "TCE-SP",
                    "entity_code": item.get("cd_orgao") or item.get("codigo"),
                    "entity_name": item.get("nm_orgao") or item.get("nome"),
                    "entity_type": item.get("tp_orgao") or item.get("tipo"),
                    "municipality": item.get("nm_municipio"),
                    "municipality_code": item.get("cd_municipio"),
                    "raw_data": item,
                }
            )

        return normalized
