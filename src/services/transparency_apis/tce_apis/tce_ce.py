"""
TCE Ceará API Client

API client for Ceará State Audit Court (Tribunal de Contas do Estado).
TCE-CE provides fiscal data for Ceará state and municipalities.

API Base: https://api-dados-abertos.tce.ce.gov.br
Formats: JSON
Endpoints:
- /municipios: Municipalities list
- /receitas: Revenue data
- /despesas: Expense data
- /contratos: Contracts
- /licitacoes: Bidding processes

Updated: 2025-11-14 - Switched to new open data API
Previous API (https://api.tce.ce.gov.br/sim/1_0/) is deprecated

Author: Anderson Henrique da Silva
Created: 2025-10-09 14:27:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

from typing import Any, Optional

from ..base import TransparencyAPIClient


class TCECearaClient(TransparencyAPIClient):
    """
    API client for TCE Ceará (Tribunal de Contas do Estado do Ceará).

    Examples:
        >>> client = TCECearaClient()
        >>> municipalities = await client.get_municipalities()
        >>> contracts = await client.get_contracts(municipality_code="230440")
    """

    def __init__(self):
        super().__init__(
            base_url="https://api-dados-abertos.tce.ce.gov.br",
            name="TCE-CE",
            rate_limit_per_minute=60,
            timeout=30.0,  # New API is faster
        )

    async def test_connection(self) -> bool:
        """
        Test TCE-CE API connectivity.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Try to fetch municipalities list (small dataset)
            result = await self._make_request(
                method="GET", endpoint="/municipios", params=None
            )

            is_success = result is not None and isinstance(result, dict)

            if is_success:
                self.logger.info("TCE-CE connection successful")
            else:
                self.logger.warning("TCE-CE returned empty response")

            return is_success

        except Exception as e:
            self.logger.error(f"TCE-CE connection failed: {str(e)}")
            return False

    async def get_municipalities(self) -> list[dict[str, Any]]:
        """
        Get list of Ceará municipalities.

        Returns:
            List of municipality dictionaries with IBGE codes
        """
        try:
            response = await self._make_request(
                method="GET", endpoint="/municipios", params=None
            )

            # New API returns {"data": [...]}
            raw_data = response.get("data", []) if isinstance(response, dict) else []

            municipalities = self._normalize_municipalities(raw_data)

            self.logger.info(
                f"Fetched {len(municipalities)} municipalities from TCE-CE"
            )

            return municipalities

        except Exception as e:
            self.logger.error(f"Failed to fetch municipalities: {str(e)}")
            return []

    async def get_contracts(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        municipality_code: Optional[str] = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get contracts from TCE-CE.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of contract dictionaries
        """
        params = {}

        if municipality_code:
            params["municipio"] = municipality_code

        if start_date:
            params["data_inicio"] = start_date

        if end_date:
            params["data_fim"] = end_date

        # Add custom params
        params.update(kwargs)

        try:
            response = await self._make_request(
                method="GET", endpoint="/contratos", params=params if params else None
            )

            # New API returns {"data": [...]}
            raw_data = response.get("data", []) if isinstance(response, dict) else []

            contracts = self._normalize_contracts(raw_data)

            self.logger.info(f"Fetched {len(contracts)} contracts from TCE-CE")

            return contracts

        except Exception as e:
            self.logger.error(f"Failed to fetch contracts: {str(e)}")
            return []

    async def get_suppliers(
        self, municipality_code: Optional[str] = None, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """
        Get suppliers/contractors from TCE-CE.

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
            response = await self._make_request(
                method="GET",
                endpoint="/fornecedores",
                params=params if params else None,
            )

            # New API returns {"data": [...]}
            raw_data = response.get("data", []) if isinstance(response, dict) else []

            suppliers = self._normalize_suppliers(raw_data)

            self.logger.info(f"Fetched {len(suppliers)} suppliers from TCE-CE")

            return suppliers

        except Exception as e:
            self.logger.error(f"Failed to fetch suppliers: {str(e)}")
            return []

    async def get_bidding_processes(
        self, municipality_code: Optional[str] = None, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """
        Get bidding processes (licitações) from TCE-CE.

        Args:
            municipality_code: IBGE municipality code
            **kwargs: Additional filters

        Returns:
            List of bidding process dictionaries
        """
        params = {}

        if municipality_code:
            params["municipio"] = municipality_code

        params.update(kwargs)

        try:
            response = await self._make_request(
                method="GET",
                endpoint="/licitacoes",
                params=params if params else None,
            )

            # New API returns {"data": [...]}
            raw_data = response.get("data", []) if isinstance(response, dict) else []

            biddings = self._normalize_bidding_processes(raw_data)

            self.logger.info(f"Fetched {len(biddings)} bidding processes from TCE-CE")

            return biddings

        except Exception as e:
            self.logger.error(f"Failed to fetch bidding processes: {str(e)}")
            return []

    def _normalize_municipalities(self, raw_data: Any) -> list[dict[str, Any]]:
        """Normalize municipality data."""
        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        normalized = []

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            # New API uses different field names
            normalized.append(
                {
                    "source": "TCE-CE",
                    "municipality_code": item.get("codigo_municipio")
                    or item.get("geoibgeId")
                    or item.get("codigoIBGE")
                    or item.get("codigo"),
                    "municipality_name": item.get("nome_municipio") or item.get("nome"),
                    "state": "CE",
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
                    "source": "TCE-CE",
                    "contract_id": item.get("numeroContrato"),
                    "supplier_name": item.get("nomeContratado")
                    or item.get("contratado"),
                    "supplier_id": item.get("cpfCnpjContratado") or item.get("cpfCnpj"),
                    "value": float(item.get("valorContrato", 0) or 0),
                    "date": item.get("dataAssinatura") or item.get("data"),
                    "object": item.get("objetoContrato") or item.get("objeto"),
                    "status": item.get("situacao"),
                    "municipality": item.get("nomeMunicipio"),
                    "municipality_code": item.get("codigoMunicipio")
                    or item.get("municipio"),
                    "government_unit": item.get("orgao"),
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
                    "source": "TCE-CE",
                    "supplier_id": item.get("cpfCnpj"),
                    "supplier_name": item.get("nome"),
                    "municipality": item.get("nomeMunicipio") or item.get("municipio"),
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
                    "source": "TCE-CE",
                    "bidding_id": item.get("numeroLicitacao") or item.get("numero"),
                    "modality": item.get("modalidade"),
                    "object": item.get("objeto"),
                    "value": float(item.get("valorEstimado", 0) or 0),
                    "date": item.get("dataAbertura") or item.get("data"),
                    "status": item.get("situacao"),
                    "municipality": item.get("nomeMunicipio") or item.get("municipio"),
                    "municipality_code": item.get("codigoMunicipio"),
                    "government_unit": item.get("orgao"),
                    "raw_data": item,
                }
            )

        return normalized
