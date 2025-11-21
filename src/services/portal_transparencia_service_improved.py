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
    ENDPOINTS = {
        "contratos": {
            "path": "/contratos",
            "required_params": ["codigoOrgao"],
            "max_page_size": 500,
            "default_orgao": "36000",  # Ministério da Saúde
        },
        "licitacoes": {
            "path": "/licitacoes",
            "required_params": ["codigoOrgao"],
            "max_page_size": 500,
            "max_date_range_days": 30,  # API requires max 1 month
            "default_orgao": "36000",
        },
        "despesas": {
            "path": "/despesas",
            "required_params": ["codigoOrgao", "mesAno"],
            "max_page_size": 500,
            "default_orgao": "36000",
        },
        "servidores": {
            "path": "/servidores",
            "required_params": [
                "codigoOrgaoLotacao|codigoOrgaoExercicio|cpf"
            ],  # At least one
            "max_page_size": 500,
        },
        "fornecedores": {
            "path": "/fornecedores",
            "required_params": [],
            "max_page_size": 500,
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
