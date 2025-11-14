"""
DataSUS API Client

Client for Brazilian Health Ministry (DataSUS) data.
Provides access to health statistics, hospital data, and public health indicators.

API Documentation: https://opendatasus.saude.gov.br/

Author: Anderson Henrique da Silva
Created: 2025-10-12
License: Proprietary - All rights reserved
"""

import asyncio
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
    """Decorator for caching DataSUS API calls with TTL."""

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
                    logger.debug(f"DataSUS cache hit: {cache_key}")
                    # Record cache hit
                    FederalAPIMetrics.record_cache_operation(
                        api_name="DataSUS", operation="read", result="hit"
                    )
                    return cache[cache_key]

            # Cache miss - record it
            FederalAPIMetrics.record_cache_operation(
                api_name="DataSUS", operation="read", result="miss"
            )

            # Calculate and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = result
            cache_times[cache_key] = current_time

            # Record cache write
            FederalAPIMetrics.record_cache_operation(
                api_name="DataSUS", operation="write", result="success"
            )

            # Update cache size gauge
            FederalAPIMetrics.update_cache_size(
                api_name="DataSUS", cache_type="memory", size=len(cache)
            )

            return result

        return wrapper

    return decorator


class DataSUSIndicator(BaseModel):
    """DataSUS health indicator."""

    code: str
    name: str
    category: str
    unit: Optional[str] = None


class DataSUSClient:
    """
    Client for DataSUS (Brazilian Health Ministry) API.

    Provides access to:
    - Mortality data (SIM - Sistema de Informação sobre Mortalidade)
    - Hospital admissions (SIH - Sistema de Informação Hospitalar)
    - Primary care data (e-SUS APS)
    - Vaccination data (SI-PNI)
    - Disease notification (SINAN)
    - Health infrastructure (CNES - Cadastro Nacional de Estabelecimentos de Saúde)
    """

    OPENDATASUS_URL = "https://opendatasus.saude.gov.br/api/3/action"
    CNES_URL = "http://cnes.datasus.gov.br/pages/estabelecimentos/extracao.jsp"

    # Major health datasets on OpenDataSUS
    DATASETS = {
        "mortality": "sim-do",  # Sistema de Informação sobre Mortalidade - Declaração de Óbito
        "hospital_admissions": "sih-rd",  # Sistema de Informação Hospitalar
        "primary_care": "esus-notifica",  # e-SUS Notifica
        "vaccination": "si-pni",  # Sistema de Informação do Programa Nacional de Imunizações
        "health_facilities": "cnes",  # Cadastro Nacional de Estabelecimentos de Saúde
        "covid19": "covid-19-vacinacao",  # COVID-19 vaccination data
    }

    def __init__(self, timeout: int = 30):
        """
        Initialize DataSUS API client.

        Args:
            timeout: Request timeout in seconds
        """
        self.base_url = self.OPENDATASUS_URL
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
        self.logger = get_logger(__name__)

        self.logger.info("DataSUS API client initialized")

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
        FederalAPIMetrics.increment_active_requests("DataSUS")

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
                api_name="DataSUS", endpoint=endpoint, size_bytes=response_size
            )

            # Check for HTTP errors
            if response.status_code >= 500:
                error_msg = f"Server error: {response.status_code}"
                # Record error before raising
                FederalAPIMetrics.record_error(
                    api_name="DataSUS", error_type="ServerError", retryable=True
                )
                raise ServerError(
                    error_msg,
                    api_name="DataSUS",
                    status_code=response.status_code,
                    response_data={"url": url},
                )
            elif response.status_code >= 400:
                error_msg = f"Client error: {response.status_code}"
                # Record error before raising
                retryable = response.status_code == 429  # Only rate limit is retryable
                FederalAPIMetrics.record_error(
                    api_name="DataSUS",
                    error_type=f"ClientError_{response.status_code}",
                    retryable=retryable,
                )
                raise exception_from_response(
                    response.status_code,
                    error_msg,
                    api_name="DataSUS",
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
                    api_name="DataSUS", error_type="JSONParseError", retryable=False
                )
                raise

        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout: {url}")
            status = "timeout"
            status_code = 0

            # Record timeout
            FederalAPIMetrics.record_timeout(
                api_name="DataSUS", method=method, timeout_seconds=self.timeout
            )
            FederalAPIMetrics.record_error(
                api_name="DataSUS", error_type="TimeoutError", retryable=True
            )

            raise TimeoutError(
                "Request timed out",
                api_name="DataSUS",
                timeout_seconds=self.timeout,
                original_error=e,
            )
        except httpx.NetworkError as e:
            self.logger.error(f"Network error: {url}")
            status = "network_error"
            status_code = 0

            # Record network error
            FederalAPIMetrics.record_error(
                api_name="DataSUS", error_type="NetworkError", retryable=True
            )

            raise NetworkError(
                f"Network error: {str(e)}", api_name="DataSUS", original_error=e
            )
        except (ServerError, TimeoutError, NetworkError):
            # Re-raise our custom exceptions as-is (they'll be caught by retry decorator)
            raise
        except Exception as e:
            # Catch-all for unexpected errors
            self.logger.error(f"Unexpected error in _make_request: {e}", exc_info=True)
            status = "error"
            FederalAPIMetrics.record_error(
                api_name="DataSUS", error_type=type(e).__name__, retryable=False
            )
            raise
        finally:
            # Always record request metrics
            duration = time.time() - start_time
            FederalAPIMetrics.record_request(
                api_name="DataSUS",
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=duration,
                status=status,
            )

            # Decrement active requests
            FederalAPIMetrics.decrement_active_requests("DataSUS")

    @cache_with_ttl(ttl_seconds=86400)  # 24 hours cache
    async def search_datasets(self, query: str, limit: int = 100) -> dict[str, Any]:
        """
        Search for datasets in OpenDataSUS.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Dataset search results
        """
        url = f"{self.OPENDATASUS_URL}/package_search"
        params = {"q": query, "rows": limit}

        self.logger.info(f"Searching DataSUS datasets: query={query}")

        data = await self._make_request(url, params=params)

        self.logger.info(f"Found {data.get('result', {}).get('count', 0)} datasets")
        return data

    @cache_with_ttl(ttl_seconds=7200)  # 2 hours cache
    async def get_health_facilities(
        self,
        state_code: Optional[str] = None,
        municipality_code: Optional[str] = None,
        facility_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Get health facilities data from CNES.

        Args:
            state_code: Two-letter state code (e.g., "RJ", "SP")
            municipality_code: IBGE municipality code
            facility_type: Type of facility (hospital, clinic, etc.)

        Returns:
            Health facilities data
        """
        # Note: CNES API is complex and often requires form-based access
        # This is a simplified version - real implementation may need web scraping

        self.logger.info(
            f"Fetching health facilities: state={state_code}, municipality={municipality_code}"
        )

        # Try to get data from OpenDataSUS CNES dataset
        dataset_id = self.DATASETS["health_facilities"]
        url = f"{self.OPENDATASUS_URL}/package_show"
        params = {"id": dataset_id}

        data = await self._make_request(url, params=params)

        # Filter by location if specified
        result = {
            "timestamp": datetime.now().isoformat(),
            "source": "DataSUS/CNES",
            "filters": {
                "state": state_code,
                "municipality": municipality_code,
                "facility_type": facility_type,
            },
            "data": data.get("result", {}),
            "note": "CNES data requires additional processing for specific locations",
        }

        self.logger.info("Fetched health facilities data")
        return result

    @cache_with_ttl(ttl_seconds=3600)  # 1 hour cache
    async def get_mortality_statistics(
        self,
        state_code: Optional[str] = None,
        year: Optional[int] = None,
        cause_category: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Get mortality statistics from SIM.

        Args:
            state_code: State code
            year: Year for data
            cause_category: Disease category (CID-10)

        Returns:
            Mortality data including:
            - Deaths by cause
            - Deaths by age group
            - Deaths by location
        """
        self.logger.info(f"Fetching mortality data: state={state_code}, year={year}")

        # Get SIM dataset
        dataset_id = self.DATASETS["mortality"]
        url = f"{self.OPENDATASUS_URL}/package_show"
        params = {"id": dataset_id}

        data = await self._make_request(url, params=params)

        result = {
            "timestamp": datetime.now().isoformat(),
            "source": "DataSUS/SIM",
            "filters": {
                "state": state_code,
                "year": year,
                "cause_category": cause_category,
            },
            "dataset_info": data.get("result", {}),
            "note": "Full mortality data requires downloading CSV files from resources",
        }

        self.logger.info("Fetched mortality statistics")
        return result

    @cache_with_ttl(ttl_seconds=3600)
    async def get_hospital_admissions(
        self,
        state_code: Optional[str] = None,
        year: Optional[int] = None,
        procedure_category: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Get hospital admission statistics from SIH.

        Args:
            state_code: State code
            year: Year for data
            procedure_category: Medical procedure category

        Returns:
            Hospital admission data
        """
        self.logger.info(
            f"Fetching hospital admissions: state={state_code}, year={year}"
        )

        dataset_id = self.DATASETS["hospital_admissions"]
        url = f"{self.OPENDATASUS_URL}/package_show"
        params = {"id": dataset_id}

        data = await self._make_request(url, params=params)

        result = {
            "timestamp": datetime.now().isoformat(),
            "source": "DataSUS/SIH",
            "filters": {
                "state": state_code,
                "year": year,
                "procedure_category": procedure_category,
            },
            "dataset_info": data.get("result", {}),
            "note": "Full admission data requires downloading files from resources",
        }

        self.logger.info("Fetched hospital admissions data")
        return result

    @cache_with_ttl(ttl_seconds=7200)
    async def get_vaccination_data(
        self, state_code: Optional[str] = None, vaccine_type: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get vaccination coverage data from SI-PNI.

        Args:
            state_code: State code
            vaccine_type: Type of vaccine

        Returns:
            Vaccination coverage data
        """
        self.logger.info(
            f"Fetching vaccination data: state={state_code}, vaccine={vaccine_type}"
        )

        dataset_id = self.DATASETS["vaccination"]
        url = f"{self.OPENDATASUS_URL}/package_show"
        params = {"id": dataset_id}

        data = await self._make_request(url, params=params)

        result = {
            "timestamp": datetime.now().isoformat(),
            "source": "DataSUS/SI-PNI",
            "filters": {"state": state_code, "vaccine_type": vaccine_type},
            "dataset_info": data.get("result", {}),
            "note": "Vaccination data available in dataset resources",
        }

        self.logger.info("Fetched vaccination data")
        return result

    async def get_health_indicators(
        self, state_code: Optional[str] = None, municipality_code: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get comprehensive health indicators for a location.

        This is the main method for Dandara agent integration.

        Args:
            state_code: State code
            municipality_code: Municipality code

        Returns:
            Comprehensive health indicators including:
            - Health facility coverage
            - Mortality rates
            - Hospital admission rates
            - Vaccination coverage
        """
        self.logger.info(
            f"Fetching health indicators: state={state_code}, municipality={municipality_code}"
        )

        # Fetch multiple datasets in parallel
        results = await asyncio.gather(
            self.get_health_facilities(state_code, municipality_code),
            self.get_mortality_statistics(state_code),
            self.get_hospital_admissions(state_code),
            self.get_vaccination_data(state_code),
            return_exceptions=True,
        )

        # Organize results
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "source": "DataSUS",
            "location": {"state": state_code, "municipality": municipality_code},
            "health_facilities": (
                results[0] if not isinstance(results[0], Exception) else None
            ),
            "mortality": results[1] if not isinstance(results[1], Exception) else None,
            "hospital_admissions": (
                results[2] if not isinstance(results[2], Exception) else None
            ),
            "vaccination": (
                results[3] if not isinstance(results[3], Exception) else None
            ),
            "errors": [str(r) for r in results if isinstance(r, Exception)],
            "note": "DataSUS data often requires downloading CSV files for detailed analysis",
        }

        self.logger.info("Fetched comprehensive health indicators")
        return health_data
