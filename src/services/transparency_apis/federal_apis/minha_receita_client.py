"""
Minha Receita API Client

Client for Minha Receita - Open source CNPJ data from Receita Federal.
Provides access to company registration data without CAPTCHA.

API Documentation: https://docs.minhareceita.org
GitHub: https://github.com/cuducos/minha-receita

Author: Anderson Henrique da Silva
Created: 2025-10-14
License: Proprietary - All rights reserved
"""

import asyncio
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
    """Decorator for caching Minha Receita API calls with TTL."""

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
                    logger.debug(f"Minha Receita cache hit: {cache_key}")
                    # Record cache hit
                    FederalAPIMetrics.record_cache_operation(
                        api_name="MinhaReceita", operation="read", result="hit"
                    )
                    return cache[cache_key]

            # Cache miss - record it
            FederalAPIMetrics.record_cache_operation(
                api_name="MinhaReceita", operation="read", result="miss"
            )

            # Calculate and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = result
            cache_times[cache_key] = current_time

            # Record cache write
            FederalAPIMetrics.record_cache_operation(
                api_name="MinhaReceita", operation="write", result="success"
            )

            # Update cache size gauge
            FederalAPIMetrics.update_cache_size(
                api_name="MinhaReceita", cache_type="memory", size=len(cache)
            )

            return result

        return wrapper

    return decorator


class CNPJData(BaseModel):
    """CNPJ data model from Minha Receita."""

    cnpj: str
    razao_social: str = Field(alias="razao_social")
    nome_fantasia: Optional[str] = Field(default=None, alias="nome_fantasia")
    situacao_cadastral: int = Field(
        alias="situacao_cadastral"
    )  # Changed from str to int
    data_situacao_cadastral: Optional[str] = Field(
        default=None, alias="data_situacao_cadastral"
    )
    descricao_situacao_cadastral: Optional[str] = Field(
        default=None, alias="descricao_situacao_cadastral"
    )
    atividade_principal: Optional[Any] = Field(
        default=None, alias="atividade_principal"
    )  # Can be dict or None
    atividades_secundarias: Optional[Any] = Field(
        default=None, alias="atividades_secundarias"
    )  # Can be list or None
    natureza_juridica: Optional[str] = Field(
        default=None, alias="natureza_juridica"
    )  # Changed from dict to str
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    cep: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    data_abertura: Optional[str] = Field(default=None, alias="data_abertura")
    capital_social: Optional[float] = Field(default=None, alias="capital_social")
    qsa: Optional[list[dict[str, Any]]] = None  # Quadro Societário

    class Config:
        populate_by_name = True


class MinhaReceitaClient:
    """
    Client for Minha Receita API - Open source CNPJ data.

    Minha Receita is a civil society initiative that provides free access to
    Receita Federal data without CAPTCHA, consolidating all information into
    a single queryable database.

    Features:
    - No authentication required
    - No rate limits (be respectful)
    - Complete CNPJ data including QSA (partners)
    - Updated regularly from Receita Federal

    API Documentation: https://docs.minhareceita.org
    """

    BASE_URL = "https://minhareceita.org"

    def __init__(self, timeout: int = 30):
        """
        Initialize Minha Receita API client.

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

        self.logger.info("Minha Receita API client initialized")

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def _format_cnpj(self, cnpj: str) -> str:
        """
        Format CNPJ for API request.

        Accepts: 00.000.000/0000-00 or 00000000000000
        Returns: 00.000.000/0000-00 (formatted)
        """
        # Remove all non-digits
        digits = "".join(filter(str.isdigit, cnpj))

        if len(digits) != 14:
            raise ValueError(f"Invalid CNPJ: must have 14 digits, got {len(digits)}")

        # Format: XX.XXX.XXX/XXXX-XX
        formatted = (
            f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"
        )
        return formatted

    @retry_with_backoff(max_attempts=3, base_delay=1.0, max_delay=30.0)
    async def _make_request(
        self, url: str, method: str = "GET", **kwargs
    ) -> dict[str, Any]:
        """
        Make HTTP request with automatic retry and error handling.

        Args:
            url: Request URL
            method: HTTP method (GET, POST, etc)
            **kwargs: Additional arguments for httpx request

        Returns:
            JSON response data

        Raises:
            NetworkError: On connection/network issues
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
        FederalAPIMetrics.increment_active_requests("MinhaReceita")

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
                api_name="MinhaReceita", endpoint=endpoint, size_bytes=response_size
            )

            # Check for HTTP errors
            if response.status_code >= 500:
                error_msg = f"Server error: {response.status_code}"
                # Record error before raising
                FederalAPIMetrics.record_error(
                    api_name="MinhaReceita", error_type="ServerError", retryable=True
                )
                raise ServerError(
                    error_msg,
                    api_name="MinhaReceita",
                    status_code=response.status_code,
                    response_data={"url": url},
                )
            elif response.status_code >= 400:
                error_msg = f"Client error: {response.status_code}"
                # Record error before raising
                retryable = response.status_code == 429  # Only rate limit is retryable
                FederalAPIMetrics.record_error(
                    api_name="MinhaReceita",
                    error_type=f"ClientError_{response.status_code}",
                    retryable=retryable,
                )
                raise exception_from_response(
                    response.status_code,
                    error_msg,
                    api_name="MinhaReceita",
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
                    api_name="MinhaReceita",
                    error_type="JSONParseError",
                    retryable=False,
                )
                raise

        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout: {url}")
            status = "timeout"
            status_code = 0

            # Record timeout
            FederalAPIMetrics.record_timeout(
                api_name="MinhaReceita", method=method, timeout_seconds=self.timeout
            )
            FederalAPIMetrics.record_error(
                api_name="MinhaReceita", error_type="TimeoutError", retryable=True
            )

            raise TimeoutError(
                "Request timed out",
                api_name="MinhaReceita",
                timeout_seconds=self.timeout,
                original_error=e,
            )
        except httpx.NetworkError as e:
            self.logger.error(f"Network error: {url}")
            status = "network_error"
            status_code = 0

            # Record network error
            FederalAPIMetrics.record_error(
                api_name="MinhaReceita", error_type="NetworkError", retryable=True
            )

            raise NetworkError(
                f"Network error: {str(e)}", api_name="MinhaReceita", original_error=e
            )
        except (ServerError, TimeoutError, NetworkError):
            # Re-raise our custom exceptions as-is (they'll be caught by retry decorator)
            raise
        except Exception as e:
            # Catch-all for unexpected errors
            self.logger.error(f"Unexpected error in _make_request: {e}", exc_info=True)
            status = "error"
            FederalAPIMetrics.record_error(
                api_name="MinhaReceita", error_type=type(e).__name__, retryable=False
            )
            raise
        finally:
            # Always record request metrics
            duration = time.time() - start_time
            FederalAPIMetrics.record_request(
                api_name="MinhaReceita",
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=duration,
                status=status,
            )

            # Decrement active requests
            FederalAPIMetrics.decrement_active_requests("MinhaReceita")

    @cache_with_ttl(
        ttl_seconds=86400
    )  # 24 hours cache (CNPJ data doesn't change often)
    async def get_cnpj(self, cnpj: str) -> CNPJData:
        """
        Get complete CNPJ data.

        Args:
            cnpj: CNPJ with or without formatting (00.000.000/0000-00 or 00000000000000)

        Returns:
            Complete CNPJ data including:
            - Company identification (razao_social, nome_fantasia)
            - Registration status (situacao_cadastral)
            - Economic activity (CNAE)
            - Address
            - Partners (QSA - Quadro Societário e Administrativo)
            - Capital social

        Raises:
            ValueError: If CNPJ is invalid
            FederalAPIError: If API request fails

        Example:
            >>> async with MinhaReceitaClient() as client:
            >>>     data = await client.get_cnpj("00.000.000/0000-00")
            >>>     print(data.razao_social)
            >>>     print(data.qsa)  # Partners
        """
        # Format CNPJ
        formatted_cnpj = self._format_cnpj(cnpj)

        self.logger.info(f"Fetching CNPJ data: {formatted_cnpj}")

        # Make request
        url = f"{self.BASE_URL}/{formatted_cnpj}"
        data = await self._make_request(url)

        # Record data fetched
        FederalAPIMetrics.record_data_fetched(
            api_name="MinhaReceita", data_type="cnpj", record_count=1
        )

        # Parse into model
        cnpj_data = CNPJData(**data)

        self.logger.info(
            f"Fetched CNPJ data: {cnpj_data.razao_social} ({cnpj_data.situacao_cadastral})"
        )

        return cnpj_data

    async def get_multiple_cnpjs(
        self, cnpjs: list[str], batch_delay: float = 0.5
    ) -> dict[str, CNPJData | Exception]:
        """
        Get data for multiple CNPJs.

        Args:
            cnpjs: List of CNPJs to fetch
            batch_delay: Delay between requests in seconds (be respectful)

        Returns:
            Dict mapping CNPJ to CNPJData or Exception if failed

        Example:
            >>> async with MinhaReceitaClient() as client:
            >>>     results = await client.get_multiple_cnpjs([
            >>>         "00.000.000/0000-00",
            >>>         "11.111.111/0001-11"
            >>>     ])
            >>>     for cnpj, data in results.items():
            >>>         if isinstance(data, Exception):
            >>>             print(f"{cnpj}: ERROR - {data}")
            >>>         else:
            >>>             print(f"{cnpj}: {data.razao_social}")
        """
        self.logger.info(f"Fetching {len(cnpjs)} CNPJs")

        results = {}

        for cnpj in cnpjs:
            try:
                data = await self.get_cnpj(cnpj)
                results[cnpj] = data
            except Exception as e:
                self.logger.warning(f"Failed to fetch CNPJ {cnpj}: {e}")
                results[cnpj] = e

            # Be respectful to the API
            if batch_delay > 0:
                await asyncio.sleep(batch_delay)

        self.logger.info(
            f"Fetched {len(cnpjs)} CNPJs: {sum(1 for v in results.values() if not isinstance(v, Exception))} succeeded"
        )

        return results

    async def search_by_name(self, name: str) -> list[dict[str, Any]]:
        """
        Search companies by name.

        Note: Minha Receita API doesn't have built-in search.
        This would require either:
        1. Using a separate search index
        2. Downloading bulk CNPJ data and searching locally
        3. Using Receita Federal's official search (with CAPTCHA)

        For now, this returns an empty list with a warning.

        Args:
            name: Company name to search

        Returns:
            Empty list (not implemented)
        """
        self.logger.warning(
            "Search by name not implemented - Minha Receita API only supports direct CNPJ lookup"
        )
        return []
