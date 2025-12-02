"""
TCE Minas Gerais API Client

API client for Minas Gerais State Audit Court (Tribunal de Contas do Estado).
TCE-MG provides fiscal oversight data for Minas Gerais state and municipalities.

API Base: https://www.tce.mg.gov.br/TCETransparenciaAPI/api
Formats: JSON
Schema: RESTful API with standardized endpoints

Available endpoints:
- /contratos: Contracts and amendments
- /licitacoes: Bidding processes
- /despesas: Expenses and commitments
- /receitas: Revenue collection
- /fornecedores: Suppliers and contractors
- /obras: Public works
- /municipios: Municipality list

Note: TCE-MG covers 853 municipalities in Minas Gerais state.
Special attention given as this is the home state of the project author.

Author: Anderson Henrique da Silva
Created: 2025-10-09 14:55:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

from typing import Any

from ..base import TransparencyAPIClient


class TCEMinasGeraisClient(TransparencyAPIClient):
    """
    API client for TCE Minas Gerais (Tribunal de Contas do Estado de Minas Gerais).

    Provides access to fiscal data for 853 municipalities in Minas Gerais state.

    Examples:
        >>> client = TCEMinasGeraisClient()
        >>> contracts = await client.get_contracts(year=2024)
        >>> municipalities = await client.get_municipalities()
        >>> obras = await client.get_public_works(municipality_code="3106200")
    """

    def __init__(self):
        super().__init__(
            base_url="https://dadosabertos.tce.mg.gov.br/api/3/action",  # CKAN API
            name="TCE-MG",
            rate_limit_per_minute=60,
            timeout=30.0,
        )

    async def test_connection(self) -> bool:
        """
        Test TCE-MG API connectivity.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # TCE-MG now uses CKAN API at dadosabertos.tce.mg.gov.br
            # Test with package_list endpoint
            result = await self._make_request(
                method="GET", endpoint="/package_list", params={"limit": 1}
            )

            # CKAN returns {"success": true, "result": [...]}
            is_success = result is not None and result.get("success") == True

            if is_success:
                self.logger.info("TCE-MG connection successful (CKAN API)")
            else:
                self.logger.warning("TCE-MG returned unsuccessful response")

            return is_success

        except Exception as e:
            self.logger.error(f"TCE-MG connection failed: {str(e)}")
            return False

    async def get_municipalities(self) -> list[dict[str, Any]]:
        """
        Get list of Minas Gerais municipalities.

        Returns:
            List of 853 municipality dictionaries with IBGE codes
        """
        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/municipios", params=None
            )

            municipalities = self._normalize_municipalities(raw_data)

            self.logger.info(
                f"Fetched {len(municipalities)} municipalities from TCE-MG"
            )

            return municipalities

        except Exception as e:
            self.logger.error(f"Failed to fetch municipalities: {str(e)}")
            return []

    async def get_contracts(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        year: int | None = None,
        municipality_code: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get contracts from TCE-MG.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            year: Filter by year
            municipality_code: IBGE municipality code (e.g., "3106200" for Belo Horizonte)
            **kwargs: Additional filters

        Returns:
            List of contract dictionaries
        """
        params = {}

        if year:
            params["anoExercicio"] = year
        if municipality_code:
            params["codigoMunicipio"] = municipality_code
        if start_date:
            params["dataInicio"] = start_date
        if end_date:
            params["dataFim"] = end_date

        # Add custom filters
        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/contratos", params=params if params else None
            )

            contracts = self._normalize_contracts(raw_data)

            self.logger.info(f"Fetched {len(contracts)} contracts from TCE-MG")

            return contracts

        except Exception as e:
            self.logger.error(f"Failed to fetch contracts: {str(e)}")
            return []

    async def get_suppliers(
        self, municipality_code: str | None = None, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """
        Get suppliers (fornecedores) from TCE-MG.

        Args:
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of supplier dictionaries
        """
        params = {}

        if municipality_code:
            params["codigoMunicipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET",
                endpoint="/fornecedores",
                params=params if params else None,
            )

            suppliers = self._normalize_suppliers(raw_data)

            self.logger.info(f"Fetched {len(suppliers)} suppliers from TCE-MG")

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
        Get bidding processes (licitações) from TCE-MG.

        Args:
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of bidding process dictionaries
        """
        params = {}

        if year:
            params["anoExercicio"] = year
        if municipality_code:
            params["codigoMunicipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/licitacoes", params=params if params else None
            )

            biddings = self._normalize_bidding_processes(raw_data)

            self.logger.info(f"Fetched {len(biddings)} bidding processes from TCE-MG")

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
        Get expenses (despesas) from TCE-MG.

        Args:
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of expense dictionaries
        """
        params = {}

        if year:
            params["anoExercicio"] = year
        if municipality_code:
            params["codigoMunicipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/despesas", params=params if params else None
            )

            expenses = self._normalize_expenses(raw_data)

            self.logger.info(f"Fetched {len(expenses)} expenses from TCE-MG")

            return expenses

        except Exception as e:
            self.logger.error(f"Failed to fetch expenses: {str(e)}")
            return []

    async def get_revenue(
        self,
        year: int | None = None,
        municipality_code: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get revenue (receitas) from TCE-MG.

        Args:
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of revenue dictionaries
        """
        params = {}

        if year:
            params["anoExercicio"] = year
        if municipality_code:
            params["codigoMunicipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/receitas", params=params if params else None
            )

            revenue = self._normalize_revenue(raw_data)

            self.logger.info(f"Fetched {len(revenue)} revenue records from TCE-MG")

            return revenue

        except Exception as e:
            self.logger.error(f"Failed to fetch revenue: {str(e)}")
            return []

    async def get_public_works(
        self,
        year: int | None = None,
        municipality_code: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get public works (obras) from TCE-MG.

        Args:
            year: Filter by year
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of public work dictionaries
        """
        params = {}

        if year:
            params["anoExercicio"] = year
        if municipality_code:
            params["codigoMunicipio"] = municipality_code

        params.update(kwargs)

        try:
            raw_data = await self._make_request(
                method="GET", endpoint="/obras", params=params if params else None
            )

            works = self._normalize_public_works(raw_data)

            self.logger.info(f"Fetched {len(works)} public works from TCE-MG")

            return works

        except Exception as e:
            self.logger.error(f"Failed to fetch public works: {str(e)}")
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
                    "source": "TCE-MG",
                    "municipality_code": item.get("codigoIbge") or item.get("codigo"),
                    "municipality_name": item.get("nome") or item.get("nomeMunicipio"),
                    "state": "MG",
                    "region": item.get("regiao"),
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
                    "source": "TCE-MG",
                    "contract_id": item.get("numeroContrato") or item.get("numero"),
                    "supplier_name": item.get("nomeContratado")
                    or item.get("fornecedor"),
                    "supplier_id": item.get("cpfCnpjContratado")
                    or item.get("documento"),
                    "value": float(item.get("valorContrato", 0) or 0),
                    "date": item.get("dataAssinatura") or item.get("data"),
                    "object": item.get("objetoContrato") or item.get("objeto"),
                    "status": item.get("situacaoContrato") or item.get("situacao"),
                    "municipality": item.get("nomeMunicipio"),
                    "municipality_code": item.get("codigoMunicipio"),
                    "government_unit": item.get("nomeOrgao") or item.get("orgao"),
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
                    "source": "TCE-MG",
                    "supplier_id": item.get("cpfCnpj") or item.get("documento"),
                    "supplier_name": item.get("nomeFornecedor") or item.get("nome"),
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
                    "source": "TCE-MG",
                    "bidding_id": item.get("numeroLicitacao") or item.get("numero"),
                    "modality": item.get("modalidadeLicitacao")
                    or item.get("modalidade"),
                    "object": item.get("objetoLicitacao") or item.get("objeto"),
                    "value": float(item.get("valorEstimado", 0) or 0),
                    "date": item.get("dataAbertura") or item.get("data"),
                    "status": item.get("situacaoLicitacao") or item.get("situacao"),
                    "municipality": item.get("nomeMunicipio"),
                    "municipality_code": item.get("codigoMunicipio"),
                    "government_unit": item.get("nomeOrgao") or item.get("orgao"),
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
                    "source": "TCE-MG",
                    "expense_id": item.get("numeroEmpenho") or item.get("numero"),
                    "value": float(item.get("valorEmpenho", 0) or 0),
                    "date": item.get("dataEmpenho") or item.get("data"),
                    "description": item.get("historicoEmpenho")
                    or item.get("descricao"),
                    "category": item.get("funcaoGoverno") or item.get("categoria"),
                    "supplier_name": item.get("nomeFavorecido")
                    or item.get("fornecedor"),
                    "supplier_id": item.get("cpfCnpjFavorecido")
                    or item.get("documento"),
                    "municipality": item.get("nomeMunicipio"),
                    "municipality_code": item.get("codigoMunicipio"),
                    "government_unit": item.get("nomeOrgao") or item.get("orgao"),
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
                    "source": "TCE-MG",
                    "revenue_id": item.get("numeroReceita") or item.get("numero"),
                    "value": float(item.get("valorReceita", 0) or 0),
                    "date": item.get("dataArrecadacao") or item.get("data"),
                    "description": item.get("descricaoReceita") or item.get("fonte"),
                    "category": item.get("categoriaReceita") or item.get("tipo"),
                    "municipality": item.get("nomeMunicipio"),
                    "municipality_code": item.get("codigoMunicipio"),
                    "government_unit": item.get("nomeOrgao") or item.get("orgao"),
                    "raw_data": item,
                }
            )

        return normalized

    def _normalize_public_works(self, raw_data: Any) -> list[dict[str, Any]]:
        """Normalize public works data to common format."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            normalized.append(
                {
                    "source": "TCE-MG",
                    "work_id": item.get("numeroObra") or item.get("codigo"),
                    "work_name": item.get("nomeObra") or item.get("descricao"),
                    "value": float(item.get("valorContratado", 0) or 0),
                    "start_date": item.get("dataInicio"),
                    "end_date": item.get("dataFim") or item.get("dataPrevisaoTermino"),
                    "status": item.get("situacaoObra") or item.get("situacao"),
                    "contractor": item.get("nomeContratado") or item.get("responsavel"),
                    "municipality": item.get("nomeMunicipio"),
                    "municipality_code": item.get("codigoMunicipio"),
                    "government_unit": item.get("nomeOrgao") or item.get("orgao"),
                    "completion_percentage": item.get("percentualExecucao"),
                    "raw_data": item,
                }
            )

        return normalized
