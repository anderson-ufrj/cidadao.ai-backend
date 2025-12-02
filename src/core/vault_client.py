"""
HashiCorp Vault Client for Cidadão.AI
Production-grade secret management with fallback strategies
"""

import asyncio
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

import httpx
import structlog

from src.core import json_utils

logger = structlog.get_logger(__name__)


class VaultStatus(Enum):
    """Vault connection status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    NOT_CONFIGURED = "not_configured"


@dataclass
class VaultConfig:
    """Vault client configuration"""

    # Connection settings
    url: str = field(default="http://localhost:8200")
    token: str | None = field(default=None)
    namespace: str | None = field(default=None)
    timeout: int = field(default=10)

    # Authentication
    auth_method: str = field(default="token")  # token, approle, k8s
    role_id: str | None = field(default=None)
    secret_id: str | None = field(default=None)

    # Paths
    secret_path: str = field(default="secret/cidadao-ai")
    transit_path: str = field(default="transit")

    # Cache settings
    cache_ttl: int = field(default=300)  # 5 minutes
    max_cache_size: int = field(default=1000)

    # Retry and circuit breaker
    max_retries: int = field(default=3)
    retry_delay: float = field(default=1.0)
    circuit_breaker_threshold: int = field(default=5)
    circuit_breaker_timeout: int = field(default=60)

    # Fallback strategy
    fallback_to_env: bool = field(default=True)
    require_vault: bool = field(default=False)  # Fail if Vault unavailable


@dataclass
class SecretEntry:
    """Cached secret entry"""

    value: Any
    created_at: datetime
    ttl: int
    last_accessed: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )  # noqa: DTZ005
    access_count: int = field(default=0)

    @property
    def is_expired(self) -> bool:
        """Check if secret is expired"""
        return datetime.now(UTC) > self.created_at + timedelta(seconds=self.ttl)

    def touch(self):
        """Update access statistics"""
        self.last_accessed = datetime.now(UTC)
        self.access_count += 1


class VaultClientError(Exception):
    """Base Vault client error"""

    pass


class VaultUnavailableError(VaultClientError):
    """Vault service is unavailable"""

    pass


class VaultAuthError(VaultClientError):
    """Vault authentication failed"""

    pass


class VaultCircuitBreakerError(VaultClientError):
    """Circuit breaker is open"""

    pass


class VaultClient:
    """
    Production-grade HashiCorp Vault client with:
    - Intelligent caching with TTL
    - Circuit breaker pattern
    - Graceful fallback to environment variables
    - Comprehensive audit logging
    - Health monitoring
    """

    def __init__(self, config: VaultConfig | None = None):
        self.config = config or self._load_config()
        self._client: httpx.AsyncClient | None = None

        # Cache system
        self._cache: dict[str, SecretEntry] = {}
        self._cache_stats = {"hits": 0, "misses": 0, "evictions": 0}

        # Circuit breaker
        self._circuit_breaker_failures = 0
        self._circuit_breaker_last_failure: datetime | None = None
        self._circuit_breaker_open = False

        # Status tracking
        self._status = VaultStatus.NOT_CONFIGURED
        self._last_health_check: datetime | None = None
        self._health_check_interval = 30  # seconds

        # Authentication
        self._auth_token: str | None = None
        self._auth_expires: datetime | None = None

        logger.info(
            "vault_client_initialized",
            vault_url=self.config.url,
            auth_method=self.config.auth_method,
            fallback_enabled=self.config.fallback_to_env,
            cache_ttl=self.config.cache_ttl,
        )

    @classmethod
    def _load_config(cls) -> VaultConfig:
        """Load configuration from environment"""
        return VaultConfig(
            url=os.getenv("VAULT_URL", "http://localhost:8200"),
            token=os.getenv("VAULT_TOKEN"),
            namespace=os.getenv("VAULT_NAMESPACE"),
            timeout=int(os.getenv("VAULT_TIMEOUT", "10")),
            auth_method=os.getenv("VAULT_AUTH_METHOD", "token"),
            role_id=os.getenv("VAULT_ROLE_ID"),
            secret_id=os.getenv("VAULT_SECRET_ID"),
            secret_path=os.getenv("VAULT_SECRET_PATH", "secret/cidadao-ai"),
            cache_ttl=int(os.getenv("VAULT_CACHE_TTL", "300")),
            fallback_to_env=os.getenv("VAULT_FALLBACK_TO_ENV", "true").lower()
            == "true",
            require_vault=os.getenv("VAULT_REQUIRE", "false").lower() == "true",
        )

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def initialize(self):
        """Initialize Vault client and authenticate"""
        try:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                headers=(
                    {"X-Vault-Namespace": self.config.namespace}
                    if self.config.namespace
                    else {}
                ),
            )

            # Test connection and authenticate
            await self._authenticate()
            await self._health_check()

            self._status = VaultStatus.HEALTHY

            logger.info(
                "vault_client_connected",
                vault_url=self.config.url,
                status=self._status.value,
            )

        except Exception as e:
            logger.error(
                "vault_client_initialization_failed",
                error=str(e),
                vault_url=self.config.url,
            )

            if self.config.require_vault:
                raise VaultUnavailableError(f"Vault initialization failed: {e}")

            self._status = VaultStatus.UNAVAILABLE
            logger.warning(
                "vault_fallback_mode_enabled", reason="initialization_failed"
            )

    async def close(self):
        """Close client connections"""
        if self._client:
            await self._client.aclose()
            self._client = None

        logger.info("vault_client_closed")

    async def _authenticate(self):
        """Authenticate with Vault"""
        if not self._client:
            raise VaultClientError("Client not initialized")

        if self.config.auth_method == "token":
            if not self.config.token:
                raise VaultAuthError("Vault token not provided")

            self._auth_token = self.config.token

            # Validate token
            response = await self._client.get(
                f"{self.config.url}/v1/auth/token/lookup-self",
                headers={"X-Vault-Token": self._auth_token},
            )

            if response.status_code != 200:
                raise VaultAuthError(f"Token validation failed: {response.status_code}")

            token_info = response.json()
            if token_info.get("data", {}).get("expire_time"):
                # Parse expiration if available
                pass

            logger.info("vault_token_authenticated")

        elif self.config.auth_method == "approle":
            if not self.config.role_id or not self.config.secret_id:
                raise VaultAuthError("AppRole credentials not provided")

            # AppRole login
            login_data = {
                "role_id": self.config.role_id,
                "secret_id": self.config.secret_id,
            }

            response = await self._client.post(
                f"{self.config.url}/v1/auth/approle/login", json=login_data
            )

            if response.status_code != 200:
                raise VaultAuthError(f"AppRole login failed: {response.status_code}")

            auth_data = response.json()["auth"]
            self._auth_token = auth_data["client_token"]

            # Set expiration
            if auth_data.get("lease_duration"):
                self._auth_expires = datetime.now(UTC) + timedelta(
                    seconds=auth_data["lease_duration"]
                )

            logger.info(
                "vault_approle_authenticated",
                lease_duration=auth_data.get("lease_duration", 0),
            )

        else:
            raise VaultAuthError(f"Unsupported auth method: {self.config.auth_method}")

    async def _health_check(self) -> bool:
        """Perform Vault health check"""
        if not self._client:
            return False

        try:
            response = await self._client.get(f"{self.config.url}/v1/sys/health")

            if response.status_code == 200:
                health_data = response.json()
                is_healthy = not health_data.get("sealed", True)

                if is_healthy:
                    self._status = VaultStatus.HEALTHY
                    self._circuit_breaker_failures = 0
                    self._circuit_breaker_open = False
                else:
                    self._status = VaultStatus.DEGRADED

                self._last_health_check = datetime.now(UTC)
                return is_healthy

        except Exception as e:
            logger.warning("vault_health_check_failed", error=str(e))

        self._status = VaultStatus.UNAVAILABLE
        return False

    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open"""
        if not self._circuit_breaker_open:
            return False

        # Check if timeout has passed
        if self._circuit_breaker_last_failure and datetime.now(
            UTC
        ) > self._circuit_breaker_last_failure + timedelta(
            seconds=self.config.circuit_breaker_timeout
        ):

            self._circuit_breaker_open = False
            logger.info("vault_circuit_breaker_closed")
            return False

        return True

    def _record_failure(self):
        """Record a failure for circuit breaker"""
        self._circuit_breaker_failures += 1
        self._circuit_breaker_last_failure = datetime.now(UTC)

        if self._circuit_breaker_failures >= self.config.circuit_breaker_threshold:
            self._circuit_breaker_open = True
            logger.warning(
                "vault_circuit_breaker_opened",
                failure_count=self._circuit_breaker_failures,
            )

    async def get_secret(self, key: str, version: int | None = None) -> str | None:
        """
        Get secret value with intelligent caching and fallback

        Args:
            key: Secret key name
            version: KV version (for versioned secrets)

        Returns:
            Secret value or None if not found
        """
        cache_key = f"{key}:{version}" if version else key

        # Check cache first
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if not entry.is_expired:
                entry.touch()
                self._cache_stats["hits"] += 1

                logger.debug(
                    "vault_secret_cache_hit",
                    key=key,
                    version=version,
                    access_count=entry.access_count,
                )

                return entry.value
            # Remove expired entry
            del self._cache[cache_key]

        self._cache_stats["misses"] += 1

        # Try Vault if available
        if self._status in [VaultStatus.HEALTHY, VaultStatus.DEGRADED]:
            try:
                value = await self._fetch_from_vault(key, version)
                if value is not None:
                    # Cache the value
                    self._cache[cache_key] = SecretEntry(
                        value=value,
                        created_at=datetime.now(UTC),
                        ttl=self.config.cache_ttl,
                    )

                    # Cleanup cache if too large
                    await self._cleanup_cache()

                    logger.info(
                        "vault_secret_retrieved",
                        key=key,
                        version=version,
                        source="vault",
                    )

                    return value

            except Exception as e:
                logger.error("vault_secret_fetch_failed", key=key, error=str(e))
                self._record_failure()

        # Fallback to environment variable
        if self.config.fallback_to_env:
            env_value = os.getenv(key.upper().replace("-", "_").replace("/", "_"))
            if env_value:
                logger.info("vault_secret_retrieved", key=key, source="environment")
                return env_value

        logger.warning(
            "vault_secret_not_found",
            key=key,
            version=version,
            vault_status=self._status.value,
        )

        return None

    async def _fetch_from_vault(
        self, key: str, version: int | None = None
    ) -> str | None:
        """Fetch secret directly from Vault"""
        if self._is_circuit_breaker_open():
            raise VaultCircuitBreakerError("Circuit breaker is open")

        if not self._client or not self._auth_token:
            raise VaultClientError("Client not authenticated")

        # Check token expiration
        if self._auth_expires and datetime.now(UTC) > self._auth_expires:
            await self._authenticate()

        # Build URL based on KV version
        if version:
            url = f"{self.config.url}/v1/{self.config.secret_path}/data/{key}"
            params = {"version": str(version)}
        else:
            url = f"{self.config.url}/v1/{self.config.secret_path}/data/{key}"
            params = {}

        headers = {"X-Vault-Token": self._auth_token}

        for attempt in range(self.config.max_retries):
            try:
                response = await self._client.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    data = response.json()

                    # Handle KV v2 format
                    if "data" in data and "data" in data["data"]:
                        secret_data = data["data"]["data"]
                    else:
                        secret_data = data.get("data", {})

                    # Return the specific field or the entire secret
                    if isinstance(secret_data, dict):
                        return secret_data.get("value") or json_utils.dumps(secret_data)
                    return str(secret_data)

                if response.status_code == 404:
                    return None

                if response.status_code == 403:
                    raise VaultAuthError("Access denied to secret")

                raise VaultClientError(f"Vault API error: {response.status_code}")

            except httpx.RequestError as e:
                if attempt == self.config.max_retries - 1:
                    raise VaultClientError(f"Network error: {e}")

                await asyncio.sleep(self.config.retry_delay * (2**attempt))

        raise VaultClientError("Max retries exceeded")

    async def _cleanup_cache(self):
        """Cleanup expired entries and enforce size limits"""
        now = datetime.now(UTC)

        # Remove expired entries
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired]

        for key in expired_keys:
            del self._cache[key]

        self._cache_stats["evictions"] += len(expired_keys)

        # Enforce size limit (LRU eviction)
        if len(self._cache) > self.config.max_cache_size:
            # Sort by last accessed time and remove oldest
            sorted_items = sorted(self._cache.items(), key=lambda x: x[1].last_accessed)

            to_remove = len(self._cache) - self.config.max_cache_size
            for key, _ in sorted_items[:to_remove]:
                del self._cache[key]
                self._cache_stats["evictions"] += 1

    async def set_secret(
        self, key: str, value: str, metadata: dict | None = None
    ) -> bool:
        """Set a secret value in Vault"""
        if self._is_circuit_breaker_open():
            raise VaultCircuitBreakerError("Circuit breaker is open")

        if not self._client or not self._auth_token:
            raise VaultClientError("Client not authenticated")

        url = f"{self.config.url}/v1/{self.config.secret_path}/data/{key}"
        headers = {"X-Vault-Token": self._auth_token}

        payload = {"data": {"value": value, **(metadata or {})}}

        try:
            response = await self._client.post(url, headers=headers, json=payload)

            if response.status_code in [200, 204]:
                # Invalidate cache
                cache_keys_to_remove = [
                    k for k in self._cache.keys() if k.startswith(key)
                ]
                for cache_key in cache_keys_to_remove:
                    del self._cache[cache_key]

                logger.info("vault_secret_stored", key=key)
                return True

            logger.error(
                "vault_secret_store_failed",
                key=key,
                status_code=response.status_code,
            )
            return False

        except Exception as e:
            logger.error("vault_secret_store_error", key=key, error=str(e))
            self._record_failure()
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get client statistics"""
        return {
            "status": self._status.value,
            "cache_stats": self._cache_stats,
            "cache_size": len(self._cache),
            "circuit_breaker": {
                "open": self._circuit_breaker_open,
                "failures": self._circuit_breaker_failures,
                "last_failure": (
                    self._circuit_breaker_last_failure.isoformat()
                    if self._circuit_breaker_last_failure
                    else None
                ),
            },
            "last_health_check": (
                self._last_health_check.isoformat() if self._last_health_check else None
            ),
            "config": {
                "url": self.config.url,
                "auth_method": self.config.auth_method,
                "cache_ttl": self.config.cache_ttl,
                "fallback_enabled": self.config.fallback_to_env,
            },
        }


# Global client instance
_vault_client: VaultClient | None = None


async def get_vault_client(config: VaultConfig | None = None) -> VaultClient:
    """Get or create global Vault client instance"""
    global _vault_client

    if _vault_client is None:
        _vault_client = VaultClient(config)
        await _vault_client.initialize()

    return _vault_client


async def close_vault_client():
    """Close global Vault client"""
    global _vault_client

    if _vault_client:
        await _vault_client.close()
        _vault_client = None
