"""
Unit tests for Vault client functionality
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from src.core.vault_client import (
    VaultClient, 
    VaultConfig, 
    VaultStatus,
    VaultClientError,
    VaultAuthError,
    VaultUnavailableError,
    VaultCircuitBreakerError,
    SecretEntry
)


@pytest.fixture
def vault_config():
    """Test Vault configuration"""
    return VaultConfig(
        url="http://test-vault:8200",
        token="test-token",
        secret_path="secret/test",
        cache_ttl=60,
        fallback_to_env=True,
        require_vault=False
    )


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client"""
    client = AsyncMock()
    return client


class TestVaultConfig:
    """Test VaultConfig functionality"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = VaultConfig()
        
        assert config.url == "http://localhost:8200"
        assert config.auth_method == "token"
        assert config.cache_ttl == 300
        assert config.fallback_to_env is True
        assert config.require_vault is False
    
    def test_config_from_env(self):
        """Test configuration loading from environment"""
        with patch.dict(os.environ, {
            'VAULT_URL': 'http://prod-vault:8200',
            'VAULT_TOKEN': 'prod-token',
            'VAULT_CACHE_TTL': '600'
        }):
            config = VaultClient._load_config()
            
            assert config.url == 'http://prod-vault:8200'
            assert config.token == 'prod-token'
            assert config.cache_ttl == 600


class TestSecretEntry:
    """Test SecretEntry functionality"""
    
    def test_secret_entry_creation(self):
        """Test secret entry creation"""
        entry = SecretEntry(
            value="test-secret",
            created_at=datetime.utcnow(),
            ttl=300
        )
        
        assert entry.value == "test-secret"
        assert entry.access_count == 0
        assert not entry.is_expired
    
    def test_secret_expiration(self):
        """Test secret expiration logic"""
        old_time = datetime.utcnow() - timedelta(seconds=400)
        entry = SecretEntry(
            value="test-secret",
            created_at=old_time,
            ttl=300
        )
        
        assert entry.is_expired
    
    def test_secret_touch(self):
        """Test access tracking"""
        entry = SecretEntry(
            value="test-secret",
            created_at=datetime.utcnow(),
            ttl=300
        )
        
        initial_time = entry.last_accessed
        entry.touch()
        
        assert entry.access_count == 1
        assert entry.last_accessed >= initial_time


class TestVaultClient:
    """Test VaultClient functionality"""
    
    def test_client_initialization(self, vault_config):
        """Test client initialization"""
        client = VaultClient(vault_config)
        
        assert client.config == vault_config
        assert client._status == VaultStatus.NOT_CONFIGURED
        assert len(client._cache) == 0
    
    @pytest.mark.asyncio
    async def test_client_context_manager(self, vault_config):
        """Test client as context manager"""
        with patch('src.core.vault_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock successful health check
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"sealed": False}
            mock_client.get.return_value = mock_response
            
            async with VaultClient(vault_config) as client:
                assert client._client is not None
    
    @pytest.mark.asyncio
    async def test_authentication_token_success(self, vault_config):
        """Test successful token authentication"""
        client = VaultClient(vault_config)
        
        with patch('src.core.vault_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            client._client = mock_client
            
            # Mock successful token validation
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": {"expire_time": None}}
            mock_client.get.return_value = mock_response
            
            await client._authenticate()
            
            assert client._auth_token == "test-token"
            mock_client.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authentication_token_failure(self, vault_config):
        """Test failed token authentication"""
        client = VaultClient(vault_config)
        
        with patch('src.core.vault_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            client._client = mock_client
            
            # Mock failed token validation
            mock_response = Mock()
            mock_response.status_code = 403
            mock_client.get.return_value = mock_response
            
            with pytest.raises(VaultAuthError):
                await client._authenticate()
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, vault_config):
        """Test successful health check"""
        client = VaultClient(vault_config)
        
        with patch('src.core.vault_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            client._client = mock_client
            
            # Mock healthy response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"sealed": False}
            mock_client.get.return_value = mock_response
            
            result = await client._health_check()
            
            assert result is True
            assert client._status == VaultStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_health_check_sealed(self, vault_config):
        """Test health check with sealed Vault"""
        client = VaultClient(vault_config)
        
        with patch('src.core.vault_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            client._client = mock_client
            
            # Mock sealed response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"sealed": True}
            mock_client.get.return_value = mock_response
            
            result = await client._health_check()
            
            assert result is False
            assert client._status == VaultStatus.DEGRADED
    
    @pytest.mark.asyncio
    async def test_get_secret_vault_success(self, vault_config):
        """Test successful secret retrieval from Vault"""
        client = VaultClient(vault_config)
        client._status = VaultStatus.HEALTHY
        client._auth_token = "test-token"
        
        with patch('src.core.vault_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            client._client = mock_client
            
            # Mock successful secret retrieval
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "data": {
                        "value": "secret-value"
                    }
                }
            }
            mock_client.get.return_value = mock_response
            
            result = await client.get_secret("test-key")
            
            assert result == "secret-value"
            assert "test-key" in client._cache
    
    @pytest.mark.asyncio
    async def test_get_secret_cache_hit(self, vault_config):
        """Test secret retrieval from cache"""
        client = VaultClient(vault_config)
        
        # Pre-populate cache
        client._cache["test-key"] = SecretEntry(
            value="cached-value",
            created_at=datetime.utcnow(),
            ttl=300
        )
        
        result = await client.get_secret("test-key")
        
        assert result == "cached-value"
        assert client._cache_stats["hits"] == 1
    
    @pytest.mark.asyncio
    async def test_get_secret_fallback_to_env(self, vault_config):
        """Test fallback to environment variables"""
        client = VaultClient(vault_config)
        client._status = VaultStatus.UNAVAILABLE
        
        with patch.dict(os.environ, {'TEST_KEY': 'env-value'}):
            result = await client.get_secret("test-key")
            
            assert result == "env-value"
    
    @pytest.mark.asyncio
    async def test_get_secret_not_found(self, vault_config):
        """Test secret not found scenario"""
        client = VaultClient(vault_config)
        client._status = VaultStatus.UNAVAILABLE
        
        result = await client.get_secret("nonexistent-key")
        
        assert result is None
    
    def test_circuit_breaker_open(self, vault_config):
        """Test circuit breaker functionality"""
        client = VaultClient(vault_config)
        
        # Trigger circuit breaker
        for _ in range(vault_config.circuit_breaker_threshold):
            client._record_failure()
        
        assert client._is_circuit_breaker_open()
    
    def test_circuit_breaker_timeout(self, vault_config):
        """Test circuit breaker timeout"""
        client = VaultClient(vault_config)
        
        # Trigger circuit breaker
        for _ in range(vault_config.circuit_breaker_threshold):
            client._record_failure()
        
        assert client._is_circuit_breaker_open()
        
        # Simulate timeout
        client._circuit_breaker_last_failure = datetime.utcnow() - timedelta(
            seconds=vault_config.circuit_breaker_timeout + 10
        )
        
        assert not client._is_circuit_breaker_open()
    
    @pytest.mark.asyncio
    async def test_cache_cleanup(self, vault_config):
        """Test cache cleanup functionality"""
        client = VaultClient(vault_config)
        
        # Add expired entry
        old_time = datetime.utcnow() - timedelta(seconds=400)
        client._cache["expired-key"] = SecretEntry(
            value="expired-value",
            created_at=old_time,
            ttl=300
        )
        
        # Add fresh entry
        client._cache["fresh-key"] = SecretEntry(
            value="fresh-value",
            created_at=datetime.utcnow(),
            ttl=300
        )
        
        await client._cleanup_cache()
        
        assert "expired-key" not in client._cache
        assert "fresh-key" in client._cache
        assert client._cache_stats["evictions"] == 1
    
    @pytest.mark.asyncio
    async def test_set_secret_success(self, vault_config):
        """Test successful secret storage"""
        client = VaultClient(vault_config)
        client._auth_token = "test-token"
        
        with patch('src.core.vault_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            client._client = mock_client
            
            # Mock successful secret storage
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.post.return_value = mock_response
            
            result = await client.set_secret("test-key", "test-value")
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_prevents_requests(self, vault_config):
        """Test circuit breaker prevents requests"""
        client = VaultClient(vault_config)
        
        # Open circuit breaker
        client._circuit_breaker_open = True
        client._circuit_breaker_last_failure = datetime.utcnow()
        
        with pytest.raises(VaultCircuitBreakerError):
            await client._fetch_from_vault("test-key")
    
    def test_get_stats(self, vault_config):
        """Test statistics retrieval"""
        client = VaultClient(vault_config)
        client._status = VaultStatus.HEALTHY
        
        stats = client.get_stats()
        
        assert stats["status"] == VaultStatus.HEALTHY.value
        assert "cache_stats" in stats
        assert "circuit_breaker" in stats
        assert "config" in stats


class TestVaultIntegration:
    """Integration tests for Vault functionality"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_fallback(self, vault_config):
        """Test complete workflow with fallback"""
        vault_config.require_vault = False
        client = VaultClient(vault_config)
        
        # Simulate Vault unavailable
        client._status = VaultStatus.UNAVAILABLE
        
        with patch.dict(os.environ, {'DATABASE_URL': 'postgres://test'}):
            result = await client.get_secret("database/url")
            
            assert result == 'postgres://test'
    
    @pytest.mark.asyncio
    async def test_required_vault_failure(self, vault_config):
        """Test failure when Vault is required but unavailable"""
        vault_config.require_vault = True
        
        with patch('src.core.vault_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock connection failure
            mock_client.get.side_effect = Exception("Connection failed")
            
            client = VaultClient(vault_config)
            
            with pytest.raises(VaultUnavailableError):
                await client.initialize()