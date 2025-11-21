"""
Portal da Transparência Integration Service - Improved Version
Real-time data fetching from Brazilian government transparency portal with robust fallbacks.
"""

from datetime import UTC, date, datetime, timedelta
from typing import Any, Optional
from urllib.parse import urlencode

import httpx

from src.core import get_logger
from src.core.config import settings

logger = get_logger(__name__)


class ImprovedPortalTransparenciaService:
    """
    Improved service for Portal da Transparência with better error handling.

    Key improvements:
    - Proper handling of required codigoOrgao parameter
    - Better date range handling for API limitations
    - Fallback mechanisms when cache is unavailable
    - More robust error messages
    """

    BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"

    # API Endpoints and their requirements
    # Complete list from Portal da Transparência Swagger UI
    ENDPOINTS = {
        # ========== SERVIDORES (Public Servants) ==========
        "servidores": {
            "path": "/servidores",
            "required_params": ["pagina"],
            "required_one_of": ["codigoOrgaoLotacao", "codigoOrgaoExercicio", "cpf"],
            "optional_params": ["nome"],
            "max_page_size": 500,
            "default_orgao_lotacao": "36000",  # Ministério da Saúde
            "description": "Lista servidores públicos federais (requer código SIAPE ou CPF)",
        },
        "servidores_remuneracao": {
            "path": "/servidores/{cpf}/remuneracao",
            "required_params": ["cpf", "mesAno"],
            "max_page_size": 500,
            "description": "Remuneração de servidor por CPF e mês/ano (MM/YYYY)",
        },
        "servidores_detalhes": {
            "path": "/servidores/{cpf}",
            "required_params": ["cpf"],
            "max_page_size": 500,
            "description": "Dados completos de um servidor por CPF",
        },
        # ========== CONTRATOS (Contracts) ==========
        "contratos": {
            "path": "/contratos",
            "required_params": ["codigoOrgao", "pagina"],
            "optional_params": ["dataInicial", "dataFinal"],
            "max_page_size": 500,
            "default_orgao": "36000",
            "description": "Contratos do governo federal",
        },
        # ========== LICITAÇÕES (Bids) ==========
        "licitacoes": {
            "path": "/licitacoes",
            "required_params": ["codigoOrgao", "dataInicial", "dataFinal", "pagina"],
            "max_page_size": 500,
            "max_date_range_days": 30,
            "default_orgao": "36000",
            "description": "Licitações públicas (requer período de até 30 dias)",
        },
        # ========== DESPESAS (Expenses) ==========
        "despesas_documentos": {
            "path": "/despesas/documentos",
            "required_params": ["codigoOrgao", "ano", "dataEmissao", "fase", "pagina"],
            "max_page_size": 500,
            "default_orgao": "36000",
            "default_fase": "3",  # Fase 3: Pagamento
            "description": "Despesas por documento (requer data de emissão e fase)",
        },
        "despesas_por_orgao": {
            "path": "/despesas/por-orgao",
            "required_params": ["ano", "pagina"],
            "required_one_of": ["codigoOrgao", "codigoUnidadeGestora", "mes"],
            "max_page_size": 500,
            "default_orgao": "36000",
            "description": "Despesas agrupadas por órgão (requer ano + (órgão OU UG OU mês))",
        },
        # ========== FORNECEDORES (Suppliers) ==========
        "fornecedores": {
            "path": "/fornecedores",
            "required_params": ["pagina"],
            "optional_params": ["cpfCnpj"],
            "max_page_size": 500,
            "description": "Fornecedores do governo",
        },
        # ========== CONVÊNIOS (Agreements) ==========
        "convenios": {
            "path": "/convenios",
            "required_params": ["pagina"],
            "required_one_of": ["uf", "municipio", "codigoOrgao", "numeroConvenio"],
            "optional_params": ["dataInicial", "dataFinal"],
            "max_page_size": 500,
            "max_date_range_days": 30,
            "default_uf": "MG",  # Minas Gerais
            "description": "Convênios federais (requer UF, município, órgão ou número)",
        },
        # ========== CARTÕES DE PAGAMENTO (Payment Cards) ==========
        "cartoes": {
            "path": "/cartoes",
            "required_params": ["mesAno", "pagina"],
            "required_one_of": ["codigoOrgao", "cpf", "cnpjFavorecido"],
            "max_page_size": 500,
            "max_month_range": 12,
            "default_orgao": "36000",
            "description": "Gastos com cartões corporativos (requer órgão, CPF ou CNPJ favorecido)",
        },
        # ========== VIAGENS (Travel) ==========
        "viagens": {
            "path": "/viagens",
            "required_params": [
                "dataIdaDe",
                "dataIdaAte",
                "dataRetornoDe",
                "dataRetornoAte",
                "pagina",
            ],
            "optional_params": ["cpf"],
            "max_page_size": 500,
            "description": "Viagens a serviço (requer períodos de ida E retorno)",
        },
        # ========== EMENDAS PARLAMENTARES (Parliamentary Amendments) ==========
        "emendas": {
            "path": "/emendas",
            "required_params": ["ano", "pagina"],
            "optional_params": ["autor"],
            "max_page_size": 500,
            "description": "Emendas parlamentares",
        },
        # ========== AUXÍLIO EMERGENCIAL (Emergency Aid) ==========
        "auxilio_emergencial": {
            "path": "/auxilio-emergencial",
            "required_params": ["mesAno", "pagina"],
            "optional_params": ["cpf"],
            "max_page_size": 500,
            "description": "Beneficiários do auxílio emergencial (formato MM/YYYY)",
        },
        # ========== BOLSA FAMÍLIA (Family Allowance) ==========
        "bolsa_familia": {
            "path": "/bolsa-familia-por-municipio",
            "required_params": ["mesAno", "codigoIbge", "pagina"],
            "max_page_size": 500,
            "description": "Bolsa Família por município (formato MM/YYYY)",
        },
        # ========== BPC (Continuous Cash Benefit) ==========
        "bpc": {
            "path": "/bpc-por-municipio",
            "required_params": ["mesAno", "codigoIbge", "pagina"],
            "max_page_size": 500,
            "description": "BPC por município (formato MM/YYYY)",
        },
        # ========== SANÇÕES (Sanctions) ==========
        "ceis": {
            "path": "/ceis",
            "required_params": ["pagina"],
            "optional_params": ["cnpj"],
            "max_page_size": 500,
            "description": "Cadastro de Empresas Inidôneas e Suspensas",
        },
        "cnep": {
            "path": "/cnep",
            "required_params": ["pagina"],
            "optional_params": ["cnpj"],
            "max_page_size": 500,
            "description": "Cadastro Nacional de Empresas Punidas",
        },
        # ========== SEGURO DEFESO (Fishing Close Season Insurance) ==========
        "seguro_defeso": {
            "path": "/seguro-defeso",
            "required_params": ["mesAno", "pagina"],
            "max_page_size": 500,
            "description": "Seguro defeso de pescadores (formato MM/YYYY)",
        },
    }

    # Known working organization codes
    KNOWN_ORGAOS = {
        "36000": "Ministério da Saúde",
        "26000": "Ministério da Educação",
        "25000": "Ministério da Economia",
        "30000": "Ministério da Justiça",
        "52000": "Ministério da Defesa",
        "35000": "Ministério das Relações Exteriores",
        "44000": "Ministério do Meio Ambiente",
    }

    def __init__(self, cache_service=None):
        """
        Initialize the Portal da Transparência service.

        Args:
            cache_service: Optional cache service (defaults to None for testing)
        """
        self.api_key = getattr(settings, "transparency_api_key", None)
        if self.api_key:
            self.api_key = (
                self.api_key.get_secret_value()
                if hasattr(self.api_key, "get_secret_value")
                else self.api_key
            )

        self.cache = cache_service  # Can work without cache
        self.client = None
        self._initialize_client()

        logger.info(
            f"Portal service initialized - API key: {'configured' if self.api_key else 'missing'}, "
            f"Cache: {'enabled' if self.cache else 'disabled'}"
        )

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
        Search government contracts with improved error handling.

        This method now properly handles the codigoOrgao requirement and
        provides better defaults for date ranges.
        """
        endpoint_info = self.ENDPOINTS["contratos"]

        # Build query parameters
        params = {
            "pagina": page,
            "tamanhoPagina": min(size, endpoint_info["max_page_size"]),
        }

        # CRITICAL: codigoOrgao is required
        if not orgao:
            orgao = endpoint_info["default_orgao"]
            logger.info(
                f"Using default orgao={orgao} ({self.KNOWN_ORGAOS.get(orgao, 'Unknown')}) - required by API"
            )

        params["codigoOrgao"] = orgao

        # Add optional filters
        if cnpj_fornecedor:
            params["cnpjFornecedor"] = cnpj_fornecedor
        if valor_minimo:
            params["valorMinimo"] = valor_minimo
        if valor_maximo:
            params["valorMaximo"] = valor_maximo
        if situacao:
            params["situacao"] = situacao
        if modalidade:
            params["modalidadeCompra"] = modalidade

        # Handle date range with safe defaults
        if not data_inicial and not data_final:
            # Use a safe, known-good date range
            # Portal data is typically 2-3 months behind
            data_final = date(2024, 10, 31)  # Safe end date
            data_inicial = data_final - timedelta(days=30)
            logger.info(f"Using safe default dates: {data_inicial} to {data_final}")

        if data_inicial:
            params["dataInicial"] = data_inicial.strftime("%d/%m/%Y")
        if data_final:
            params["dataFinal"] = data_final.strftime("%d/%m/%Y")

        # Try cache if available
        cache_key = f"contracts:{urlencode(params)}"
        if self.cache:
            try:
                cached = await self.cache.get(cache_key)
                if cached:
                    logger.info("Returning cached contracts data")
                    return cached
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")

        # Check for API key
        if not self.api_key:
            logger.warning("No API key - returning demo data")
            return self._get_demo_contracts(params)

        try:
            # Make API request
            response = await self.client.get(endpoint_info["path"], params=params)

            if response.status_code == 403:
                logger.error("API key rejected (403 Forbidden)")
                return self._get_demo_contracts_with_warning(params, "Invalid API key")

            response.raise_for_status()
            data = response.json()

            # Handle different response formats
            if isinstance(data, list):
                contratos = data
                total = len(data)
            else:
                contratos = data.get("resultado", [])
                total = data.get("quantidadeTotal", len(contratos))

            result = {
                "contratos": contratos,
                "total": total,
                "pagina": page,
                "tamanho_pagina": size,
                "orgao_consultado": orgao,
                "orgao_nome": self.KNOWN_ORGAOS.get(orgao, "Unknown"),
                "timestamp": datetime.now(UTC).isoformat(),
                "source": "portal_transparencia_api",
                "api_status": "ok",
            }

            # Try to cache if available
            if self.cache:
                try:
                    await self.cache.set(cache_key, result, ttl=3600)
                except Exception as e:
                    logger.warning(f"Cache write failed: {e}")

            logger.info(
                f"Successfully fetched {len(contratos)} contracts from Portal API "
                f"(orgao: {orgao}, total available: {total})"
            )

            return result

        except httpx.HTTPStatusError as e:
            error_detail = self._parse_error_response(e.response)
            logger.error(
                f"API error {e.response.status_code}: {error_detail}",
                extra={"status_code": e.response.status_code, "detail": error_detail},
            )

            # Return demo data with error info
            return self._get_demo_contracts_with_warning(
                params, f"API Error {e.response.status_code}: {error_detail}"
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching contracts: {e}")
            return self._get_demo_contracts_with_warning(params, str(e))

    def _parse_error_response(self, response) -> str:
        """Parse error details from API response."""
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                return (
                    error_data.get("detail")
                    or error_data.get("message")
                    or error_data.get("Erro na API")
                    or str(error_data)
                )
            return str(error_data)
        except:
            return response.text[:500] if response.text else "Unknown error"

    def _get_demo_contracts(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get realistic demo contracts when API is unavailable."""
        orgao = params.get("codigoOrgao", "36000")
        orgao_nome = self.KNOWN_ORGAOS.get(orgao, "Órgão Desconhecido")

        demo_contracts = [
            {
                "id": 698621306 + i,
                "numero": f"00{38 + i:03d}2024",
                "objeto": f"Aquisição de {item} para {orgao_nome}",
                "numeroProcesso": f"23000.00{1234 + i:04d}/2024-{10 + i:02d}",
                "fundamentoLegal": "Lei 14.133/2021",
                "dataAssinatura": "2024-01-15",
                "dataVigenciaInicio": "2024-01-20",
                "dataVigenciaFim": "2025-01-20",
                "valorInicial": 250000.00 * (i + 1),
                "situacao": "Ativo",
                "modalidadeCompra": "Pregão Eletrônico",
                "codigoOrgao": orgao,
                "nomeOrgao": orgao_nome,
                "cnpjFornecedor": f"{10 + i:02d}.345.678/0001-90",
                "nomeFornecedor": f"Empresa {i + 1} Ltda",
            }
            for i, item in enumerate(
                [
                    "medicamentos essenciais",
                    "equipamentos médicos",
                    "material hospitalar",
                    "serviços de manutenção",
                    "insumos laboratoriais",
                ]
            )
        ]

        # Filter by orgao if different
        if orgao != "36000":
            # Generate different demo data for other organs
            demo_contracts = demo_contracts[:2]  # Less data for other organs

        return {
            "contratos": demo_contracts[: params.get("tamanhoPagina", 100)],
            "total": len(demo_contracts),
            "pagina": params.get("pagina", 1),
            "tamanho_pagina": params.get("tamanhoPagina", 100),
            "orgao_consultado": orgao,
            "orgao_nome": orgao_nome,
            "timestamp": datetime.now(UTC).isoformat(),
            "source": "demo_data",
            "api_status": "unavailable",
            "demo_mode": True,
        }

    def _get_demo_contracts_with_warning(
        self, params: dict[str, Any], warning: str
    ) -> dict[str, Any]:
        """Get demo contracts with warning message."""
        result = self._get_demo_contracts(params)
        result["warning"] = warning
        result["fallback_reason"] = warning
        return result

    async def search_servidor_remuneracao(
        self,
        cpf: Optional[str] = None,
        nome: Optional[str] = None,
        mes_ano: Optional[str] = None,
        page: int = 1,
        size: int = 100,
    ) -> dict[str, Any]:
        """
        Search public servant salary by CPF or name.

        CRITICAL: This is the endpoint needed for salary queries like
        "Quanto ganha a professora Aracele Garcia de Oliveira Fassbinder?"

        Args:
            cpf: CPF do servidor (11 digits, optional if nome provided)
            nome: Nome do servidor (optional if cpf provided)
            mes_ano: Mês/Ano no formato MM/YYYY (optional, defaults to last month)
            page: Página (default 1)
            size: Tamanho da página (max 500)

        Returns:
            Dict with servidor salary data and traceability metadata
        """
        if not cpf and not nome:
            raise ValueError("Either cpf or nome must be provided")

        # Default to last month if not specified
        if not mes_ano:
            today = datetime.now(UTC)
            last_month = today - timedelta(days=30)
            mes_ano = last_month.strftime("%m/%Y")
            logger.info(f"Using default mes_ano: {mes_ano}")

        # STEP 1: If only nome provided, first search for servidor to get CPF
        if not cpf and nome:
            logger.info(f"Searching servidor by name: {nome}")
            servidor_search_result = await self._search_servidor_by_name(
                nome, page, size
            )

            if not servidor_search_result.get("servidores"):
                logger.warning(f"No servidor found with name: {nome}")
                return {
                    "servidor": None,
                    "remuneracao": None,
                    "error": f"Servidor não encontrado: {nome}",
                    "mes_ano": mes_ano,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "source": "portal_transparencia_api",
                    "traceability": {
                        "query": {"nome": nome, "mes_ano": mes_ano},
                        "steps": ["search_by_name"],
                        "apis_called": ["/servidores"],
                        "result": "not_found",
                    },
                }

            # Get first matching servidor
            servidor = servidor_search_result["servidores"][0]
            cpf = servidor.get("cpf")
            logger.info(f"Found servidor: {servidor.get('nome')} (CPF: {cpf})")

        # STEP 2: Now fetch remuneracao with CPF
        endpoint_info = self.ENDPOINTS["servidores_remuneracao"]
        path = endpoint_info["path"].replace("{cpf}", cpf)

        params = {
            "mesAno": mes_ano,
            "pagina": page,
            "tamanhoPagina": min(size, endpoint_info["max_page_size"]),
        }

        # Try cache if available
        cache_key = f"remuneracao:{cpf}:{mes_ano}"
        if self.cache:
            try:
                cached = await self.cache.get(cache_key)
                if cached:
                    logger.info(f"Returning cached salary data for CPF {cpf}")
                    return cached
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")

        # Check for API key
        if not self.api_key:
            logger.warning("No API key - cannot fetch real salary data")
            return {
                "servidor": None,
                "remuneracao": None,
                "error": "API key not configured",
                "mes_ano": mes_ano,
                "timestamp": datetime.now(UTC).isoformat(),
                "source": "demo_data",
                "demo_mode": True,
            }

        try:
            # Make API request
            logger.info(f"Fetching salary data: {path} with params {params}")
            response = await self.client.get(path, params=params)

            if response.status_code == 403:
                logger.error(f"API key rejected (403 Forbidden) for endpoint {path}")
                return {
                    "servidor": None,
                    "remuneracao": None,
                    "error": "Invalid API key or unauthorized endpoint",
                    "mes_ano": mes_ano,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "source": "portal_transparencia_api",
                    "api_status": "forbidden",
                }

            if response.status_code == 404:
                logger.warning(f"No salary data found for CPF {cpf} in {mes_ano}")
                return {
                    "servidor": None,
                    "remuneracao": None,
                    "error": f"Nenhuma remuneração encontrada para o período {mes_ano}",
                    "cpf": cpf,
                    "mes_ano": mes_ano,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "source": "portal_transparencia_api",
                    "api_status": "not_found",
                }

            response.raise_for_status()
            data = response.json()

            # Handle different response formats
            if isinstance(data, list):
                remuneracao_list = data
            else:
                remuneracao_list = data.get("resultado", [data])

            result = {
                "servidor": {
                    "cpf": cpf,
                    "nome": (
                        nome or servidor.get("nome") if "servidor" in locals() else None
                    ),
                },
                "remuneracao": remuneracao_list,
                "mes_ano": mes_ano,
                "pagina": page,
                "tamanho_pagina": size,
                "timestamp": datetime.now(UTC).isoformat(),
                "source": "portal_transparencia_api",
                "api_status": "ok",
                "traceability": {
                    "query": {"cpf": cpf, "nome": nome, "mes_ano": mes_ano},
                    "steps": (
                        ["search_by_name", "fetch_remuneracao"]
                        if nome
                        else ["fetch_remuneracao"]
                    ),
                    "apis_called": ["/servidores", path] if nome else [path],
                    "result": "success",
                    "total_records": len(remuneracao_list),
                },
            }

            # Try to cache if available
            if self.cache:
                try:
                    await self.cache.set(cache_key, result, ttl=86400)  # 24h cache
                except Exception as e:
                    logger.warning(f"Cache write failed: {e}")

            logger.info(
                f"Successfully fetched salary data for CPF {cpf}: {len(remuneracao_list)} records"
            )

            return result

        except httpx.HTTPStatusError as e:
            error_detail = self._parse_error_response(e.response)
            logger.error(
                f"API error {e.response.status_code}: {error_detail}",
                extra={"status_code": e.response.status_code, "detail": error_detail},
            )

            return {
                "servidor": None,
                "remuneracao": None,
                "error": f"API Error {e.response.status_code}: {error_detail}",
                "cpf": cpf,
                "mes_ano": mes_ano,
                "timestamp": datetime.now(UTC).isoformat(),
                "source": "portal_transparencia_api",
                "api_status": "error",
            }

        except Exception as e:
            logger.error(f"Unexpected error fetching salary: {e}")
            return {
                "servidor": None,
                "remuneracao": None,
                "error": str(e),
                "cpf": cpf,
                "mes_ano": mes_ano,
                "timestamp": datetime.now(UTC).isoformat(),
                "source": "portal_transparencia_api",
                "api_status": "error",
            }

    async def _search_servidor_by_name(
        self, nome: str, page: int = 1, size: int = 100
    ) -> dict[str, Any]:
        """
        Internal method to search servidor by name.

        This is used as a helper for salary queries when only name is provided.
        """
        endpoint_info = self.ENDPOINTS["servidores"]

        params = {
            "nome": nome,
            "pagina": page,
            "tamanhoPagina": min(size, endpoint_info["max_page_size"]),
        }

        logger.info(f"Searching servidor by name: {nome}")

        try:
            response = await self.client.get(endpoint_info["path"], params=params)

            if response.status_code == 403:
                logger.error("API key rejected for servidor search")
                return {"servidores": [], "error": "Invalid API key"}

            response.raise_for_status()
            data = response.json()

            # Handle different response formats
            if isinstance(data, list):
                servidores = data
            else:
                servidores = data.get("resultado", [])

            logger.info(f"Found {len(servidores)} servidores matching '{nome}'")

            return {
                "servidores": servidores,
                "total": len(servidores),
                "pagina": page,
                "tamanho_pagina": size,
                "timestamp": datetime.now(UTC).isoformat(),
                "source": "portal_transparencia_api",
            }

        except Exception as e:
            logger.error(f"Error searching servidor by name: {e}")
            return {"servidores": [], "error": str(e)}

    async def test_connection(self) -> dict[str, Any]:
        """
        Test Portal da Transparência API connectivity and configuration.

        Returns detailed status information.
        """
        status = {
            "api_configured": bool(self.api_key),
            "endpoints_tested": {},
            "overall_status": "unknown",
        }

        if not self.api_key:
            status["overall_status"] = "no_api_key"
            status["message"] = "API key not configured - demo mode only"
            return status

        # Test contratos endpoint (most reliable)
        try:
            result = await self.search_contracts(orgao="36000", page=1, size=1)

            if result.get("api_status") == "ok":
                status["endpoints_tested"]["contratos"] = "working"
                status["overall_status"] = "operational"
            else:
                status["endpoints_tested"]["contratos"] = "fallback"
                status["overall_status"] = "degraded"

        except Exception as e:
            status["endpoints_tested"]["contratos"] = f"error: {str(e)}"
            status["overall_status"] = "error"

        return status

    async def get_available_orgaos(self) -> list[dict[str, str]]:
        """Get list of available organization codes."""
        return [{"codigo": k, "nome": v} for k, v in self.KNOWN_ORGAOS.items()]

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


# Create a singleton instance
improved_portal_service = None


def get_improved_portal_service(cache_service=None):
    """Get or create the improved portal service."""
    global improved_portal_service
    if improved_portal_service is None:
        improved_portal_service = ImprovedPortalTransparenciaService(cache_service)
    return improved_portal_service


# Create the default instance for backward compatibility
portal_transparencia = get_improved_portal_service()
