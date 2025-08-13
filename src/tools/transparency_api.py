"""
Module: tools.transparency_api
Description: Client for Portal da Transparência API
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, Field as PydanticField, validator

from src.core import get_logger, settings
from src.core.exceptions import (
    DataNotFoundError,
    DataSourceError,
    TransparencyAPIError,
)


class APIRateLimit:
    """Rate limiter for API requests."""
    
    def __init__(self, max_requests_per_minute: int = 90):
        self.max_requests = max_requests_per_minute
        self.requests = []
        self.logger = get_logger(__name__)
    
    async def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded."""
        now = datetime.now()
        
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < timedelta(minutes=1)]
        
        if len(self.requests) >= self.max_requests:
            # Calculate wait time
            oldest_request = min(self.requests)
            wait_time = 60 - (now - oldest_request).total_seconds()
            
            if wait_time > 0:
                self.logger.warning(
                    "rate_limit_reached",
                    wait_time=wait_time,
                    requests_count=len(self.requests),
                )
                await asyncio.sleep(wait_time)
                
                # Clean up old requests again after waiting
                now = datetime.now()
                self.requests = [req_time for req_time in self.requests 
                                if now - req_time < timedelta(minutes=1)]
        
        # Record this request
        self.requests.append(now)


class TransparencyAPIFilter(BaseModel):
    """Filter parameters for API requests."""
    
    ano: Optional[int] = PydanticField(default=None, description="Year")
    mes: Optional[int] = PydanticField(default=None, ge=1, le=12, description="Month")
    data_inicio: Optional[str] = PydanticField(default=None, description="Start date (DD/MM/YYYY)")
    data_fim: Optional[str] = PydanticField(default=None, description="End date (DD/MM/YYYY)")
    valor_inicial: Optional[float] = PydanticField(default=None, description="Minimum value")
    valor_final: Optional[float] = PydanticField(default=None, description="Maximum value")
    codigo_orgao: Optional[str] = PydanticField(default=None, description="Organization code (required for contratos/licitacoes)")
    orgao: Optional[str] = PydanticField(default=None, description="Organization code (legacy)")
    cnpj_contratado: Optional[str] = PydanticField(default=None, description="Contracted CNPJ")
    modalidade: Optional[int] = PydanticField(default=None, description="Bidding modality")
    pagina: int = PydanticField(default=1, ge=1, description="Page number")
    tamanho_pagina: int = PydanticField(default=20, ge=1, le=500, description="Page size")
    
    @validator('data_inicio', 'data_fim')
    def validate_date_format(cls, v):
        """Validate date format."""
        if v is not None:
            try:
                datetime.strptime(v, '%d/%m/%Y')
            except ValueError:
                raise ValueError('Date must be in DD/MM/YYYY format')
        return v
    
    def to_params(self) -> Dict[str, Any]:
        """Convert to query parameters."""
        params = {}
        for field, value in self.dict(exclude_none=True).items():
            if value is not None:
                # Convert snake_case to camelCase for API
                if field == "data_inicio":
                    params["dataInicio"] = value
                elif field == "data_fim":
                    params["dataFim"] = value
                elif field == "valor_inicial":
                    params["valorInicial"] = value
                elif field == "valor_final":
                    params["valorFinal"] = value
                elif field == "cnpj_contratado":
                    params["cnpjContratado"] = value
                elif field == "tamanho_pagina":
                    params["tamanhoPagina"] = value
                elif field == "codigo_orgao":
                    params["codigoOrgao"] = value
                elif field == "orgao":
                    # Legacy support - convert to codigoOrgao
                    params["codigoOrgao"] = value
                else:
                    params[field] = value
        return params


class TransparencyAPIResponse(BaseModel):
    """Response from Transparency API."""
    
    data: List[Dict[str, Any]] = PydanticField(default_factory=list)
    links: Optional[Dict[str, str]] = PydanticField(default=None)
    meta: Optional[Dict[str, Any]] = PydanticField(default=None)
    total_records: int = PydanticField(default=0)
    current_page: int = PydanticField(default=1)
    total_pages: int = PydanticField(default=1)


class TransparencyAPIClient:
    """
    Client for Portal da Transparência API.
    
    Handles authentication, rate limiting, caching, and error handling.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_per_minute: int = 90,
    ):
        """
        Initialize the API client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            rate_limit_per_minute: Maximum requests per minute
        """
        self.api_key = api_key or settings.transparency_api_key.get_secret_value()
        self.base_url = base_url or settings.transparency_api_base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.header_key = settings.transparency_api_header_key
        
        self.rate_limiter = APIRateLimit(rate_limit_per_minute)
        self.logger = get_logger(__name__)
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
        
        self.logger.info(
            "transparency_api_client_initialized",
            base_url=self.base_url,
            rate_limit=rate_limit_per_minute,
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            self.header_key: self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "CidadaoAI/1.0.0",
        }
    
    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an API request with retry logic.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response data
            
        Raises:
            TransparencyAPIError: If request fails
        """
        url = urljoin(self.base_url, endpoint)
        headers = self._get_headers()
        
        # Wait for rate limit if needed
        await self.rate_limiter.wait_if_needed()
        
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.info(
                    "api_request_started",
                    url=url,
                    params=params,
                    attempt=attempt + 1,
                )
                
                response = await self.client.get(
                    url,
                    params=params,
                    headers=headers,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    self.logger.info(
                        "api_request_success",
                        url=url,
                        status_code=response.status_code,
                        response_size=len(str(data)),
                    )
                    
                    return data
                
                elif response.status_code == 429:
                    # Rate limit exceeded
                    retry_after = int(response.headers.get("Retry-After", 60))
                    
                    self.logger.warning(
                        "api_rate_limit_exceeded",
                        retry_after=retry_after,
                        attempt=attempt + 1,
                    )
                    
                    if attempt < self.max_retries:
                        await asyncio.sleep(retry_after)
                        continue
                    
                    raise TransparencyAPIError(
                        "Rate limit exceeded",
                        error_code="RATE_LIMIT_EXCEEDED",
                        details={"retry_after": retry_after}
                    )
                
                elif response.status_code == 404:
                    raise DataNotFoundError(
                        f"Data not found for endpoint: {endpoint}",
                        details={"endpoint": endpoint, "params": params}
                    )
                
                else:
                    # Other HTTP errors
                    error_msg = f"API request failed with status {response.status_code}"
                    
                    try:
                        error_data = response.json()
                        error_msg += f": {error_data}"
                    except:
                        error_msg += f": {response.text}"
                    
                    self.logger.error(
                        "api_request_failed",
                        url=url,
                        status_code=response.status_code,
                        error=error_msg,
                        attempt=attempt + 1,
                    )
                    
                    if attempt < self.max_retries:
                        # Exponential backoff
                        await asyncio.sleep(2 ** attempt)
                        continue
                    
                    raise TransparencyAPIError(
                        error_msg,
                        error_code=f"HTTP_{response.status_code}",
                        details={"status_code": response.status_code}
                    )
            
            except httpx.TimeoutException:
                self.logger.error(
                    "api_request_timeout",
                    url=url,
                    timeout=self.timeout,
                    attempt=attempt + 1,
                )
                
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                
                raise TransparencyAPIError(
                    f"Request timeout after {self.timeout} seconds",
                    error_code="TIMEOUT",
                    details={"timeout": self.timeout}
                )
            
            except Exception as e:
                self.logger.error(
                    "api_request_error",
                    url=url,
                    error=str(e),
                    attempt=attempt + 1,
                )
                
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                
                raise TransparencyAPIError(
                    f"Unexpected error: {str(e)}",
                    error_code="UNEXPECTED_ERROR",
                    details={"original_error": str(e)}
                )
        
        raise TransparencyAPIError(
            f"Failed after {self.max_retries + 1} attempts",
            error_code="MAX_RETRIES_EXCEEDED"
        )
    
    def _parse_response(self, data: Dict[str, Any]) -> TransparencyAPIResponse:
        """Parse API response into structured format."""
        # Handle different response formats
        if isinstance(data, list):
            # Simple list response
            return TransparencyAPIResponse(
                data=data,
                total_records=len(data),
                current_page=1,
                total_pages=1,
            )
        
        elif isinstance(data, dict):
            # Paginated response
            response_data = data.get("data", data.get("items", []))
            links = data.get("links", {})
            meta = data.get("meta", {})
            
            return TransparencyAPIResponse(
                data=response_data,
                links=links,
                meta=meta,
                total_records=meta.get("total", len(response_data)),
                current_page=meta.get("current_page", 1),
                total_pages=meta.get("last_page", 1),
            )
        
        else:
            # Unexpected format
            return TransparencyAPIResponse(
                data=[],
                total_records=0,
            )
    
    # Specific endpoint methods
    
    async def get_contracts(
        self,
        filters: Optional[TransparencyAPIFilter] = None,
    ) -> TransparencyAPIResponse:
        """
        Get government contracts.
        
        Args:
            filters: Filter parameters
            
        Returns:
            Contracts data
        """
        params = filters.to_params() if filters else {}
        data = await self._make_request("/api-de-dados/contratos", params)
        return self._parse_response(data)
    
    async def get_expenses(
        self,
        filters: Optional[TransparencyAPIFilter] = None,
    ) -> TransparencyAPIResponse:
        """
        Get government expenses.
        
        Args:
            filters: Filter parameters
            
        Returns:
            Expenses data
        """
        params = filters.to_params() if filters else {}
        data = await self._make_request("/api-de-dados/despesas", params)
        return self._parse_response(data)
    
    async def get_agreements(
        self,
        filters: Optional[TransparencyAPIFilter] = None,
    ) -> TransparencyAPIResponse:
        """
        Get government agreements (convênios).
        
        Args:
            filters: Filter parameters
            
        Returns:
            Agreements data
        """
        params = filters.to_params() if filters else {}
        data = await self._make_request("/api-de-dados/convenios", params)
        return self._parse_response(data)
    
    async def get_biddings(
        self,
        filters: Optional[TransparencyAPIFilter] = None,
    ) -> TransparencyAPIResponse:
        """
        Get government biddings (licitações).
        
        Args:
            filters: Filter parameters
            
        Returns:
            Biddings data
        """
        params = filters.to_params() if filters else {}
        data = await self._make_request("/api-de-dados/licitacoes", params)
        return self._parse_response(data)
    
    async def get_servants(
        self,
        filters: Optional[TransparencyAPIFilter] = None,
    ) -> TransparencyAPIResponse:
        """
        Get government servants.
        
        Args:
            filters: Filter parameters
            
        Returns:
            Servants data
        """
        params = filters.to_params() if filters else {}
        data = await self._make_request("/api-de-dados/servidores", params)
        return self._parse_response(data)
    
    async def search_data(
        self,
        endpoint: str,
        filters: Optional[TransparencyAPIFilter] = None,
        custom_params: Optional[Dict[str, Any]] = None,
    ) -> TransparencyAPIResponse:
        """
        Generic search method for any endpoint.
        
        Args:
            endpoint: API endpoint
            filters: Standard filter parameters
            custom_params: Additional custom parameters
            
        Returns:
            Search results
        """
        params = {}
        
        if filters:
            params.update(filters.to_params())
        
        if custom_params:
            params.update(custom_params)
        
        data = await self._make_request(endpoint, params)
        return self._parse_response(data)
    
    async def get_all_pages(
        self,
        endpoint: str,
        filters: Optional[TransparencyAPIFilter] = None,
        max_pages: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get all pages of data from an endpoint.
        
        Args:
            endpoint: API endpoint
            filters: Filter parameters
            max_pages: Maximum number of pages to fetch
            
        Returns:
            All data from all pages
        """
        all_data = []
        current_filters = filters or TransparencyAPIFilter()
        
        for page in range(1, max_pages + 1):
            current_filters.pagina = page
            
            try:
                response = await self.search_data(endpoint, current_filters)
                
                if not response.data:
                    break
                
                all_data.extend(response.data)
                
                self.logger.info(
                    "page_fetched",
                    endpoint=endpoint,
                    page=page,
                    records=len(response.data),
                    total_so_far=len(all_data),
                )
                
                # Check if this is the last page
                if page >= response.total_pages:
                    break
                
            except DataNotFoundError:
                break
            except Exception as e:
                self.logger.error(
                    "page_fetch_failed",
                    endpoint=endpoint,
                    page=page,
                    error=str(e),
                )
                break
        
        self.logger.info(
            "all_pages_fetched",
            endpoint=endpoint,
            total_records=len(all_data),
            pages_fetched=page,
        )
        
        return all_data


# Factory function for easy client creation
def create_transparency_client(**kwargs) -> TransparencyAPIClient:
    """
    Create a Transparency API client with default settings.
    
    Args:
        **kwargs: Override default settings
        
    Returns:
        Configured API client
    """
    return TransparencyAPIClient(**kwargs)