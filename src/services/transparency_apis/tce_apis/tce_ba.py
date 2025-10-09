"""
TCE Bahia API Client

API client for Bahia State Audit Court (Tribunal de Contas do Estado).
TCE-BA provides fiscal oversight data for Bahia state and municipalities.

API Base: https://sistemas.tce.ba.gov.br/egestaoapi
Formats: JSON
Schema: RESTful API with versioned endpoints

Available endpoints:
- /contratos: Contracts and agreements
- /licitacoes: Bidding processes
- /despesas: Expenses and payments
- /receitas: Revenue and income
- /fornecedores: Suppliers database
- /servidores: Public servants (when authorized)
- /municipios: Municipality list

Note: TCE-BA covers 417 municipalities in Bahia state.

Author: Anderson Henrique da Silva
Created: 2025-10-09 15:00:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

from typing import Any, Dict, List, Optional

from ..base import TransparencyAPIClient


class TCEBahiaClient(TransparencyAPIClient):
    """
    API client for TCE Bahia (Tribunal de Contas do Estado da Bahia).

    Provides access to fiscal data for 417 municipalities in Bahia state.

    Examples:
        >>> client = TCEBahiaClient()
        >>> contracts = await client.get_contracts(year=2024)
        >>> suppliers = await client.get_suppliers(municipality_code="2927408")
    """

    def __init__(self):
        super().__init__(
            base_url="https://sistemas.tce.ba.gov.br/egestaoapi",
            name="TCE-BA",
            rate_limit_per_minute=60,
            timeout=30.0
        )

    async def test_connection(self) -> bool:
        """
        Test TCE-BA API connectivity.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Try to fetch municipality list (small dataset)
            result = await self._make_request(
                method="GET",
                endpoint="/v1/municipios",
                params={"limite": 1}
            )

            is_success = result is not None

            if is_success:
                self.logger.info("TCE-BA connection successful")
            else:
                self.logger.warning("TCE-BA returned empty response")

            return is_success

        except Exception as e:
            self.logger.error(f"TCE-BA connection failed: {str(e)}")
            return False

    async def get_municipalities(self) -> List[Dict[str, Any]]:
        """
        Get list of Bahia municipalities.

        Returns:
            List of 417 municipality dictionaries with IBGE codes
        """
        try:
            raw_data = await self._make_request(
                method="GET",
                endpoint="/v1/municipios",
                params=None
            )

            municipalities = self._normalize_municipalities(raw_data)

            self.logger.info(f"Fetched {len(municipalities)} municipalities from TCE-BA")

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
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Get contracts from TCE-BA.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            year: Filter by year
            municipality_code: IBGE municipality code (e.g., "2927408" for Salvador)
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
            params["dataInicio"] = start_date
        if end_date:
            params["dataFim"] = end_date

        # Add custom filters
        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET",
                endpoint="/v1/contratos",
                params=params if params else None
            )

            contracts = self._normalize_contracts(raw_data)

            self.logger.info(f"Fetched {len(contracts)} contracts from TCE-BA")

            return contracts

        except Exception as e:
            self.logger.error(f"Failed to fetch contracts: {str(e)}")
            return []

    async def get_suppliers(
        self,
        municipality_code: Optional[str] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Get suppliers (fornecedores) from TCE-BA.

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
                endpoint="/v1/fornecedores",
                params=params if params else None
            )

            suppliers = self._normalize_suppliers(raw_data)

            self.logger.info(f"Fetched {len(suppliers)} suppliers from TCE-BA")

            return suppliers

        except Exception as e:
            self.logger.error(f"Failed to fetch suppliers: {str(e)}")
            return []

    async def get_bidding_processes(
        self,
        year: Optional[int] = None,
        municipality_code: Optional[str] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Get bidding processes (licitações) from TCE-BA.

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
                method="GET",
                endpoint="/v1/licitacoes",
                params=params if params else None
            )

            biddings = self._normalize_bidding_processes(raw_data)

            self.logger.info(f"Fetched {len(biddings)} bidding processes from TCE-BA")

            return biddings

        except Exception as e:
            self.logger.error(f"Failed to fetch bidding processes: {str(e)}")
            return []

    async def get_expenses(
        self,
        year: Optional[int] = None,
        municipality_code: Optional[str] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Get expenses (despesas) from TCE-BA.

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
                method="GET",
                endpoint="/v1/despesas",
                params=params if params else None
            )

            expenses = self._normalize_expenses(raw_data)

            self.logger.info(f"Fetched {len(expenses)} expenses from TCE-BA")

            return expenses

        except Exception as e:
            self.logger.error(f"Failed to fetch expenses: {str(e)}")
            return []

    async def get_revenue(
        self,
        year: Optional[int] = None,
        municipality_code: Optional[str] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Get revenue (receitas) from TCE-BA.

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
                method="GET",
                endpoint="/v1/receitas",
                params=params if params else None
            )

            revenue = self._normalize_revenue(raw_data)

            self.logger.info(f"Fetched {len(revenue)} revenue records from TCE-BA")

            return revenue

        except Exception as e:
            self.logger.error(f"Failed to fetch revenue: {str(e)}")
            return []

    def _normalize_municipalities(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize municipality data."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append({
                "source": "TCE-BA",
                "municipality_code": item.get("codigoIbge") or item.get("codigo"),
                "municipality_name": item.get("nome") or item.get("nomeMunicipio"),
                "state": "BA",
                "raw_data": item
            })

        return normalized

    def _normalize_contracts(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize contract data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append({
                "source": "TCE-BA",
                "contract_id": item.get("numeroContrato") or item.get("numero"),
                "supplier_name": item.get("nomeContratado") or item.get("fornecedor"),
                "supplier_id": item.get("cnpjCpfContratado") or item.get("documento"),
                "value": float(item.get("valorContrato", 0) or 0),
                "date": item.get("dataAssinatura") or item.get("data"),
                "object": item.get("objetoContrato") or item.get("objeto"),
                "status": item.get("situacao") or item.get("status"),
                "municipality": item.get("nomeMunicipio"),
                "municipality_code": item.get("codigoMunicipio"),
                "government_unit": item.get("nomeOrgao") or item.get("orgao"),
                "raw_data": item
            })

        return normalized

    def _normalize_suppliers(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize supplier data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append({
                "source": "TCE-BA",
                "supplier_id": item.get("cnpjCpf") or item.get("documento"),
                "supplier_name": item.get("nome") or item.get("razaoSocial"),
                "municipality": item.get("nomeMunicipio"),
                "municipality_code": item.get("codigoMunicipio"),
                "raw_data": item
            })

        return normalized

    def _normalize_bidding_processes(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize bidding process data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append({
                "source": "TCE-BA",
                "bidding_id": item.get("numeroLicitacao") or item.get("numero"),
                "modality": item.get("modalidade"),
                "object": item.get("objetoLicitacao") or item.get("objeto"),
                "value": float(item.get("valorEstimado", 0) or 0),
                "date": item.get("dataAbertura") or item.get("data"),
                "status": item.get("situacao") or item.get("status"),
                "municipality": item.get("nomeMunicipio"),
                "municipality_code": item.get("codigoMunicipio"),
                "government_unit": item.get("nomeOrgao") or item.get("orgao"),
                "raw_data": item
            })

        return normalized

    def _normalize_expenses(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize expense data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append({
                "source": "TCE-BA",
                "expense_id": item.get("numeroEmpenho") or item.get("numero"),
                "value": float(item.get("valorEmpenho", 0) or 0),
                "date": item.get("dataEmpenho") or item.get("data"),
                "description": item.get("historico") or item.get("descricao"),
                "category": item.get("funcao") or item.get("categoria"),
                "supplier_name": item.get("nomeFavorecido") or item.get("fornecedor"),
                "supplier_id": item.get("cnpjCpfFavorecido") or item.get("documento"),
                "municipality": item.get("nomeMunicipio"),
                "municipality_code": item.get("codigoMunicipio"),
                "government_unit": item.get("nomeOrgao") or item.get("orgao"),
                "raw_data": item
            })

        return normalized

    def _normalize_revenue(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize revenue data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append({
                "source": "TCE-BA",
                "revenue_id": item.get("numeroReceita") or item.get("numero"),
                "value": float(item.get("valorReceita", 0) or 0),
                "date": item.get("dataArrecadacao") or item.get("data"),
                "description": item.get("descricao") or item.get("fonte"),
                "category": item.get("categoria") or item.get("tipo"),
                "municipality": item.get("nomeMunicipio"),
                "municipality_code": item.get("codigoMunicipio"),
                "government_unit": item.get("nomeOrgao") or item.get("orgao"),
                "raw_data": item
            })

        return normalized
