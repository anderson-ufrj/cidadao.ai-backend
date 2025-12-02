"""
SICONFI API Client - Tesouro Nacional

Sistema de Informações Contábeis e Fiscais do Setor Público Brasileiro.
Provides fiscal and accounting data for all Brazilian states and municipalities.

API Documentation: http://apidatalake.tesouro.gov.br/docs/siconfi/
Base URL: https://apidatalake.tesouro.gov.br/ords/siconfi/tt/

Coverage:
- 5,570 municipalities
- 27 states + Federal District
- Historical data from 2014+

Reports Available:
- RREO: Relatório Resumido da Execução Orçamentária
- RGF: Relatório de Gestão Fiscal
- DCA: Declaração de Contas Anuais
- MSC: Matriz de Saldos Contábeis

Author: Anderson Henrique da Silva
Created: 2025-11-14
License: Proprietary - All rights reserved
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ..base import TransparencyAPIClient
from .exceptions import FederalAPIError
from .retry import retry_with_backoff


class RREOData(BaseModel):
    """RREO - Relatório Resumido da Execução Orçamentária."""

    exercicio: int = Field(alias="an_exercicio", description="Fiscal year")
    periodo: int = Field(alias="nr_periodo", description="Period number (1-6)")
    cod_ibge: Any | None = Field(
        default=None, alias="cod_ibge", description="IBGE municipality code"
    )
    ente: str = Field(alias="ente", description="Entity name (state/municipality)")
    uf: str = Field(alias="uf", description="State code")
    populacao: int | None = Field(
        default=None, alias="populacao", description="Population"
    )
    anexo: str = Field(alias="anexo", description="Report annex")
    conta: str | None = Field(default=None, alias="conta", description="Account code")
    descricao_conta: str | None = Field(
        default=None, alias="descricao_conta", description="Account description"
    )
    valor: float | None = Field(default=None, alias="valor", description="Value in BRL")

    class Config:
        populate_by_name = True


class RGFData(BaseModel):
    """RGF - Relatório de Gestão Fiscal."""

    exercicio: int = Field(alias="an_exercicio", description="Fiscal year")
    periodo: int = Field(alias="nr_periodo", description="Period number")
    cod_ibge: Any | None = Field(
        default=None, alias="cod_ibge", description="IBGE municipality code"
    )
    ente: str | None = Field(default=None, alias="ente", description="Entity name")
    uf: str | None = Field(default=None, alias="uf", description="State code")
    anexo: str | None = Field(default=None, alias="anexo", description="Report annex")
    conta: str | None = Field(default=None, alias="conta", description="Account code")
    descricao_conta: str | None = Field(
        default=None, alias="descricao_conta", description="Account description"
    )
    valor: float | None = Field(default=None, alias="valor", description="Value in BRL")

    class Config:
        populate_by_name = True


class DCAData(BaseModel):
    """DCA - Declaração de Contas Anuais."""

    exercicio: int = Field(alias="an_exercicio", description="Fiscal year")
    cod_ibge: Any | None = Field(
        default=None, alias="cod_ibge", description="IBGE municipality code"
    )
    ente: str | None = Field(default=None, alias="ente", description="Entity name")
    uf: str | None = Field(default=None, alias="uf", description="State code")
    anexo: str | None = Field(default=None, alias="anexo", description="Report annex")
    conta: str | None = Field(default=None, alias="conta", description="Account code")
    descricao_conta: str | None = Field(
        default=None, alias="descricao_conta", description="Account description"
    )
    valor: float | None = Field(default=None, alias="valor", description="Value in BRL")

    class Config:
        populate_by_name = True
        extra = "allow"  # Allow extra fields from API


class MSCData(BaseModel):
    """MSC - Matriz de Saldos Contábeis."""

    exercicio: int = Field(alias="an_exercicio", description="Fiscal year")
    mes: int = Field(alias="me_referencia", description="Reference month")
    cod_ibge: Any | None = Field(
        default=None, alias="cod_ibge", description="IBGE municipality code"
    )
    ente: str | None = Field(default=None, alias="ente", description="Entity name")
    uf: str | None = Field(default=None, alias="uf", description="State code")
    conta_contabil: str | None = Field(
        default=None, alias="conta_contabil", description="Accounting account"
    )
    descricao_conta: str | None = Field(
        default=None, alias="descricao_conta", description="Account description"
    )
    saldo_inicial: float | None = Field(
        default=None, alias="saldo_inicial", description="Initial balance"
    )
    debito: float | None = Field(
        default=None, alias="debito", description="Debit amount"
    )
    credito: float | None = Field(
        default=None, alias="credito", description="Credit amount"
    )
    saldo_final: float | None = Field(
        default=None, alias="saldo_final", description="Final balance"
    )

    class Config:
        populate_by_name = True


class EntityInfo(BaseModel):
    """Entity (Municipality/State) information."""

    cod_ibge: Any = Field(description="IBGE code")
    ente: str | None = Field(default=None, description="Entity name")
    capital: str | None = Field(default=None, description="Capital name")
    regiao: str | None = Field(default=None, description="Region")
    uf: str | None = Field(default=None, description="State code")
    esfera: str | None = Field(
        default=None, description="Government sphere (M=Municipal, E=State)"
    )
    exercicio: int | None = Field(default=None, description="Fiscal year")
    populacao: int | None = Field(default=None, description="Population")

    class Config:
        populate_by_name = True
        extra = "allow"  # Allow extra fields from API


class SICONFIClient(TransparencyAPIClient):
    """
    Client for SICONFI API - Tesouro Nacional.

    Provides access to fiscal and accounting data for all Brazilian
    states and municipalities.

    Features:
    - No authentication required (public data)
    - 5,000 items per page (pagination handled automatically)
    - Data from 2014+ for most entities
    - Real-time budget execution tracking

    Example:
        ```python
        async with SICONFIClient() as client:
            # Get budget execution for São Paulo
            rreo = await client.get_rreo(
                year=2024,
                period=1,
                entity_code="3550308"  # São Paulo IBGE code
            )
            print(f"Found {len(rreo)} budget execution records")
        ```
    """

    BASE_URL = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"

    # RREO annexes (budget execution report)
    RREO_ANNEXES = [
        "RREO-Anexo 01",  # Balanço Orçamentário
        "RREO-Anexo 02",  # Demonstrativo da Execução das Despesas
        "RREO-Anexo 03",  # Demonstrativo da Receita Corrente Líquida
        "RREO-Anexo 06",  # Demonstrativo dos Resultados Primário e Nominal
    ]

    # RGF annexes (fiscal management report)
    RGF_ANNEXES = [
        "RGF-Anexo 01",  # Demonstrativo da Despesa com Pessoal
        "RGF-Anexo 02",  # Demonstrativo da Dívida Consolidada Líquida
        "RGF-Anexo 03",  # Demonstrativo das Garantias e Contragarantias
        "RGF-Anexo 04",  # Demonstrativo das Operações de Crédito
    ]

    def __init__(self, timeout: float = 60.0):
        """
        Initialize SICONFI client.

        Args:
            timeout: Request timeout in seconds (default: 60s for large datasets)
        """
        super().__init__(
            name="SICONFI",
            base_url=self.BASE_URL,
            timeout=timeout,
        )

    @retry_with_backoff(max_attempts=3)
    async def get_rreo(
        self,
        year: int,
        period: int,
        entity_code: str | None = None,
        annex: str = "RREO-Anexo 01",
        limit: int = 5000,
    ) -> list[RREOData]:
        """
        Get RREO - Relatório Resumido da Execução Orçamentária.

        Budget execution summary report with revenue and expense data.

        Args:
            year: Fiscal year (e.g., 2024)
            period: Period number (1-6, bimonthly)
            entity_code: IBGE code for municipality/state (optional, returns all if None)
            annex: Report annex (default: Anexo 01 - Balanço Orçamentário)
            limit: Maximum records to return (default: 5000)

        Returns:
            List of RREO budget execution records

        Example:
            ```python
            # Get Q1 2024 budget execution for São Paulo
            rreo = await client.get_rreo(
                year=2024,
                period=1,
                entity_code="3550308"
            )
            ```
        """
        params: dict[str, Any] = {
            "an_exercicio": year,
            "nr_periodo": period,
            "no_anexo": annex,
        }

        if entity_code:
            params["id_ente"] = entity_code

        try:
            data = await self._make_request("GET", "/rreo", params=params)

            # Handle pagination - SICONFI returns items directly or in 'items' field
            if isinstance(data, dict):
                items = data.get("items", [])
            else:
                items = data if isinstance(data, list) else []

            # Limit results
            items = items[:limit]

            return [RREOData(**item) for item in items]

        except Exception as e:
            raise FederalAPIError(f"Failed to fetch RREO data: {str(e)}")

    @retry_with_backoff(max_attempts=3)
    async def get_rgf(
        self,
        year: int,
        period: int,
        entity_code: str | None = None,
        annex: str = "RGF-Anexo 01",
        limit: int = 5000,
    ) -> list[RGFData]:
        """
        Get RGF - Relatório de Gestão Fiscal.

        Fiscal management report with personnel expenses, debt, and fiscal limits.

        Args:
            year: Fiscal year
            period: Period number (1-3 for quadrimesters, or 1-6 for bimonthly)
            entity_code: IBGE code (optional)
            annex: Report annex (default: Anexo 01 - Personnel expenses)
            limit: Maximum records

        Returns:
            List of RGF fiscal management records
        """
        params: dict[str, Any] = {
            "an_exercicio": year,
            "nr_periodo": period,
            "no_anexo": annex,
        }

        if entity_code:
            params["id_ente"] = entity_code

        try:
            data = await self._make_request("GET", "/rgf", params=params)

            if isinstance(data, dict):
                items = data.get("items", [])
            else:
                items = data if isinstance(data, list) else []

            items = items[:limit]

            return [RGFData(**item) for item in items]

        except Exception as e:
            raise FederalAPIError(f"Failed to fetch RGF data: {str(e)}")

    @retry_with_backoff(max_attempts=3)
    async def get_dca(
        self,
        year: int,
        entity_code: str | None = None,
        annex: str = "DCA-Anexo I-AB",
        limit: int = 5000,
    ) -> list[DCAData]:
        """
        Get DCA - Declaração de Contas Anuais.

        Annual accounts statement with yearly financial summary.

        Args:
            year: Fiscal year
            entity_code: IBGE code (optional)
            annex: Report annex (default: Anexo I-AB)
            limit: Maximum records

        Returns:
            List of DCA annual account records
        """
        params: dict[str, Any] = {
            "an_exercicio": year,
            "no_anexo": annex,
        }

        if entity_code:
            params["id_ente"] = entity_code

        try:
            data = await self._make_request("GET", "/dca", params=params)

            if isinstance(data, dict):
                items = data.get("items", [])
            else:
                items = data if isinstance(data, list) else []

            items = items[:limit]

            return [DCAData(**item) for item in items]

        except Exception as e:
            raise FederalAPIError(f"Failed to fetch DCA data: {str(e)}")

    @retry_with_backoff(max_attempts=3)
    async def get_msc(
        self,
        year: int,
        month: int,
        entity_code: str | None = None,
        limit: int = 5000,
    ) -> list[MSCData]:
        """
        Get MSC - Matriz de Saldos Contábeis.

        Accounting balances matrix with monthly account movements.

        Args:
            year: Fiscal year
            month: Month (1-12)
            entity_code: IBGE code (optional)
            limit: Maximum records

        Returns:
            List of MSC accounting balance records
        """
        params: dict[str, Any] = {
            "an_exercicio": year,
            "me_referencia": month,
        }

        if entity_code:
            params["id_ente"] = entity_code

        try:
            data = await self._make_request("GET", "/msc", params=params)

            if isinstance(data, dict):
                items = data.get("items", [])
            else:
                items = data if isinstance(data, list) else []

            items = items[:limit]

            return [MSCData(**item) for item in items]

        except Exception as e:
            raise FederalAPIError(f"Failed to fetch MSC data: {str(e)}")

    @retry_with_backoff(max_attempts=3)
    async def get_entities(
        self,
        year: int,
        sphere: str | None = None,
        state: str | None = None,
        limit: int | None = None,
    ) -> list[EntityInfo]:
        """
        Get list of entities (municipalities/states) with available data.

        Args:
            year: Fiscal year
            sphere: Government sphere ('M'=Municipal, 'E'=State, None=All)
            state: State code (e.g., 'SP', 'RJ', None=All)
            limit: Maximum number of entities to return (optional)

        Returns:
            List of entities with available data
        """
        params: dict[str, Any] = {
            "an_exercicio": year,
        }

        if sphere:
            params["esfera"] = sphere
        if state:
            params["uf"] = state

        try:
            data = await self._make_request("GET", "/entes", params=params)

            if isinstance(data, dict):
                items = data.get("items", [])
            else:
                items = data if isinstance(data, list) else []

            # Apply limit if specified
            if limit is not None:
                items = items[:limit]

            return [EntityInfo(**item) for item in items]

        except Exception as e:
            raise FederalAPIError(f"Failed to fetch entities: {str(e)}")

    async def get_municipality_summary(
        self,
        entity_code: str,
        year: int,
    ) -> dict[str, Any]:
        """
        Get complete fiscal summary for a municipality.

        Retrieves RREO, RGF, and DCA data for comprehensive analysis.

        Args:
            entity_code: IBGE municipality code
            year: Fiscal year

        Returns:
            Dictionary with budget execution, fiscal management, and annual accounts
        """
        try:
            # Get latest period data
            rreo = await self.get_rreo(
                year=year, period=6, entity_code=entity_code, limit=100
            )
            rgf = await self.get_rgf(
                year=year, period=3, entity_code=entity_code, limit=100
            )
            dca = await self.get_dca(year=year, entity_code=entity_code, limit=100)

            return {
                "entity_code": entity_code,
                "year": year,
                "budget_execution": [r.model_dump() for r in rreo],
                "fiscal_management": [r.model_dump() for r in rgf],
                "annual_accounts": [d.model_dump() for d in dca],
                "total_records": len(rreo) + len(rgf) + len(dca),
            }

        except Exception as e:
            raise FederalAPIError(f"Failed to get municipality summary: {str(e)}")

    async def test_connection(self) -> bool:
        """
        Test if SICONFI API is accessible.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Try to get entities for current year
            current_year = datetime.now().year
            entities = await self.get_entities(year=current_year, limit=1)
            return len(entities) > 0
        except Exception:
            return False

    async def get_contracts(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        SICONFI doesn't provide contract data directly.
        This method is implemented for interface compatibility.

        Use RREO data for budget execution information instead.

        Returns:
            Empty list (not applicable for SICONFI)
        """
        return []
