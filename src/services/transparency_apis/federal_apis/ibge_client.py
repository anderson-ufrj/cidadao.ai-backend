"""
IBGE API Client

Client for Brazilian Institute of Geography and Statistics API.
Provides access to demographic, economic, and social indicators.

API Documentation: https://servicodados.ibge.gov.br/api/docs

Author: Anderson Henrique da Silva
Created: 2025-10-12
License: Proprietary - All rights reserved
"""

import asyncio
import hashlib
import json
from datetime import datetime
from functools import wraps
from typing import Any

import httpx
from pydantic import BaseModel, field_validator

from src.core import get_logger

from .exceptions import NetworkError, ServerError, TimeoutError, exception_from_response
from .metrics import FederalAPIMetrics
from .retry import retry_with_backoff

logger = get_logger(__name__)


def cache_with_ttl(ttl_seconds: int = 3600):
    """Decorator for caching IBGE API calls with TTL."""

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
                    logger.debug(f"IBGE cache hit: {cache_key}")
                    # Record cache hit
                    FederalAPIMetrics.record_cache_operation(
                        api_name="IBGE", operation="read", result="hit"
                    )
                    return cache[cache_key]

            # Cache miss - record it
            FederalAPIMetrics.record_cache_operation(
                api_name="IBGE", operation="read", result="miss"
            )

            # Calculate and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = result
            cache_times[cache_key] = current_time

            # Record cache write
            FederalAPIMetrics.record_cache_operation(
                api_name="IBGE", operation="write", result="success"
            )

            # Update cache size gauge
            FederalAPIMetrics.update_cache_size(
                api_name="IBGE", cache_type="memory", size=len(cache)
            )

            return result

        return wrapper

    return decorator


class IBGELocation(BaseModel):
    """Geographic location representation."""

    id: str
    nome: str
    regiao: dict[str, Any] | None = None
    microrregiao: dict[str, Any] | None = None
    mesorregiao: dict[str, Any] | None = None

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id_to_str(cls, v):
        """Convert integer IDs from IBGE API to strings."""
        return str(v) if isinstance(v, int) else v


class IBGEIndicator(BaseModel):
    """IBGE indicator representation."""

    id: str
    nome: str
    unidade: str | None = None
    periodicidade: str | None = None

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id_to_str(cls, v):
        """Convert integer IDs from IBGE API to strings."""
        return str(v) if isinstance(v, int) else v


class IBGEClient:
    """
    Client for IBGE (Brazilian Institute of Geography and Statistics) API.

    Provides access to:
    - Demographic data (population, age distribution, race/ethnicity)
    - Economic indicators (GDP, per capita income, poverty rates)
    - Social indicators (education, health, housing)
    - Geographic data (municipalities, states, regions)
    """

    BASE_URL = "https://servicodados.ibge.gov.br/api/v3"
    AGREGADOS_URL = "https://servicodados.ibge.gov.br/api/v3/agregados"
    LOCALIDADES_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"

    def __init__(self, timeout: int = 30):
        """
        Initialize IBGE API client.

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

        self.logger.info("IBGE API client initialized")

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()

    async def test_connection(self) -> bool:
        """
        Test connection to IBGE API.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            states = await self.get_states()
            return len(states) > 0
        except Exception:
            return False

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

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
        FederalAPIMetrics.increment_active_requests("IBGE")

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
                api_name="IBGE", endpoint=endpoint, size_bytes=response_size
            )

            # Check for HTTP errors
            if response.status_code >= 500:
                error_msg = f"Server error: {response.status_code}"
                # Record error before raising
                FederalAPIMetrics.record_error(
                    api_name="IBGE", error_type="ServerError", retryable=True
                )
                raise ServerError(
                    error_msg,
                    api_name="IBGE",
                    status_code=response.status_code,
                    response_data={"url": url},
                )
            if response.status_code >= 400:
                error_msg = f"Client error: {response.status_code}"
                # Record error before raising
                retryable = response.status_code == 429  # Only rate limit is retryable
                FederalAPIMetrics.record_error(
                    api_name="IBGE",
                    error_type=f"ClientError_{response.status_code}",
                    retryable=retryable,
                )
                raise exception_from_response(
                    response.status_code,
                    error_msg,
                    api_name="IBGE",
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
                    api_name="IBGE", error_type="JSONParseError", retryable=False
                )
                raise

        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout: {url}")
            status = "timeout"
            status_code = 0

            # Record timeout
            FederalAPIMetrics.record_timeout(
                api_name="IBGE", method=method, timeout_seconds=self.timeout
            )
            FederalAPIMetrics.record_error(
                api_name="IBGE", error_type="TimeoutError", retryable=True
            )

            raise TimeoutError(
                "Request timed out",
                api_name="IBGE",
                timeout_seconds=self.timeout,
                original_error=e,
            )
        except httpx.NetworkError as e:
            self.logger.error(f"Network error: {url}")
            status = "network_error"
            status_code = 0

            # Record network error
            FederalAPIMetrics.record_error(
                api_name="IBGE", error_type="NetworkError", retryable=True
            )

            raise NetworkError(
                f"Network error: {str(e)}", api_name="IBGE", original_error=e
            )
        except (ServerError, TimeoutError, NetworkError):
            # Re-raise our custom exceptions as-is (they'll be caught by retry decorator)
            raise
        except Exception as e:
            # Catch-all for unexpected errors
            self.logger.error(f"Unexpected error in _make_request: {e}", exc_info=True)
            status = "error"
            FederalAPIMetrics.record_error(
                api_name="IBGE", error_type=type(e).__name__, retryable=False
            )
            raise
        finally:
            # Always record request metrics
            duration = time.time() - start_time
            FederalAPIMetrics.record_request(
                api_name="IBGE",
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=duration,
                status=status,
            )

            # Decrement active requests
            FederalAPIMetrics.decrement_active_requests("IBGE")

    @cache_with_ttl(ttl_seconds=86400)  # 24 hours cache
    async def get_municipalities(
        self, state_id: str | None = None
    ) -> list[IBGELocation]:
        """
        Get list of municipalities.

        Args:
            state_id: Two-digit state ID (e.g., "33" for RJ) or None for all

        Returns:
            List of municipalities
        """
        if state_id:
            url = f"{self.LOCALIDADES_URL}/estados/{state_id}/municipios"
        else:
            url = f"{self.LOCALIDADES_URL}/municipios"

        self.logger.info(f"Fetching municipalities: state_id={state_id}")

        data = await self._make_request(url)
        municipalities = [IBGELocation(**m) for m in data]

        # Record data fetched
        FederalAPIMetrics.record_data_fetched(
            api_name="IBGE",
            data_type="municipalities",
            record_count=len(municipalities),
        )

        self.logger.info(f"Fetched {len(municipalities)} municipalities")
        return municipalities

    @cache_with_ttl(ttl_seconds=86400)  # 24 hours cache
    async def get_states(self) -> list[IBGELocation]:
        """
        Get list of Brazilian states.

        Returns:
            List of states
        """
        url = f"{self.LOCALIDADES_URL}/estados"

        self.logger.info("Fetching states")

        data = await self._make_request(url)
        states = [IBGELocation(**s) for s in data]

        # Record data fetched
        FederalAPIMetrics.record_data_fetched(
            api_name="IBGE", data_type="states", record_count=len(states)
        )

        self.logger.info(f"Fetched {len(states)} states")
        return states

    @cache_with_ttl(ttl_seconds=3600)  # 1 hour cache
    async def get_population(
        self, location_id: str | None = None, year: int | None = None
    ) -> dict[str, Any]:
        """
        Get population data.

        Args:
            location_id: Location ID (state or municipality) or None for Brazil
            year: Year for population data or None for latest

        Returns:
            Population data
        """
        # População estimada (agregado 6579)
        url = f"{self.AGREGADOS_URL}/6579/periodos"

        if year:
            url += f"/{year}"
        else:
            url += "/all"

        if location_id:
            url += f"/variaveis/9324?localidades=N6[{location_id}]"
        else:
            url += "/variaveis/9324?localidades=N1[all]"

        self.logger.info(f"Fetching population: location={location_id}, year={year}")

        data = await self._make_request(url)

        self.logger.info("Fetched population data")
        return data

    @cache_with_ttl(ttl_seconds=3600)
    async def get_demographic_data(
        self,
        location_ids: list[str] | None = None,
        indicators: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get comprehensive demographic data.

        Args:
            location_ids: List of location IDs or None for all
            indicators: Specific indicators to fetch or None for common ones

        Returns:
            Demographic data including:
            - Population by age groups
            - Population by race/ethnicity
            - Household data
            - Urbanization rates
        """
        try:
            # Default indicators if not specified
            if not indicators:
                indicators = [
                    "6579",  # População estimada
                    "1301",  # População residente por sexo
                    "93",  # População residente por cor ou raça
                ]

            results = {}

            for indicator_id in indicators:
                url = f"{self.AGREGADOS_URL}/{indicator_id}/periodos/all/variaveis/all"

                if location_ids:
                    location_filter = ",".join(location_ids)
                    url += f"?localidades=N6[{location_filter}]"

                self.logger.info(f"Fetching demographic indicator: {indicator_id}")

                response = await self.client.get(url)
                response.raise_for_status()

                results[indicator_id] = response.json()

                # Rate limiting - avoid hammering the API
                await asyncio.sleep(0.5)

            self.logger.info("Fetched demographic data")
            return results

        except Exception as e:
            self.logger.error(f"Error fetching demographic data: {e}")
            raise

    @cache_with_ttl(ttl_seconds=7200)  # 2 hours cache
    async def get_gdp_per_capita(
        self, location_ids: list[str] | None = None, year: int | None = None
    ) -> dict[str, Any]:
        """
        Get GDP per capita data.

        Args:
            location_ids: Location IDs or None for all
            year: Year or None for latest

        Returns:
            GDP per capita data by location
        """
        try:
            # PIB per capita (agregado 5938)
            url = f"{self.AGREGADOS_URL}/5938/periodos"

            if year:
                url += f"/{year}"
            else:
                url += "/all"

            url += "/variaveis/37"  # PIB per capita variable

            if location_ids:
                location_filter = ",".join(location_ids)
                url += f"?localidades=N6[{location_filter}]"
            else:
                url += "?localidades=N3[all]"  # All states

            self.logger.info(
                f"Fetching GDP per capita: locations={location_ids}, year={year}"
            )

            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()

            self.logger.info("Fetched GDP per capita data")
            return data

        except Exception as e:
            self.logger.error(f"Error fetching GDP per capita: {e}")
            raise

    @cache_with_ttl(ttl_seconds=7200)
    async def get_poverty_data(
        self, location_ids: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Get poverty and inequality data.

        Args:
            location_ids: Location IDs or None for all

        Returns:
            Poverty indicators including:
            - People below poverty line
            - Gini coefficient
            - Income distribution
        """
        try:
            # Síntese de Indicadores Sociais
            indicators = [
                "4099",  # Pessoas em domicílios com rendimento per capita abaixo da linha de pobreza
                "4100",  # Coeficiente de Gini
                "4102",  # Razão entre rendimentos
            ]

            results = {}

            for indicator_id in indicators:
                url = f"{self.AGREGADOS_URL}/{indicator_id}/periodos/all/variaveis/all"

                if location_ids:
                    location_filter = ",".join(location_ids)
                    url += f"?localidades=N1[{location_filter}]"

                self.logger.info(f"Fetching poverty indicator: {indicator_id}")

                try:
                    response = await self.client.get(url)
                    response.raise_for_status()
                    results[indicator_id] = response.json()
                except Exception as e:
                    self.logger.warning(
                        f"Failed to fetch indicator {indicator_id}: {e}"
                    )
                    results[indicator_id] = None

                await asyncio.sleep(0.5)

            self.logger.info("Fetched poverty data")
            return results

        except Exception as e:
            self.logger.error(f"Error fetching poverty data: {e}")
            raise

    @cache_with_ttl(ttl_seconds=3600)
    async def get_education_data(
        self, location_ids: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Get education indicators from IBGE.

        Args:
            location_ids: Location IDs or None for all

        Returns:
            Education data including:
            - Literacy rates
            - School enrollment
            - Years of study
        """
        try:
            # PNAD Contínua - Educação
            indicators = [
                "7113",  # Taxa de analfabetismo
                "7267",  # Taxa de escolarização
                "7109",  # Anos de estudo
            ]

            results = {}

            for indicator_id in indicators:
                url = f"{self.AGREGADOS_URL}/{indicator_id}/periodos/all/variaveis/all"

                if location_ids:
                    location_filter = ",".join(location_ids)
                    url += f"?localidades=N1[{location_filter}]"

                self.logger.info(f"Fetching education indicator: {indicator_id}")

                try:
                    response = await self.client.get(url)
                    response.raise_for_status()
                    results[indicator_id] = response.json()
                except Exception as e:
                    self.logger.warning(
                        f"Failed to fetch indicator {indicator_id}: {e}"
                    )
                    results[indicator_id] = None

                await asyncio.sleep(0.5)

            self.logger.info("Fetched education data")
            return results

        except Exception as e:
            self.logger.error(f"Error fetching education data: {e}")
            raise

    @cache_with_ttl(ttl_seconds=7200)
    async def get_housing_data(
        self, location_ids: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Get housing and infrastructure data.

        Args:
            location_ids: Location IDs or None for all

        Returns:
            Housing data including:
            - Households with water supply
            - Households with sewage
            - Households with electricity
        """
        try:
            # Censo Demográfico - Características dos domicílios
            indicators = [
                "8468",  # Domicílios com abastecimento de água
                "8469",  # Domicílios com esgotamento sanitário
                "8470",  # Domicílios com energia elétrica
            ]

            results = {}

            for indicator_id in indicators:
                url = f"{self.AGREGADOS_URL}/{indicator_id}/periodos/all/variaveis/all"

                if location_ids:
                    location_filter = ",".join(location_ids)
                    url += f"?localidades=N6[{location_filter}]"

                self.logger.info(f"Fetching housing indicator: {indicator_id}")

                try:
                    response = await self.client.get(url)
                    response.raise_for_status()
                    results[indicator_id] = response.json()
                except Exception as e:
                    self.logger.warning(
                        f"Failed to fetch indicator {indicator_id}: {e}"
                    )
                    results[indicator_id] = None

                await asyncio.sleep(0.5)

            self.logger.info("Fetched housing data")
            return results

        except Exception as e:
            self.logger.error(f"Error fetching housing data: {e}")
            raise

    async def get_comprehensive_social_data(
        self,
        state_id: str | None = None,
        municipality_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get comprehensive social equity data for analysis.

        This is the main method for Dandara agent integration.

        Args:
            state_id: State ID for state-level data
            municipality_ids: Municipality IDs for municipal-level data

        Returns:
            Comprehensive social data including all major indicators
        """
        try:
            self.logger.info(
                f"Fetching comprehensive social data: state={state_id}, municipalities={municipality_ids}"
            )

            # Determine location filter
            location_ids = (
                municipality_ids
                if municipality_ids
                else (state_id if state_id else None)
            )

            # Fetch all data in parallel
            results = await asyncio.gather(
                self.get_demographic_data(location_ids),
                self.get_gdp_per_capita(location_ids),
                self.get_poverty_data(location_ids),
                self.get_education_data(location_ids),
                self.get_housing_data(location_ids),
                return_exceptions=True,
            )

            # Organize results
            comprehensive_data = {
                "timestamp": datetime.now().isoformat(),
                "source": "IBGE",
                "locations": {
                    "state_id": state_id,
                    "municipality_ids": municipality_ids,
                },
                "demographic": (
                    results[0] if not isinstance(results[0], Exception) else None
                ),
                "economic": (
                    results[1] if not isinstance(results[1], Exception) else None
                ),
                "poverty": (
                    results[2] if not isinstance(results[2], Exception) else None
                ),
                "education": (
                    results[3] if not isinstance(results[3], Exception) else None
                ),
                "housing": (
                    results[4] if not isinstance(results[4], Exception) else None
                ),
                "errors": [str(r) for r in results if isinstance(r, Exception)],
            }

            self.logger.info("Fetched comprehensive social data successfully")
            return comprehensive_data

        except Exception as e:
            self.logger.error(f"Error fetching comprehensive social data: {e}")
            raise
