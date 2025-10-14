"""
Compras.gov.br API Client

Client for Brazilian Government Procurement API.
Provides access to historical bidding, contracts, suppliers, and procurement data.

API Documentation: https://compras.dados.gov.br/docs/home.html
Base URL: http://compras.dados.gov.br

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
from pydantic import BaseModel, Field

from src.core import get_logger

from .exceptions import NetworkError, ServerError, TimeoutError, exception_from_response
from .metrics import FederalAPIMetrics
from .retry import retry_with_backoff

logger = get_logger(__name__)


def cache_with_ttl(ttl_seconds: int = 3600):
    """Decorator for caching Compras.gov.br API calls with TTL."""

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
                    logger.debug(f"Compras.gov cache hit: {cache_key}")
                    FederalAPIMetrics.record_cache_operation(
                        api_name="ComprasGov", operation="read", result="hit"
                    )
                    return cache[cache_key]

            # Cache miss
            FederalAPIMetrics.record_cache_operation(
                api_name="ComprasGov", operation="read", result="miss"
            )

            # Calculate and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = result
            cache_times[cache_key] = current_time

            # Record cache write
            FederalAPIMetrics.record_cache_operation(
                api_name="ComprasGov", operation="write", result="success"
            )

            # Update cache size gauge
            FederalAPIMetrics.update_cache_size(
                api_name="ComprasGov", cache_type="memory", size=len(cache)
            )

            return result

        return wrapper

    return decorator


class Organization(BaseModel):
    """Organization (órgão) data."""

    codigo: Optional[str] = None
    nome: Optional[str] = None
    cnpj: Optional[str] = None
    esfera: Optional[str] = None  # Federal, Estadual, Municipal
    poder: Optional[str] = None  # Executivo, Legislativo, Judiciário

    class Config:
        populate_by_name = True


class Supplier(BaseModel):
    """Supplier (fornecedor) data."""

    cnpj_cpf: Optional[str] = Field(default=None, alias="cnpj_cpf")
    nome: Optional[str] = None
    uf: Optional[str] = None
    municipio: Optional[str] = None
    habilitado: Optional[bool] = None

    class Config:
        populate_by_name = True


class Bidding(BaseModel):
    """Bidding (licitação) data."""

    codigo: Optional[str] = None
    numero: Optional[str] = None
    ano: Optional[int] = None
    modalidade: Optional[str] = None  # Pregão, Concorrência, Tomada de Preços, etc
    objeto: Optional[str] = None
    situacao: Optional[str] = None
    data_abertura: Optional[str] = Field(default=None, alias="data_abertura")
    data_homologacao: Optional[str] = Field(default=None, alias="data_homologacao")
    valor_estimado: Optional[float] = Field(default=None, alias="valor_estimado")
    valor_homologado: Optional[float] = Field(default=None, alias="valor_homologado")
    orgao_codigo: Optional[str] = Field(default=None, alias="orgao_codigo")
    orgao_nome: Optional[str] = Field(default=None, alias="orgao_nome")

    class Config:
        populate_by_name = True


class Contract(BaseModel):
    """Contract (contrato) data."""

    numero: Optional[str] = None
    ano: Optional[int] = None
    objeto: Optional[str] = None
    situacao: Optional[str] = None
    data_assinatura: Optional[str] = Field(default=None, alias="data_assinatura")
    data_vigencia_inicio: Optional[str] = Field(
        default=None, alias="data_vigencia_inicio"
    )
    data_vigencia_fim: Optional[str] = Field(default=None, alias="data_vigencia_fim")
    valor_inicial: Optional[float] = Field(default=None, alias="valor_inicial")
    valor_global: Optional[float] = Field(default=None, alias="valor_global")
    fornecedor_cnpj: Optional[str] = Field(default=None, alias="fornecedor_cnpj")
    fornecedor_nome: Optional[str] = Field(default=None, alias="fornecedor_nome")
    orgao_codigo: Optional[str] = Field(default=None, alias="orgao_codigo")
    orgao_nome: Optional[str] = Field(default=None, alias="orgao_nome")

    class Config:
        populate_by_name = True


class Material(BaseModel):
    """Material (item) data."""

    codigo: Optional[str] = None
    descricao: Optional[str] = None
    unidade_fornecimento: Optional[str] = Field(
        default=None, alias="unidade_fornecimento"
    )
    grupo: Optional[str] = None
    sustentavel: Optional[bool] = None

    class Config:
        populate_by_name = True


class Service(BaseModel):
    """Service data."""

    codigo: Optional[str] = None
    descricao: Optional[str] = None
    grupo: Optional[str] = None

    class Config:
        populate_by_name = True


class ComprasGovClient:
    """
    Client for Compras.gov.br API - Brazilian Government Procurement.

    Provides access to historical procurement data including:
    - Biddings (licitações) - auctions, competitions, etc.
    - Contracts (contratos) - until 2020 and from 2021
    - Suppliers (fornecedores) - company registry
    - Materials and Services catalogs
    - Annual Procurement Plans (PGC)

    Note: For data from 2023 onwards, use PNCP API instead.

    Features:
    - No authentication required
    - Multiple output formats (JSON, XML, CSV, HTML)
    - HATEOAS-style navigation with links
    - ODBL license (Open Database License)

    API Documentation: https://compras.dados.gov.br/docs/home.html
    """

    BASE_URL = "http://compras.dados.gov.br"

    # API modules
    MODULES = {
        "biddings": "licitacoes",
        "contracts_old": "contratos",  # Until 2020
        "contracts_new": "contratacoes",  # From 2021
        "suppliers": "fornecedores",
        "materials": "materiais",
        "services": "servicos",
        "annual_plan": "pgc",
    }

    # Bidding modalities
    MODALITIES = {
        "pregao": 1,  # Auction (most common)
        "concorrencia": 2,  # Competition
        "tomada_precos": 3,  # Price quotation
        "convite": 4,  # Invitation
        "concurso": 5,  # Contest
        "leilao": 6,  # Auction
    }

    def __init__(self, timeout: int = 30):
        """
        Initialize Compras.gov.br API client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
        self.logger = get_logger(__name__)
        self.logger.info("Compras.gov.br API client initialized")

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
        FederalAPIMetrics.increment_active_requests("ComprasGov")

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
                api_name="ComprasGov", endpoint=endpoint, size_bytes=response_size
            )

            # Check for HTTP errors
            if response.status_code >= 500:
                FederalAPIMetrics.record_error(
                    api_name="ComprasGov", error_type="ServerError", retryable=True
                )
                raise ServerError(
                    f"Server error: {response.status_code}",
                    api_name="ComprasGov",
                    status_code=response.status_code,
                    response_data={"url": url},
                )
            elif response.status_code >= 400:
                retryable = response.status_code == 429
                FederalAPIMetrics.record_error(
                    api_name="ComprasGov",
                    error_type=f"ClientError_{response.status_code}",
                    retryable=retryable,
                )
                raise exception_from_response(
                    response.status_code,
                    f"Client error: {response.status_code}",
                    api_name="ComprasGov",
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
                    api_name="ComprasGov", error_type="JSONParseError", retryable=False
                )
                raise

        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout: {url}")
            status = "timeout"
            status_code = 0

            FederalAPIMetrics.record_timeout(
                api_name="ComprasGov", method=method, timeout_seconds=self.timeout
            )
            FederalAPIMetrics.record_error(
                api_name="ComprasGov", error_type="TimeoutError", retryable=True
            )

            raise TimeoutError(
                "Request timed out",
                api_name="ComprasGov",
                timeout_seconds=self.timeout,
                original_error=e,
            )
        except httpx.NetworkError as e:
            self.logger.error(f"Network error: {url}")
            status = "network_error"
            status_code = 0

            FederalAPIMetrics.record_error(
                api_name="ComprasGov", error_type="NetworkError", retryable=True
            )

            raise NetworkError(
                f"Network error: {str(e)}", api_name="ComprasGov", original_error=e
            )
        except (ServerError, TimeoutError, NetworkError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in _make_request: {e}", exc_info=True)
            status = "error"
            FederalAPIMetrics.record_error(
                api_name="ComprasGov", error_type=type(e).__name__, retryable=False
            )
            raise
        finally:
            # Always record request metrics
            duration = time.time() - start_time
            FederalAPIMetrics.record_request(
                api_name="ComprasGov",
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=duration,
                status=status,
            )

            # Decrement active requests
            FederalAPIMetrics.decrement_active_requests("ComprasGov")

    @cache_with_ttl(ttl_seconds=86400)  # 24 hours cache
    async def search_organizations(
        self, name: Optional[str] = None, limit: int = 100
    ) -> list[Organization]:
        """
        Search for organizations (órgãos).

        Args:
            name: Organization name to filter
            limit: Maximum results to return

        Returns:
            List of organizations

        Example:
            >>> async with ComprasGovClient() as client:
            >>>     orgs = await client.search_organizations(name="educação")
        """
        self.logger.info(f"Searching organizations: name={name}")

        url = f"{self.BASE_URL}/{self.MODULES['biddings']}/v1/orgaos.json"

        params = {}
        if name:
            params["nome"] = name

        data = await self._make_request(url, params=params)

        # Extract items from response
        items = data.get("_embedded", {}).get("orgaos", [])[:limit]

        FederalAPIMetrics.record_data_fetched(
            api_name="ComprasGov", data_type="organizations", record_count=len(items)
        )

        organizations = [Organization(**item) for item in items]

        self.logger.info(f"Found {len(organizations)} organizations")

        return organizations

    @cache_with_ttl(ttl_seconds=3600)  # 1 hour cache
    async def search_biddings(
        self,
        organization_code: Optional[str] = None,
        modality: Optional[int] = None,
        year: Optional[int] = None,
        limit: int = 100,
    ) -> list[Bidding]:
        """
        Search for biddings (licitações).

        Args:
            organization_code: Organization code to filter
            modality: Bidding modality code (use MODALITIES dict)
            year: Year to filter
            limit: Maximum results to return

        Returns:
            List of biddings

        Example:
            >>> async with ComprasGovClient() as client:
            >>>     biddings = await client.search_biddings(
            >>>         modality=client.MODALITIES["pregao"],
            >>>         year=2022
            >>>     )
        """
        self.logger.info(
            f"Searching biddings: org={organization_code}, modality={modality}, year={year}"
        )

        url = f"{self.BASE_URL}/{self.MODULES['biddings']}/v1/licitacoes.json"

        params = {}
        if organization_code:
            params["codigo_orgao"] = organization_code
        if modality:
            params["modalidade"] = modality
        if year:
            params["ano"] = year

        data = await self._make_request(url, params=params)

        # Extract items from response
        items = data.get("_embedded", {}).get("licitacoes", [])[:limit]

        FederalAPIMetrics.record_data_fetched(
            api_name="ComprasGov", data_type="biddings", record_count=len(items)
        )

        biddings = [Bidding(**item) for item in items]

        self.logger.info(f"Found {len(biddings)} biddings")

        return biddings

    @cache_with_ttl(ttl_seconds=7200)  # 2 hours cache
    async def get_bidding_details(self, bidding_code: str) -> dict[str, Any]:
        """
        Get detailed information about a specific bidding.

        Args:
            bidding_code: Bidding code (e.g., "02000105001802012")

        Returns:
            Detailed bidding information

        Example:
            >>> async with ComprasGovClient() as client:
            >>>     details = await client.get_bidding_details("02000105001802012")
        """
        self.logger.info(f"Fetching bidding details: {bidding_code}")

        url = f"{self.BASE_URL}/{self.MODULES['biddings']}/doc/licitacao/{bidding_code}.json"

        data = await self._make_request(url)

        FederalAPIMetrics.record_data_fetched(
            api_name="ComprasGov", data_type="bidding_detail", record_count=1
        )

        self.logger.info(f"Fetched bidding details for {bidding_code}")

        return data

    @cache_with_ttl(ttl_seconds=3600)  # 1 hour cache
    async def search_suppliers(
        self, state: Optional[str] = None, name: Optional[str] = None, limit: int = 100
    ) -> list[Supplier]:
        """
        Search for suppliers (fornecedores).

        Args:
            state: State abbreviation (UF) - e.g., "SP", "RJ"
            name: Supplier name to filter
            limit: Maximum results to return

        Returns:
            List of suppliers

        Example:
            >>> async with ComprasGovClient() as client:
            >>>     suppliers = await client.search_suppliers(state="DF")
        """
        self.logger.info(f"Searching suppliers: state={state}, name={name}")

        url = f"{self.BASE_URL}/{self.MODULES['suppliers']}/v1/fornecedores.json"

        params = {}
        if state:
            params["uf"] = state.upper()
        if name:
            params["nome"] = name

        data = await self._make_request(url, params=params)

        # Extract items from response
        items = data.get("_embedded", {}).get("fornecedores", [])[:limit]

        FederalAPIMetrics.record_data_fetched(
            api_name="ComprasGov", data_type="suppliers", record_count=len(items)
        )

        suppliers = [Supplier(**item) for item in items]

        self.logger.info(f"Found {len(suppliers)} suppliers")

        return suppliers

    @cache_with_ttl(ttl_seconds=86400)  # 24 hours cache
    async def search_materials(
        self, description: Optional[str] = None, limit: int = 100
    ) -> list[Material]:
        """
        Search for materials (materiais) in the catalog.

        Args:
            description: Material description to filter
            limit: Maximum results to return

        Returns:
            List of materials

        Example:
            >>> async with ComprasGovClient() as client:
            >>>     materials = await client.search_materials(description="computador")
        """
        self.logger.info(f"Searching materials: description={description}")

        url = f"{self.BASE_URL}/{self.MODULES['materials']}/v1/materiais.json"

        params = {}
        if description:
            params["descricao"] = description

        data = await self._make_request(url, params=params)

        # Extract items from response
        items = data.get("_embedded", {}).get("materiais", [])[:limit]

        FederalAPIMetrics.record_data_fetched(
            api_name="ComprasGov", data_type="materials", record_count=len(items)
        )

        materials = [Material(**item) for item in items]

        self.logger.info(f"Found {len(materials)} materials")

        return materials

    @cache_with_ttl(ttl_seconds=86400)  # 24 hours cache
    async def search_services(
        self, description: Optional[str] = None, limit: int = 100
    ) -> list[Service]:
        """
        Search for services in the catalog.

        Args:
            description: Service description to filter
            limit: Maximum results to return

        Returns:
            List of services

        Example:
            >>> async with ComprasGovClient() as client:
            >>>     services = await client.search_services(description="manutenção")
        """
        self.logger.info(f"Searching services: description={description}")

        url = f"{self.BASE_URL}/{self.MODULES['services']}/v1/servicos.json"

        params = {}
        if description:
            params["descricao"] = description

        data = await self._make_request(url, params=params)

        # Extract items from response
        items = data.get("_embedded", {}).get("servicos", [])[:limit]

        FederalAPIMetrics.record_data_fetched(
            api_name="ComprasGov", data_type="services", record_count=len(items)
        )

        services = [Service(**item) for item in items]

        self.logger.info(f"Found {len(services)} services")

        return services

    @cache_with_ttl(ttl_seconds=3600)  # 1 hour cache
    async def search_contracts(
        self,
        organization_code: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 100,
        new_law: bool = True,
    ) -> list[Contract]:
        """
        Search for contracts (contratos).

        Args:
            organization_code: Organization code to filter
            year: Year to filter
            limit: Maximum results to return
            new_law: If True, use new law endpoint (2021+), else use old (until 2020)

        Returns:
            List of contracts

        Example:
            >>> async with ComprasGovClient() as client:
            >>>     # New law contracts (2021+)
            >>>     contracts = await client.search_contracts(year=2023)
            >>>     # Old law contracts (until 2020)
            >>>     old_contracts = await client.search_contracts(
            >>>         year=2019, new_law=False
            >>>     )
        """
        module = (
            self.MODULES["contracts_new"] if new_law else self.MODULES["contracts_old"]
        )

        self.logger.info(
            f"Searching contracts: org={organization_code}, year={year}, new_law={new_law}"
        )

        url = f"{self.BASE_URL}/{module}/v1/contratos.json"

        params = {}
        if organization_code:
            params["codigo_orgao"] = organization_code
        if year:
            params["ano"] = year

        data = await self._make_request(url, params=params)

        # Extract items from response
        items = data.get("_embedded", {}).get("contratos", [])[:limit]

        FederalAPIMetrics.record_data_fetched(
            api_name="ComprasGov", data_type="contracts", record_count=len(items)
        )

        contracts = [Contract(**item) for item in items]

        self.logger.info(f"Found {len(contracts)} contracts")

        return contracts
