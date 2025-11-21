"""
Portal da Transparência Integration Service
Real-time data fetching from Brazilian government transparency portal
"""

import asyncio
from datetime import UTC, date, datetime, timedelta
from typing import Any, Optional
from urllib.parse import urlencode

import httpx

from src.core import get_logger
from src.core.config import settings
from src.core.exceptions import TransparencyAPIError
from src.services.cache_service import CacheService

logger = get_logger(__name__)


class PortalTransparenciaService:
    """Service for fetching real data from Portal da Transparência."""

    BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"

    # API Endpoints
    ENDPOINTS = {
        "contratos": "/contratos",
        "licitacoes": "/licitacoes",
        "convenios": "/convenios",
        "despesas": "/despesas",
        "servidores": "/servidores",
        "viagens": "/viagens",
        "cartoes": "/cartoes",
        "fornecedores": "/fornecedores",
        "orgaos": "/orgaos",
        "emendas": "/emendas-parlamentares",
    }

    def __init__(self):
        """Initialize the Portal da Transparência service."""
        self.api_key = getattr(settings, "transparency_api_key", None)
        if self.api_key:
            self.api_key = (
                self.api_key.get_secret_value()
                if hasattr(self.api_key, "get_secret_value")
                else self.api_key
            )

        self.cache = CacheService()
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize HTTP client with proper headers."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "CidadaoAI/1.0 (https://cidadao.ai)",
        }

        if self.api_key:
            headers["chave-api-dados"] = self.api_key

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=10),
        )

    async def search_contracts(
        self,
        orgao: Optional[str] = None,
        cnpj_fornecedor: Optional[str] = None,
        data_inicial: Optional[date] = None,
        data_final: Optional[date] = None,
        valor_minimo: Optional[float] = None,
        valor_maximo: Optional[float] = None,
        situacao: Optional[str] = None,
        modalidade: Optional[str] = None,
        page: int = 1,
        size: int = 100,
    ) -> dict[str, Any]:
        """
        Search government contracts with filters.

        Args:
            orgao: Government agency code
            cnpj_fornecedor: Supplier CNPJ
            data_inicial: Start date
            data_final: End date
            valor_minimo: Minimum value
            valor_maximo: Maximum value
            situacao: Contract status
            modalidade: Contract modality
            page: Page number
            size: Page size

        Returns:
            Dict with contracts data and metadata
        """
        # Build query parameters
        params = {"pagina": page, "tamanhoPagina": min(size, 500)}  # API limit

        # CRITICAL FIX: Portal API requires codigoOrgao parameter (returns 400 without it)
        # Use Ministério da Saúde (36000) as default for general queries
        if not orgao:
            orgao = "36000"  # Ministério da Saúde - high volume of contracts
            logger.info(
                "Using default orgao=36000 (Ministério da Saúde) for Portal API - codigoOrgao is required"
            )

        params["codigoOrgao"] = orgao  # Always include codigoOrgao (required by API)

        if cnpj_fornecedor:
            params["cnpjFornecedor"] = cnpj_fornecedor
        if data_inicial:
            params["dataInicial"] = data_inicial.strftime("%d/%m/%Y")
        if data_final:
            params["dataFinal"] = data_final.strftime("%d/%m/%Y")
        if valor_minimo:
            params["valorMinimo"] = valor_minimo
        if valor_maximo:
            params["valorMaximo"] = valor_maximo
        if situacao:
            params["situacao"] = situacao
        if modalidade:
            params["modalidadeCompra"] = modalidade

        # Portal API requires at least one filter (date or orgao)
        # If no filters provided, use last 30 days as default
        has_filter = any(
            [
                orgao,
                cnpj_fornecedor,
                data_inicial,
                data_final,
                valor_minimo,
                valor_maximo,
            ]
        )
        if not has_filter:
            # Default to last 30 days
            # Note: Portal API may have delayed data updates, use safe date range
            today = date.today()
            # Portal API typically has data up to 2-3 months behind current date
            # Use safe end date to avoid 400 errors for data not yet available
            safe_end_date = date(2024, 12, 31)  # Use last known good data period
            if today > safe_end_date:
                end_date = safe_end_date
                logger.info(
                    f"Using safe end date {end_date} (current: {today}) for Portal API"
                )
            else:
                end_date = today

            start_date = end_date - timedelta(days=30)
            params["dataInicial"] = start_date.strftime("%d/%m/%Y")
            params["dataFinal"] = end_date.strftime("%d/%m/%Y")
            logger.info(
                f"Portal API date range: {params['dataInicial']} to {params['dataFinal']}"
            )

        # Check cache
        cache_key = f"contracts:{urlencode(params)}"
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info("Returning cached contracts data")
            return cached

        # Demo mode if no API key
        if not self.api_key:
            logger.warning("No API key configured - returning demo data")
            return self._get_demo_contracts(params)

        try:
            response = await self.client.get(self.ENDPOINTS["contratos"], params=params)
            response.raise_for_status()

            data = response.json()

            # Handle different response formats
            # Portal API can return: array directly, or object with 'resultado'
            if isinstance(data, list):
                # Direct array response
                contratos = data
                total = len(data)
            else:
                # Object response with 'resultado' key
                contratos = data.get("resultado", [])
                total = data.get("quantidadeTotal", len(contratos))

            # Process and enrich data
            result = {
                "contratos": contratos,
                "total": total,
                "pagina": page,
                "tamanho_pagina": size,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            # Cache for 1 hour
            await self.cache.set(cache_key, result, ttl=3600)

            logger.info(
                f"Fetched {len(result['contratos'])} contracts from Portal da Transparência"
            )
            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Invalid API key for Portal da Transparência")
                raise TransparencyAPIError("Invalid API key")
            elif e.response.status_code == 429:
                logger.warning("Rate limit exceeded for Portal da Transparência")
                raise TransparencyAPIError("Rate limit exceeded")
            else:
                logger.error(f"HTTP error from Portal da Transparência: {e}")
                raise TransparencyAPIError(f"API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching contracts: {e}")
            raise TransparencyAPIError(f"Failed to fetch contracts: {str(e)}")

    async def search_biddings(
        self,
        orgao: Optional[str] = None,
        modalidade: Optional[str] = None,
        situacao: Optional[str] = None,
        data_inicial: Optional[date] = None,
        data_final: Optional[date] = None,
        page: int = 1,
        size: int = 100,
    ) -> dict[str, Any]:
        """Search government biddings (licitações)."""
        params = {"pagina": page, "tamanhoPagina": min(size, 500)}

        if orgao:
            params["codigoOrgao"] = orgao
        if modalidade:
            params["modalidadeLicitacao"] = modalidade
        if situacao:
            params["situacao"] = situacao
        if data_inicial:
            params["dataInicial"] = data_inicial.strftime("%d/%m/%Y")
        if data_final:
            params["dataFinal"] = data_final.strftime("%d/%m/%Y")

        try:
            response = await self.client.get(
                self.ENDPOINTS["licitacoes"], params=params
            )
            response.raise_for_status()

            data = response.json()
            return {
                "licitacoes": data.get("resultado", []),
                "total": data.get("quantidadeTotal", 0),
                "pagina": page,
                "tamanho_pagina": size,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error fetching biddings: {e}")
            raise TransparencyAPIError(f"Failed to fetch biddings: {str(e)}")

    async def search_expenses(
        self,
        orgao: Optional[str] = None,
        favorecido: Optional[str] = None,
        elemento_despesa: Optional[str] = None,
        mes_ano: Optional[str] = None,  # MM/AAAA
        page: int = 1,
        size: int = 100,
    ) -> dict[str, Any]:
        """Search government expenses."""
        params = {"pagina": page, "tamanhoPagina": min(size, 500)}

        if orgao:
            params["codigoOrgao"] = orgao
        if favorecido:
            params["nomeFavorecido"] = favorecido
        if elemento_despesa:
            params["codigoElementoDespesa"] = elemento_despesa
        if mes_ano:
            params["mesAno"] = mes_ano

        try:
            response = await self.client.get(self.ENDPOINTS["despesas"], params=params)
            response.raise_for_status()

            data = response.json()
            return {
                "despesas": data.get("resultado", []),
                "total": data.get("quantidadeTotal", 0),
                "pagina": page,
                "tamanho_pagina": size,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error fetching expenses: {e}")
            raise TransparencyAPIError(f"Failed to fetch expenses: {str(e)}")

    async def search_public_servants(
        self,
        nome: Optional[str] = None,
        cpf: Optional[str] = None,
        orgao: Optional[str] = None,
        cargo: Optional[str] = None,
        page: int = 1,
        size: int = 100,
    ) -> dict[str, Any]:
        """Search public servants information."""
        params = {"pagina": page, "tamanhoPagina": min(size, 500)}

        if nome:
            params["nome"] = nome
        if cpf:
            params["cpf"] = cpf
        if orgao:
            params["codigoOrgaoLotacao"] = orgao
        if cargo:
            params["descricaoCargo"] = cargo

        try:
            response = await self.client.get(
                self.ENDPOINTS["servidores"], params=params
            )
            response.raise_for_status()

            data = response.json()

            # Handle both list and object responses
            if isinstance(data, list):
                return {
                    "servidores": data,
                    "total": len(data),
                    "pagina": page,
                    "tamanho_pagina": size,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            else:
                return {
                    "servidores": data.get("resultado", []),
                    "total": data.get("quantidadeTotal", 0),
                    "pagina": page,
                    "tamanho_pagina": size,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
        except Exception as e:
            logger.error(f"Error fetching servants: {e}")
            raise TransparencyAPIError(f"Failed to fetch servants: {str(e)}")

    async def get_supplier_info(self, cnpj: str) -> dict[str, Any]:
        """Get detailed information about a supplier."""
        cache_key = f"supplier:{cnpj}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        try:
            # Get basic info
            response = await self.client.get(f"{self.ENDPOINTS['fornecedores']}/{cnpj}")
            response.raise_for_status()

            supplier_info = response.json()

            # Get contracts for this supplier
            contracts = await self.search_contracts(cnpj_fornecedor=cnpj, size=10)

            result = {
                "fornecedor": supplier_info,
                "contratos_recentes": contracts.get("contratos", []),
                "total_contratos": contracts.get("total", 0),
                "timestamp": datetime.now(UTC).isoformat(),
            }

            # Cache for 24 hours
            await self.cache.set(cache_key, result, ttl=86400)

            return result

        except Exception as e:
            logger.error(f"Error fetching supplier info: {e}")
            raise TransparencyAPIError(f"Failed to fetch supplier: {str(e)}")

    async def get_agency_info(self, codigo: str) -> dict[str, Any]:
        """Get detailed information about a government agency."""
        try:
            response = await self.client.get(f"{self.ENDPOINTS['orgaos']}/{codigo}")
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Error fetching agency info: {e}")
            raise TransparencyAPIError(f"Failed to fetch agency: {str(e)}")

    async def analyze_spending_patterns(
        self, orgao: Optional[str] = None, periodo_meses: int = 12
    ) -> dict[str, Any]:
        """Analyze spending patterns over time."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=periodo_meses * 30)

        # Fetch contracts
        contracts_task = self.search_contracts(
            orgao=orgao, data_inicial=start_date, data_final=end_date, size=500
        )

        # Fetch expenses
        expenses_tasks = []
        current_date = start_date
        while current_date <= end_date:
            mes_ano = current_date.strftime("%m/%Y")
            expenses_tasks.append(
                self.search_expenses(orgao=orgao, mes_ano=mes_ano, size=500)
            )
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        # Wait for all requests
        results = await asyncio.gather(
            contracts_task, *expenses_tasks, return_exceptions=True
        )

        # Process results
        contracts = (
            results[0].get("contratos", []) if isinstance(results[0], dict) else []
        )
        all_expenses = []
        for result in results[1:]:
            if isinstance(result, dict):
                all_expenses.extend(result.get("despesas", []))

        # Analyze patterns
        analysis = {
            "periodo": {"inicio": start_date.isoformat(), "fim": end_date.isoformat()},
            "total_contratos": len(contracts),
            "total_despesas": len(all_expenses),
            "valor_total_contratos": sum(c.get("valorTotal", 0) for c in contracts),
            "fornecedores_unicos": len(
                set(
                    c.get("cnpjFornecedor")
                    for c in contracts
                    if c.get("cnpjFornecedor")
                )
            ),
            "modalidades": {},
            "evolucao_mensal": {},
            "maiores_fornecedores": [],
            "alertas": [],
        }

        # Count by modality
        for contract in contracts:
            modalidade = contract.get("modalidadeCompra", "Não informado")
            analysis["modalidades"][modalidade] = (
                analysis["modalidades"].get(modalidade, 0) + 1
            )

        # Find top suppliers
        supplier_values = {}
        for contract in contracts:
            cnpj = contract.get("cnpjFornecedor")
            if cnpj:
                supplier_values[cnpj] = supplier_values.get(cnpj, 0) + contract.get(
                    "valorTotal", 0
                )

        analysis["maiores_fornecedores"] = sorted(
            [{"cnpj": k, "valor_total": v} for k, v in supplier_values.items()],
            key=lambda x: x["valor_total"],
            reverse=True,
        )[:10]

        # Check for alerts
        if len(analysis["maiores_fornecedores"]) > 0:
            top_supplier_value = analysis["maiores_fornecedores"][0]["valor_total"]
            if analysis["valor_total_contratos"] > 0:
                concentration = top_supplier_value / analysis["valor_total_contratos"]
                if concentration > 0.3:
                    analysis["alertas"].append(
                        {
                            "tipo": "concentracao_fornecedor",
                            "mensagem": f"Fornecedor concentra {concentration:.1%} dos contratos",
                            "severidade": "alta",
                        }
                    )

        return analysis

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def _get_demo_contracts(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get demo contracts when no API key is available."""
        from datetime import datetime

        demo_contracts = [
            {
                "id": "CTR-2024-001",
                "numero": "001/2024",
                "objeto": "Aquisição de medicamentos para tratamento de COVID-19 e outras doenças respiratórias",
                "valorTotal": 2500000.00,
                "dataAssinatura": "2024-01-15",
                "dataPublicacao": "2024-01-16",
                "vigenciaInicio": "2024-01-20",
                "vigenciaFim": "2025-01-20",
                "situacao": "Ativo",
                "modalidadeCompra": "Pregão Eletrônico",
                "cnpjFornecedor": "12345678000190",
                "nomeFantasiaFornecedor": "Farmacêutica Nacional S.A.",
                "orgaoContratante": {
                    "codigo": "26000",
                    "nome": "Ministério da Saúde",
                    "sigla": "MS",
                },
            },
            {
                "id": "CTR-2024-002",
                "numero": "002/2024",
                "objeto": "Contratação de serviços de manutenção hospitalar para unidades de saúde",
                "valorTotal": 8750000.00,
                "dataAssinatura": "2024-02-01",
                "dataPublicacao": "2024-02-02",
                "vigenciaInicio": "2024-02-05",
                "vigenciaFim": "2025-02-05",
                "situacao": "Ativo",
                "modalidadeCompra": "Concorrência",
                "cnpjFornecedor": "98765432000123",
                "nomeFantasiaFornecedor": "Engenharia e Manutenção LTDA",
                "orgaoContratante": {
                    "codigo": "26000",
                    "nome": "Ministério da Saúde",
                    "sigla": "MS",
                },
            },
            {
                "id": "CTR-2024-003",
                "numero": "003/2024",
                "objeto": "Fornecimento de equipamentos de proteção individual (EPIs) para profissionais de saúde",
                "valorTotal": 3200000.00,
                "dataAssinatura": "2024-03-10",
                "dataPublicacao": "2024-03-11",
                "vigenciaInicio": "2024-03-15",
                "vigenciaFim": "2025-03-15",
                "situacao": "Ativo",
                "modalidadeCompra": "Pregão Eletrônico",
                "cnpjFornecedor": "11223344000155",
                "nomeFantasiaFornecedor": "Proteção Médica Distribuidora",
                "orgaoContratante": {
                    "codigo": "26000",
                    "nome": "Ministério da Saúde",
                    "sigla": "MS",
                },
            },
        ]

        # Filter by organization if specified
        if params.get("codigoOrgao"):
            demo_contracts = [
                c
                for c in demo_contracts
                if c["orgaoContratante"]["codigo"] == params["codigoOrgao"]
            ]

        return {
            "contratos": demo_contracts[: params.get("tamanhoPagina", 100)],
            "total": len(demo_contracts),
            "pagina": params.get("pagina", 1),
            "tamanho_pagina": params.get("tamanhoPagina", 100),
            "timestamp": datetime.now(UTC).isoformat(),
            "demo_mode": True,
        }


# Singleton instance
portal_transparencia = PortalTransparenciaService()
