"""
Banco Central do Brasil API Client

Client for Brazilian Central Bank open data APIs.
Provides access to economic indicators (SELIC, exchange rates, PIX statistics).

API Documentation: https://dadosabertos.bcb.gov.br/
SGS API: https://api.bcb.gov.br/dados/serie/bcdata.sgs

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
from pydantic import BaseModel, ConfigDict

from src.core import get_logger

from .exceptions import NetworkError, ServerError, TimeoutError, exception_from_response
from .metrics import FederalAPIMetrics
from .retry import retry_with_backoff

logger = get_logger(__name__)


def cache_with_ttl(ttl_seconds: int = 3600):
    """Decorator for caching BCB API calls with TTL."""

    def decorator(func):
        cache = {}
        cache_times = {}

        @wraps(func)
        async def wrapper(*args, **kwargs):
            key_parts = [func.__name__]
            for arg in args[1:]:
                if isinstance(arg, (str, int, float, bool)):
                    key_parts.append(str(arg))
                elif isinstance(arg, (list, dict)):
                    key_parts.append(
                        hashlib.md5(
                            json.dumps(arg, sort_keys=True).encode()
                        ).hexdigest()[:8]
                    )

            cache_key = "_".join(key_parts)
            current_time = datetime.now().timestamp()

            if cache_key in cache:
                cached_time = cache_times.get(cache_key, 0)
                if current_time - cached_time < ttl_seconds:
                    logger.debug(f"BCB cache hit: {cache_key}")
                    FederalAPIMetrics.record_cache_operation(
                        api_name="BCB", operation="read", result="hit"
                    )
                    return cache[cache_key]

            FederalAPIMetrics.record_cache_operation(
                api_name="BCB", operation="read", result="miss"
            )

            result = await func(*args, **kwargs)
            cache[cache_key] = result
            cache_times[cache_key] = current_time

            FederalAPIMetrics.record_cache_operation(
                api_name="BCB", operation="write", result="success"
            )
            FederalAPIMetrics.update_cache_size(
                api_name="BCB", cache_type="memory", size=len(cache)
            )

            return result

        return wrapper

    return decorator


class SELICData(BaseModel):
    """SELIC rate data point."""

    data: str  # Date in dd/MM/yyyy format
    valor: str  # Value as string


class ExchangeRateData(BaseModel):
    """Exchange rate data point."""

    dataHoraCotacao: str
    tipoBoletim: str
    moeda: dict[str, Any]
    valorCompra: Optional[float] = None
    valorVenda: Optional[float] = None
    paridadeCompra: Optional[float] = None
    paridadeVenda: Optional[float] = None


class BancoCentralClient:
    """
    Client for Banco Central do Brasil APIs.

    Provides access to:
    - SELIC (Sistema Especial de Liquidação e Custódia) rate
    - Exchange rates (daily bulletins)
    - PIX statistics
    - Other economic indicators

    No authentication required for open data APIs.
    """

    SGS_BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"
    OLINDA_BASE_URL = "https://olinda.bcb.gov.br/olinda/servico"
    OPEN_DATA_URL = "https://dadosabertos.bcb.gov.br"

    # SGS Series Codes
    SERIES = {
        "selic": 11,  # SELIC daily
        "selic_monthly": 4390,  # SELIC accumulated monthly
        "selic_annual": 1178,  # SELIC annualized base 252
        "ipca": 433,  # IPCA monthly
        "igpm": 189,  # IGP-M monthly
        "cdi": 12,  # CDI daily
    }

    def __init__(self, timeout: int = 30):
        """
        Initialize Banco Central API client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
        self.logger = get_logger(__name__)
        self.logger.info("Banco Central API client initialized")

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
        """Make HTTP request with retry and metrics."""
        import time

        start_time = time.time()
        status_code = 500
        status = "error"
        endpoint = url.split("/")[-1] if "/" in url else url

        FederalAPIMetrics.increment_active_requests("BCB")

        try:
            self.logger.debug(f"Making {method} request to {url}")

            if method.upper() == "GET":
                response = await self.client.get(url, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            status_code = response.status_code

            response_size = len(response.content) if hasattr(response, "content") else 0
            FederalAPIMetrics.record_response_size(
                api_name="BCB", endpoint=endpoint, size_bytes=response_size
            )

            if response.status_code >= 500:
                FederalAPIMetrics.record_error(
                    api_name="BCB", error_type="ServerError", retryable=True
                )
                raise ServerError(
                    f"Server error: {response.status_code}",
                    api_name="BCB",
                    status_code=response.status_code,
                    response_data={"url": url},
                )
            elif response.status_code >= 400:
                retryable = response.status_code == 429
                FederalAPIMetrics.record_error(
                    api_name="BCB",
                    error_type=f"ClientError_{response.status_code}",
                    retryable=retryable,
                )
                raise exception_from_response(
                    response.status_code,
                    f"Client error: {response.status_code}",
                    api_name="BCB",
                    response_data={"url": url},
                )

            try:
                data = response.json()
                status = "success"
                return data
            except Exception as e:
                self.logger.error(f"Failed to parse JSON: {e}")
                status = "error"
                FederalAPIMetrics.record_error(
                    api_name="BCB", error_type="JSONParseError", retryable=False
                )
                raise

        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout: {url}")
            status = "timeout"
            status_code = 0
            FederalAPIMetrics.record_timeout(
                api_name="BCB", method=method, timeout_seconds=self.timeout
            )
            FederalAPIMetrics.record_error(
                api_name="BCB", error_type="TimeoutError", retryable=True
            )
            raise TimeoutError(
                "Request timed out",
                api_name="BCB",
                timeout_seconds=self.timeout,
                original_error=e,
            )
        except httpx.NetworkError as e:
            self.logger.error(f"Network error: {url}")
            status = "network_error"
            status_code = 0
            FederalAPIMetrics.record_error(
                api_name="BCB", error_type="NetworkError", retryable=True
            )
            raise NetworkError(
                f"Network error: {str(e)}", api_name="BCB", original_error=e
            )
        except (ServerError, TimeoutError, NetworkError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            status = "error"
            FederalAPIMetrics.record_error(
                api_name="BCB", error_type=type(e).__name__, retryable=False
            )
            raise
        finally:
            duration = time.time() - start_time
            FederalAPIMetrics.record_request(
                api_name="BCB",
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=duration,
                status=status,
            )
            FederalAPIMetrics.decrement_active_requests("BCB")

    @cache_with_ttl(ttl_seconds=3600)  # 1 hour
    async def get_selic(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        last_n: Optional[int] = None,
    ) -> list[SELICData]:
        """
        Get SELIC rate data.

        Args:
            start_date: Start date in dd/MM/yyyy format
            end_date: End date in dd/MM/yyyy format
            last_n: Get last N values (alternative to date range)

        Returns:
            List of SELIC data points

        Note: Date range limited to 10 years by BCB API

        Example:
            >>> async with BancoCentralClient() as client:
            >>>     # Last 30 days
            >>>     data = await client.get_selic(last_n=30)
            >>>     # Date range
            >>>     data = await client.get_selic(
            >>>         start_date="01/01/2024",
            >>>         end_date="31/12/2024"
            >>>     )
        """
        series_code = self.SERIES["selic"]

        if last_n:
            url = (
                f"{self.SGS_BASE_URL}/{series_code}/dados/ultimos/{last_n}?formato=json"
            )
        else:
            url = f"{self.SGS_BASE_URL}/{series_code}/dados?formato=json"
            if start_date:
                url += f"&dataInicial={start_date}"
            if end_date:
                url += f"&dataFinal={end_date}"

        self.logger.info(
            f"Fetching SELIC data: last_n={last_n}, dates={start_date} to {end_date}"
        )

        data = await self._make_request(url)

        FederalAPIMetrics.record_data_fetched(
            api_name="BCB", data_type="selic", record_count=len(data)
        )

        selic_data = [SELICData(**item) for item in data]

        self.logger.info(f"Fetched {len(selic_data)} SELIC data points")

        return selic_data

    @cache_with_ttl(ttl_seconds=86400)  # 24 hours
    async def get_exchange_rates(
        self, currency: str = "USD", start_date: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Get exchange rate data.

        Args:
            currency: Currency code (USD, EUR, GBP, etc.)
            start_date: Start date

        Returns:
            List of exchange rate data

        Example:
            >>> async with BancoCentralClient() as client:
            >>>     rates = await client.get_exchange_rates("USD")
            >>>     print(rates[0]["valorVenda"])  # Selling rate
        """
        self.logger.info(f"Fetching exchange rates for {currency}")

        # BCB Exchange Rate API endpoint
        url = f"{self.OLINDA_BASE_URL}/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)"
        url += f"?@moeda='{currency}'"

        if not start_date:
            start_date = datetime.now().strftime("%m-%d-%Y")

        url += f"&@dataCotacao='{start_date}'"
        url += "&$format=json"

        data = await self._make_request(url)

        value = data.get("value", [])

        FederalAPIMetrics.record_data_fetched(
            api_name="BCB", data_type="exchange_rate", record_count=len(value)
        )

        self.logger.info(f"Fetched {len(value)} exchange rate points")

        return value

    @cache_with_ttl(ttl_seconds=7200)  # 2 hours
    async def get_pix_statistics(self) -> dict[str, Any]:
        """
        Get PIX statistics (transactions, volume, adoption).

        Returns:
            PIX statistics data

        Example:
            >>> async with BancoCentralClient() as client:
            >>>     stats = await client.get_pix_statistics()
            >>>     print(stats)  # Transaction counts, values, etc.
        """
        self.logger.info("Fetching PIX statistics")

        url = f"{self.OLINDA_BASE_URL}/Pix_DadosAbertos/versao/v1/odata/EstatisticasGerais?$format=json"

        data = await self._make_request(url)

        FederalAPIMetrics.record_data_fetched(
            api_name="BCB", data_type="pix_stats", record_count=1
        )

        self.logger.info("Fetched PIX statistics")

        return data

    async def get_indicator(
        self,
        indicator_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        last_n: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """
        Get any economic indicator by name.

        Args:
            indicator_name: One of: selic, selic_monthly, selic_annual, ipca, igpm, cdi
            start_date: Start date dd/MM/yyyy
            end_date: End date dd/MM/yyyy
            last_n: Last N values

        Returns:
            List of indicator data points

        Example:
            >>> async with BancoCentralClient() as client:
            >>>     ipca = await client.get_indicator("ipca", last_n=12)  # Last 12 months
            >>>     cdi = await client.get_indicator("cdi", last_n=30)  # Last 30 days
        """
        if indicator_name not in self.SERIES:
            raise ValueError(
                f"Unknown indicator: {indicator_name}. Available: {list(self.SERIES.keys())}"
            )

        series_code = self.SERIES[indicator_name]

        if last_n:
            url = (
                f"{self.SGS_BASE_URL}/{series_code}/dados/ultimos/{last_n}?formato=json"
            )
        else:
            url = f"{self.SGS_BASE_URL}/{series_code}/dados?formato=json"
            if start_date:
                url += f"&dataInicial={start_date}"
            if end_date:
                url += f"&dataFinal={end_date}"

        self.logger.info(f"Fetching {indicator_name} data")

        data = await self._make_request(url)

        FederalAPIMetrics.record_data_fetched(
            api_name="BCB", data_type=indicator_name, record_count=len(data)
        )

        self.logger.info(f"Fetched {len(data)} {indicator_name} data points")

        return data
