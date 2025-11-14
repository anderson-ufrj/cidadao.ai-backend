"""
PNCP API Client

Client for Portal Nacional de Contratações Públicas (PNCP).
Provides access to public procurement data mandated by Law 14.133/2021.

API Documentation: https://pncp.gov.br/api/consulta/swagger-ui/index.html
Base URL: https://pncp.gov.br/api/consulta/v1

Author: Anderson Henrique da Silva
Created: 2025-10-14
License: Proprietary - All rights reserved
"""

import hashlib
import json
from datetime import datetime
from functools import wraps
from typing import Any, Optional

import httpx
from pydantic import BaseModel

from src.core import get_logger

from .exceptions import NetworkError, ServerError, TimeoutError, exception_from_response
from .metrics import FederalAPIMetrics
from .retry import retry_with_backoff

logger = get_logger(__name__)


def cache_with_ttl(ttl_seconds: int = 3600):
    """Decorator for caching PNCP API calls with TTL."""

    def decorator(func):
        cache = {}
        cache_times = {}

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            key_parts = [func.__name__]

            for arg in args[1:]:  # Skip 'self'
                if isinstance(arg, (str, int, float, bool)):
                    key_parts.append(str(arg))
                elif isinstance(arg, (list, dict)):
                    key_parts.append(
                        hashlib.md5(
                            json.dumps(arg, sort_keys=True).encode()
                        ).hexdigest()[:8]
                    )

            cache_key = "_".join(key_parts)

            # Check cache validity
            current_time = datetime.now().timestamp()
            if cache_key in cache:
                cached_time = cache_times.get(cache_key, 0)
                if current_time - cached_time < ttl_seconds:
                    logger.debug(f"PNCP cache hit: {cache_key}")
                    FederalAPIMetrics.record_cache_operation(
                        api_name="PNCP", operation="read", result="hit"
                    )
                    return cache[cache_key]

            # Cache miss
            FederalAPIMetrics.record_cache_operation(
                api_name="PNCP", operation="read", result="miss"
            )

            # Calculate and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = result
            cache_times[cache_key] = current_time

            # Record cache write
            FederalAPIMetrics.record_cache_operation(
                api_name="PNCP", operation="write", result="success"
            )

            # Update cache size gauge
            FederalAPIMetrics.update_cache_size(
                api_name="PNCP", cache_type="memory", size=len(cache)
            )

            return result

        return wrapper

    return decorator


class ContractPublication(BaseModel):
    """Contract publication data from PNCP."""

    sequencialCompra: Optional[int] = None
    numeroCompra: Optional[str] = None
    anoCompra: Optional[int] = None
    orgaoEntidade: Optional[dict[str, Any]] = None
    unidadeOrgao: Optional[dict[str, Any]] = None
    modalidadeId: Optional[int] = None
    modalidadeNome: Optional[str] = None
    modoDisputaId: Optional[int] = None
    modoDisputaNome: Optional[str] = None
    situacaoCompraId: Optional[int] = None
    situacaoCompraNome: Optional[str] = None
    numeroControlePNCP: Optional[str] = None
    linkSistemaOrigem: Optional[str] = None
    dataPublicacaoPncp: Optional[str] = None
    dataAberturaProposta: Optional[str] = None
    dataEncerramentoProposta: Optional[str] = None
    objetoCompra: Optional[str] = None
    informacaoComplementar: Optional[str] = None
    valorTotalEstimado: Optional[float] = None
    valorTotalHomologado: Optional[float] = None
    orcamentoSigilosoCodigo: Optional[int] = None
    orcamentoSigilosoDescricao: Optional[str] = None

    class Config:
        populate_by_name = True


class AnnualProcurementPlan(BaseModel):
    """Annual procurement plan item from PNCP."""

    orgaoCnpj: Optional[str] = None
    anoPlano: Optional[int] = None
    sequencialItem: Optional[int] = None
    codigoCatmat: Optional[str] = None
    descricaoItem: Optional[str] = None
    unidadeFornecimento: Optional[str] = None
    quantidadeEstimada: Optional[float] = None
    valorUnitarioEstimado: Optional[float] = None
    valorTotalEstimado: Optional[float] = None
    dataInclusao: Optional[str] = None

    class Config:
        populate_by_name = True


class PriceRegistration(BaseModel):
    """Price registration record from PNCP."""

    numeroControlePNCP: Optional[str] = None
    orgaoEntidade: Optional[dict[str, Any]] = None
    numeroAta: Optional[str] = None
    anoAta: Optional[int] = None
    dataPublicacaoPncp: Optional[str] = None
    dataVigenciaInicio: Optional[str] = None
    dataVigenciaFim: Optional[str] = None
    objetoAta: Optional[str] = None
    situacaoAtaId: Optional[int] = None
    situacaoAtaNome: Optional[str] = None
    valorTotalEstimado: Optional[float] = None

    class Config:
        populate_by_name = True


class PNCPClient:
    """
    Client for Portal Nacional de Contratações Públicas (PNCP).

    PNCP is the mandatory national portal for all public procurement in Brazil,
    established by Law 14.133/2021 (Nova Lei de Licitações).

    Features:
    - No authentication required for consultation APIs
    - Access to all federal, state, and municipal procurement data
    - Standardized data format across all government levels
    - Real-time procurement opportunities

    API Documentation: https://pncp.gov.br/api/consulta/swagger-ui/index.html
    """

    BASE_URL = "https://pncp.gov.br/api/consulta/v1"

    # Procurement modality codes (modalidade de contratação)
    MODALITIES = {
        "pregao_eletronico": 6,  # Electronic bidding (most common)
        "concorrencia_eletronica": 1,  # Electronic competition
        "concorrencia": 2,  # Competition
        "concurso": 3,  # Contest
        "leilao_eletronico": 4,  # Electronic auction
        "leilao": 5,  # Auction
        "dialogo_competitivo": 7,  # Competitive dialogue
        "credenciamento": 8,  # Accreditation
        "pre_qualificacao": 9,  # Pre-qualification
        "manifestacao_interesse": 10,  # Expression of interest
    }

    # Procurement situation codes
    SITUATIONS = {
        "publicada": 1,  # Published
        "em_andamento": 2,  # In progress
        "homologada": 3,  # Approved
        "revogada": 4,  # Revoked
        "suspensa": 5,  # Suspended
        "cancelada": 6,  # Cancelled
        "deserta": 7,  # Deserted
        "fracassada": 8,  # Failed
    }

    def __init__(self, timeout: int = 30):
        """
        Initialize PNCP API client.

        Args:
            timeout: Request timeout in seconds
        """
        self.base_url = self.BASE_URL
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
        self.logger = get_logger(__name__)
        self.logger.info("PNCP API client initialized")

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    @retry_with_backoff(max_attempts=3, base_delay=1.0, max_delay=30.0)
    async def _make_request(
        self, url: str, method: str = "GET", **kwargs
    ) -> dict[str, Any] | list[Any]:
        """
        Make HTTP request with automatic retry and error handling.

        Args:
            url: Request URL
            method: HTTP method
            **kwargs: Additional arguments for httpx request

        Returns:
            JSON response data

        Raises:
            NetworkError: On connection issues
            TimeoutError: On request timeout
            ServerError: On server errors (5xx)
            FederalAPIError: On other API errors
        """
        import time

        start_time = time.time()
        status_code = 500
        status = "error"
        endpoint = url.split("/")[-1] if "/" in url else url

        # Increment active requests
        FederalAPIMetrics.increment_active_requests("PNCP")

        try:
            self.logger.debug(f"Making {method} request to {url}")

            if method.upper() == "GET":
                response = await self.client.get(url, **kwargs)
            elif method.upper() == "POST":
                response = await self.client.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            status_code = response.status_code

            # Record response size
            response_size = len(response.content) if hasattr(response, "content") else 0
            FederalAPIMetrics.record_response_size(
                api_name="PNCP", endpoint=endpoint, size_bytes=response_size
            )

            # Check for HTTP errors
            if response.status_code >= 500:
                FederalAPIMetrics.record_error(
                    api_name="PNCP", error_type="ServerError", retryable=True
                )
                raise ServerError(
                    f"Server error: {response.status_code}",
                    api_name="PNCP",
                    status_code=response.status_code,
                    response_data={"url": url},
                )
            elif response.status_code >= 400:
                retryable = response.status_code == 429
                FederalAPIMetrics.record_error(
                    api_name="PNCP",
                    error_type=f"ClientError_{response.status_code}",
                    retryable=retryable,
                )
                raise exception_from_response(
                    response.status_code,
                    f"Client error: {response.status_code}",
                    api_name="PNCP",
                    response_data={"url": url},
                )

            # Parse JSON response
            try:
                data = response.json()
                status = "success"
                return data
            except Exception as e:
                self.logger.error(f"Failed to parse JSON response: {e}")
                status = "error"
                FederalAPIMetrics.record_error(
                    api_name="PNCP", error_type="JSONParseError", retryable=False
                )
                raise

        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout: {url}")
            status = "timeout"
            status_code = 0

            FederalAPIMetrics.record_timeout(
                api_name="PNCP", method=method, timeout_seconds=self.timeout
            )
            FederalAPIMetrics.record_error(
                api_name="PNCP", error_type="TimeoutError", retryable=True
            )

            raise TimeoutError(
                "Request timed out",
                api_name="PNCP",
                timeout_seconds=self.timeout,
                original_error=e,
            )
        except httpx.NetworkError as e:
            self.logger.error(f"Network error: {url}")
            status = "network_error"
            status_code = 0

            FederalAPIMetrics.record_error(
                api_name="PNCP", error_type="NetworkError", retryable=True
            )

            raise NetworkError(
                f"Network error: {str(e)}", api_name="PNCP", original_error=e
            )
        except (ServerError, TimeoutError, NetworkError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in _make_request: {e}", exc_info=True)
            status = "error"
            FederalAPIMetrics.record_error(
                api_name="PNCP", error_type=type(e).__name__, retryable=False
            )
            raise
        finally:
            # Always record request metrics
            duration = time.time() - start_time
            FederalAPIMetrics.record_request(
                api_name="PNCP",
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=duration,
                status=status,
            )

            # Decrement active requests
            FederalAPIMetrics.decrement_active_requests("PNCP")

    @cache_with_ttl(ttl_seconds=3600)  # 1 hour cache
    async def search_contracts(
        self,
        start_date: str,
        end_date: str,
        modality_code: int = 6,  # Default to "pregao_eletronico" (most common)
        state: Optional[str] = None,
        page_size: int = 50,
        page: int = 1,
    ) -> list[ContractPublication]:
        """
        Search for contract publications.

        Args:
            start_date: Start date (yyyyMMdd) - REQUIRED
            end_date: End date (yyyyMMdd) - REQUIRED
            modality_code: Procurement modality code (use MODALITIES dict). Default: 6 (pregão eletrônico)
            state: State abbreviation (UF) - e.g., "SP", "RJ"
            page_size: Results per page (min: 10, max: 500)
            page: Page number

        Returns:
            List of contract publications

        Example:
            >>> async with PNCPClient() as client:
            >>>     # Search electronic bidding in São Paulo
            >>>     contracts = await client.search_contracts(
            >>>         start_date="20240101",
            >>>         end_date="20240131",
            >>>         modality_code=client.MODALITIES["pregao_eletronico"],
            >>>         state="SP"
            >>>     )
        """
        # Validate page_size (API requires >= 10)
        if page_size < 10:
            self.logger.warning(f"page_size {page_size} < 10, adjusting to 10")
            page_size = 10
        elif page_size > 500:
            self.logger.warning(f"page_size {page_size} > 500, adjusting to 500")
            page_size = 500

        self.logger.info(
            f"Searching contracts: dates={start_date} to {end_date}, "
            f"modality={modality_code}, state={state}"
        )

        url = f"{self.BASE_URL}/contratacoes/publicacao"

        params = {
            "dataInicial": start_date,
            "dataFinal": end_date,
            "codigoModalidadeContratacao": modality_code,
            "tamanhoPagina": page_size,
            "pagina": page,
        }

        if state:
            params["uf"] = state.upper()

        data = await self._make_request(url, params=params)

        # PNCP returns paginated results with structure:
        # {"data": [...], "totalRegistros": N, "totalPaginas": N, ...}
        items = data.get("data", []) if isinstance(data, dict) else data

        FederalAPIMetrics.record_data_fetched(
            api_name="PNCP", data_type="contracts", record_count=len(items)
        )

        contracts = [ContractPublication(**item) for item in items]

        self.logger.info(f"Found {len(contracts)} contract publications")

        return contracts

    @cache_with_ttl(ttl_seconds=7200)  # 2 hours cache
    async def get_annual_plan(
        self, cnpj: str, year: int, page_size: int = 100, page: int = 1
    ) -> list[AnnualProcurementPlan]:
        """
        Get annual procurement plan for an organization.

        Args:
            cnpj: Organization CNPJ (with or without formatting)
            year: Plan year
            page_size: Results per page
            page: Page number

        Returns:
            List of procurement plan items

        Example:
            >>> async with PNCPClient() as client:
            >>>     plan = await client.get_annual_plan(
            >>>         cnpj="00.000.000/0001-00",
            >>>         year=2024
            >>>     )
        """
        # Remove formatting from CNPJ
        cnpj_digits = "".join(filter(str.isdigit, cnpj))

        self.logger.info(f"Fetching annual plan: CNPJ={cnpj_digits}, year={year}")

        url = f"{self.BASE_URL}/plano-contratacoes-anual"

        params = {
            "orgaoCnpj": cnpj_digits,
            "anoPlano": year,
            "tamanhoPagina": page_size,
            "pagina": page,
        }

        data = await self._make_request(url, params=params)

        # PNCP returns paginated results with "data" field
        items = data.get("data", []) if isinstance(data, dict) else data

        FederalAPIMetrics.record_data_fetched(
            api_name="PNCP", data_type="annual_plan", record_count=len(items)
        )

        plan_items = [AnnualProcurementPlan(**item) for item in items]

        self.logger.info(f"Found {len(plan_items)} procurement plan items")

        return plan_items

    @cache_with_ttl(ttl_seconds=7200)  # 2 hours cache
    async def search_price_registrations(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        state: Optional[str] = None,
        page_size: int = 50,
        page: int = 1,
    ) -> list[PriceRegistration]:
        """
        Search for price registration records (Ata de Registro de Preço).

        Args:
            start_date: Start date (YYYY-MM-DD or dd/MM/yyyy)
            end_date: End date (YYYY-MM-DD or dd/MM/yyyy)
            state: State abbreviation (UF)
            page_size: Results per page
            page: Page number

        Returns:
            List of price registration records

        Example:
            >>> async with PNCPClient() as client:
            >>>     registrations = await client.search_price_registrations(
            >>>         start_date="01/01/2024",
            >>>         end_date="31/01/2024",
            >>>         state="RJ"
            >>>     )
        """
        self.logger.info(
            f"Searching price registrations: dates={start_date} to {end_date}, state={state}"
        )

        url = f"{self.BASE_URL}/atas-registro-preco"

        params = {"tamanhoPagina": page_size, "pagina": page}

        if start_date:
            params["dataInicial"] = start_date
        if end_date:
            params["dataFinal"] = end_date
        if state:
            params["uf"] = state.upper()

        data = await self._make_request(url, params=params)

        # PNCP returns paginated results with "data" field
        items = data.get("data", []) if isinstance(data, dict) else data

        FederalAPIMetrics.record_data_fetched(
            api_name="PNCP", data_type="price_registration", record_count=len(items)
        )

        registrations = [PriceRegistration(**item) for item in items]

        self.logger.info(f"Found {len(registrations)} price registration records")

        return registrations

    async def get_contract_details(self, control_number: str) -> dict[str, Any]:
        """
        Get detailed information about a specific contract.

        Args:
            control_number: PNCP control number (numeroControlePNCP)

        Returns:
            Detailed contract information

        Example:
            >>> async with PNCPClient() as client:
            >>>     details = await client.get_contract_details("12345678901234567890")
        """
        self.logger.info(f"Fetching contract details: {control_number}")

        url = f"{self.BASE_URL}/contratacoes/{control_number}"

        data = await self._make_request(url)

        FederalAPIMetrics.record_data_fetched(
            api_name="PNCP", data_type="contract_detail", record_count=1
        )

        self.logger.info(f"Fetched contract details for {control_number}")

        return data
