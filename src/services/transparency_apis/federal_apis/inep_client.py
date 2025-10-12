"""
INEP API Client

Client for National Institute of Educational Studies and Research (INEP) data.
Provides access to education statistics, school census, and IDEB indicators.

API Documentation: https://dados.gov.br/organization/inep

Author: Anderson Henrique da Silva
Created: 2025-10-12
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from functools import wraps
import hashlib
import json

import httpx
from pydantic import BaseModel, Field as PydanticField

from src.core import get_logger
from .exceptions import NetworkError, TimeoutError, ServerError, exception_from_response
from .retry import retry_with_backoff


logger = get_logger(__name__)


def cache_with_ttl(ttl_seconds: int = 3600):
    """Decorator for caching INEP API calls with TTL."""
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
                    key_parts.append(hashlib.md5(
                        json.dumps(arg, sort_keys=True).encode()
                    ).hexdigest()[:8])

            cache_key = "_".join(key_parts)

            # Check cache validity
            current_time = datetime.now().timestamp()
            if cache_key in cache:
                cached_time = cache_times.get(cache_key, 0)
                if current_time - cached_time < ttl_seconds:
                    logger.debug(f"INEP cache hit: {cache_key}")
                    return cache[cache_key]

            # Calculate and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = result
            cache_times[cache_key] = current_time

            return result

        return wrapper
    return decorator


class INEPSchool(BaseModel):
    """School representation from INEP."""
    code: str
    name: str
    location: Dict[str, Any]
    education_levels: List[str]


class IDEBIndicator(BaseModel):
    """IDEB (Índice de Desenvolvimento da Educação Básica) indicator."""
    year: int
    value: float
    location_type: str  # municipal, state, national
    location_code: Optional[str] = None
    education_level: str  # anos_iniciais, anos_finais, ensino_medio


class INEPClient:
    """
    Client for INEP (National Institute of Educational Studies) data.

    Provides access to:
    - School Census (Censo Escolar)
    - IDEB indicators (Índice de Desenvolvimento da Educação Básica)
    - ENEM results (Exame Nacional do Ensino Médio)
    - Higher education data (Censo da Educação Superior)
    - Teacher data
    - Infrastructure data
    """

    DADOS_GOV_URL = "https://dados.gov.br/api/3/action"

    # Major INEP datasets on dados.gov.br
    DATASETS = {
        "school_census": "microdados-do-censo-escolar",
        "ideb": "indice-de-desenvolvimento-da-educacao-basica-ideb",
        "enem": "microdados-do-enem",
        "higher_education": "microdados-do-censo-da-educacao-superior",
        "teachers": "censo-escolar-docentes",
        "schools": "censo-escolar-escolas",
    }

    def __init__(self, timeout: int = 30):
        """
        Initialize INEP API client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
        self.logger = get_logger(__name__)

        self.logger.info("INEP API client initialized")

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
    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
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
        try:
            self.logger.debug(f"Making {method} request to {url}")

            if method.upper() == "GET":
                response = await self.client.get(url, **kwargs)
            elif method.upper() == "POST":
                response = await self.client.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check for HTTP errors
            if response.status_code >= 500:
                error_msg = f"Server error: {response.status_code}"
                raise ServerError(
                    error_msg,
                    api_name="INEP",
                    status_code=response.status_code,
                    response_data={"url": url}
                )
            elif response.status_code >= 400:
                error_msg = f"Client error: {response.status_code}"
                raise exception_from_response(
                    response.status_code,
                    error_msg,
                    api_name="INEP",
                    response_data={"url": url}
                )

            # Parse JSON response
            try:
                data = response.json()
                return data
            except Exception as e:
                self.logger.error(f"Failed to parse JSON response: {e}")
                raise

        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout: {url}")
            raise TimeoutError(
                f"Request timed out",
                api_name="INEP",
                timeout_seconds=self.timeout,
                original_error=e
            )
        except httpx.NetworkError as e:
            self.logger.error(f"Network error: {url}")
            raise NetworkError(
                f"Network error: {str(e)}",
                api_name="INEP",
                original_error=e
            )
        except (ServerError, TimeoutError, NetworkError):
            # Re-raise our custom exceptions as-is (they'll be caught by retry decorator)
            raise
        except Exception as e:
            # Catch-all for unexpected errors
            self.logger.error(f"Unexpected error in _make_request: {e}", exc_info=True)
            raise

    @cache_with_ttl(ttl_seconds=86400)  # 24 hours cache
    async def search_datasets(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """
        Search for INEP datasets.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Dataset search results
        """
        url = f"{self.DADOS_GOV_URL}/package_search"
        params = {
            "q": f"inep {query}",
            "fq": "organization:inep",
            "rows": limit
        }

        self.logger.info(f"Searching INEP datasets: query={query}")

        data = await self._make_request(url, params=params)

        self.logger.info(f"Found {data.get('result', {}).get('count', 0)} datasets")
        return data

    @cache_with_ttl(ttl_seconds=7200)  # 2 hours cache
    async def get_school_census_data(
        self,
        state_code: Optional[str] = None,
        municipality_code: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get school census data.

        Args:
            state_code: State code
            municipality_code: Municipality code
            year: Census year

        Returns:
            School census data including:
            - Number of schools
            - Number of students
            - Infrastructure indicators
            - Teacher data
        """
        self.logger.info(f"Fetching school census: state={state_code}, municipality={municipality_code}, year={year}")

        dataset_id = self.DATASETS["school_census"]
        url = f"{self.DADOS_GOV_URL}/package_show"
        params = {"id": dataset_id}

        data = await self._make_request(url, params=params)

        result = {
            "timestamp": datetime.now().isoformat(),
            "source": "INEP/Censo Escolar",
            "filters": {
                "state": state_code,
                "municipality": municipality_code,
                "year": year or "latest"
            },
            "dataset_info": data.get("result", {}),
            "note": "School census data available as CSV/microdata files in resources"
        }

        self.logger.info("Fetched school census data")
        return result

    @cache_with_ttl(ttl_seconds=7200)
    async def get_ideb_indicators(
        self,
        state_code: Optional[str] = None,
        municipality_code: Optional[str] = None,
        year: Optional[int] = None,
        education_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get IDEB (Basic Education Development Index) indicators.

        Args:
            state_code: State code
            municipality_code: Municipality code
            year: Year (IDEB is calculated every 2 years: 2019, 2021, etc.)
            education_level: Level (anos_iniciais, anos_finais, ensino_medio)

        Returns:
            IDEB indicators by location and education level
        """
        self.logger.info(f"Fetching IDEB data: state={state_code}, municipality={municipality_code}, year={year}")

        dataset_id = self.DATASETS["ideb"]
        url = f"{self.DADOS_GOV_URL}/package_show"
        params = {"id": dataset_id}

        data = await self._make_request(url, params=params)

        result = {
            "timestamp": datetime.now().isoformat(),
            "source": "INEP/IDEB",
            "filters": {
                "state": state_code,
                "municipality": municipality_code,
                "year": year or "latest",
                "education_level": education_level or "all"
            },
            "dataset_info": data.get("result", {}),
            "note": "IDEB data available in dataset resources - typically as Excel or CSV"
        }

        self.logger.info("Fetched IDEB indicators")
        return result

    @cache_with_ttl(ttl_seconds=7200)
    async def get_enem_results(
        self,
        state_code: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get ENEM (National High School Exam) results.

        Args:
            state_code: State code
            year: Exam year

        Returns:
            ENEM performance data
        """
        self.logger.info(f"Fetching ENEM results: state={state_code}, year={year}")

        dataset_id = self.DATASETS["enem"]
        url = f"{self.DADOS_GOV_URL}/package_show"
        params = {"id": dataset_id}

        data = await self._make_request(url, params=params)

        result = {
            "timestamp": datetime.now().isoformat(),
            "source": "INEP/ENEM",
            "filters": {
                "state": state_code,
                "year": year or "latest"
            },
            "dataset_info": data.get("result", {}),
            "note": "ENEM microdata available as large CSV files"
        }

        self.logger.info("Fetched ENEM results")
        return result

    @cache_with_ttl(ttl_seconds=3600)
    async def get_school_infrastructure(
        self,
        state_code: Optional[str] = None,
        municipality_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get school infrastructure data.

        Args:
            state_code: State code
            municipality_code: Municipality code

        Returns:
            School infrastructure indicators including:
            - Internet access
            - Computer labs
            - Libraries
            - Sports facilities
            - Accessibility features
        """
        self.logger.info(f"Fetching school infrastructure: state={state_code}, municipality={municipality_code}")

        dataset_id = self.DATASETS["schools"]
        url = f"{self.DADOS_GOV_URL}/package_show"
        params = {"id": dataset_id}

        data = await self._make_request(url, params=params)

        result = {
            "timestamp": datetime.now().isoformat(),
            "source": "INEP/Censo Escolar - Escolas",
            "filters": {
                "state": state_code,
                "municipality": municipality_code
            },
            "dataset_info": data.get("result", {}),
            "note": "School-level infrastructure data in census microdata"
        }

        self.logger.info("Fetched school infrastructure data")
        return result

    @cache_with_ttl(ttl_seconds=7200)
    async def get_teacher_statistics(
        self,
        state_code: Optional[str] = None,
        municipality_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get teacher statistics.

        Args:
            state_code: State code
            municipality_code: Municipality code

        Returns:
            Teacher data including:
            - Number of teachers
            - Education levels
            - Subject areas
            - Employment status
        """
        self.logger.info(f"Fetching teacher statistics: state={state_code}, municipality={municipality_code}")

        dataset_id = self.DATASETS["teachers"]
        url = f"{self.DADOS_GOV_URL}/package_show"
        params = {"id": dataset_id}

        data = await self._make_request(url, params=params)

        result = {
            "timestamp": datetime.now().isoformat(),
            "source": "INEP/Censo Escolar - Docentes",
            "filters": {
                "state": state_code,
                "municipality": municipality_code
            },
            "dataset_info": data.get("result", {}),
            "note": "Teacher microdata available in census files"
        }

        self.logger.info("Fetched teacher statistics")
        return result

    async def get_education_indicators(
        self,
        state_code: Optional[str] = None,
        municipality_code: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive education indicators for a location.

        This is the main method for Dandara agent integration.

        Args:
            state_code: State code
            municipality_code: Municipality code
            year: Data year

        Returns:
            Comprehensive education indicators including:
            - School census data
            - IDEB indicators
            - Infrastructure metrics
            - Teacher statistics
        """
        self.logger.info(f"Fetching education indicators: state={state_code}, municipality={municipality_code}, year={year}")

        # Fetch multiple datasets in parallel
        results = await asyncio.gather(
            self.get_school_census_data(state_code, municipality_code, year),
            self.get_ideb_indicators(state_code, municipality_code, year),
            self.get_school_infrastructure(state_code, municipality_code),
            self.get_teacher_statistics(state_code, municipality_code),
            return_exceptions=True
        )

        # Organize results
        education_data = {
            "timestamp": datetime.now().isoformat(),
            "source": "INEP",
            "location": {
                "state": state_code,
                "municipality": municipality_code
            },
            "year": year or "latest",
            "school_census": results[0] if not isinstance(results[0], Exception) else None,
            "ideb": results[1] if not isinstance(results[1], Exception) else None,
            "infrastructure": results[2] if not isinstance(results[2], Exception) else None,
            "teachers": results[3] if not isinstance(results[3], Exception) else None,
            "errors": [str(r) for r in results if isinstance(r, Exception)],
            "note": "INEP data typically requires downloading microdata files for detailed analysis"
        }

        self.logger.info("Fetched comprehensive education indicators")
        return education_data
