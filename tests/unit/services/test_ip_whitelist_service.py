"""Tests for IP whitelist service."""

import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import Mock, AsyncMock, patch

from src.services.ip_whitelist_service import IPWhitelistService, IPWhitelist
from src.core.config import settings


@pytest.fixture
def ip_whitelist_service():
    """Create IP whitelist service instance."""
    return IPWhitelistService()


@pytest.fixture
async def mock_db_session():
    """Create mock database session."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.execute = AsyncMock()
    session.add = Mock()
    return session


class TestIPWhitelistService:
    """Test IP whitelist service."""
    
    async def test_add_single_ip(self, ip_whitelist_service, mock_db_session):
        """Test adding a single IP address."""
        # Mock query result
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        
        # Add IP
        entry = await ip_whitelist_service.add_ip(
            session=mock_db_session,
            ip_address="192.168.1.100",
            created_by="admin@test.com",
            description="Test IP",
            environment="production"
        )
        
        # Verify
        assert entry.ip_address == "192.168.1.100"
        assert entry.created_by == "admin@test.com"
        assert entry.description == "Test IP"
        assert entry.environment == "production"
        assert entry.is_cidr is False
        assert entry.active is True
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    async def test_add_cidr_range(self, ip_whitelist_service, mock_db_session):
        """Test adding a CIDR range."""
        # Mock query result
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        
        # Add CIDR
        entry = await ip_whitelist_service.add_ip(
            session=mock_db_session,
            ip_address="10.0.0.0/24",
            created_by="admin@test.com",
            description="Test subnet",
            environment="production",
            is_cidr=True
        )
        
        # Verify
        assert entry.ip_address == "10.0.0.0"
        assert entry.is_cidr is True
        assert entry.cidr_prefix == 24
        assert entry.active is True
    
    async def test_add_duplicate_ip_fails(self, ip_whitelist_service, mock_db_session):
        """Test adding duplicate IP fails."""
        # Mock existing entry
        existing = Mock(spec=IPWhitelist)
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = existing
        
        # Try to add duplicate
        with pytest.raises(ValueError, match="already whitelisted"):
            await ip_whitelist_service.add_ip(
                session=mock_db_session,
                ip_address="192.168.1.100",
                created_by="admin@test.com"
            )
    
    async def test_add_invalid_ip_fails(self, ip_whitelist_service, mock_db_session):
        """Test adding invalid IP fails."""
        with pytest.raises(ValueError, match="Invalid IP address format"):
            await ip_whitelist_service.add_ip(
                session=mock_db_session,
                ip_address="not.an.ip.address",
                created_by="admin@test.com"
            )
    
    async def test_check_ip_exact_match(self, ip_whitelist_service, mock_db_session):
        """Test checking IP with exact match."""
        # Mock whitelist entries
        entries = [
            Mock(
                ip_address="192.168.1.100",
                is_cidr=False,
                active=True,
                expires_at=None
            ),
            Mock(
                ip_address="10.0.0.0",
                is_cidr=True,
                cidr_prefix=24,
                active=True,
                expires_at=None
            )
        ]
        
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = entries
        
        # Force cache reload
        ip_whitelist_service._last_cache_update = None
        
        # Check whitelisted IP
        result = await ip_whitelist_service.check_ip(
            session=mock_db_session,
            ip_address="192.168.1.100",
            environment="production"
        )
        assert result is True
    
    async def test_check_ip_cidr_match(self, ip_whitelist_service, mock_db_session):
        """Test checking IP within CIDR range."""
        # Mock whitelist entries
        entries = [
            Mock(
                ip_address="10.0.0.0",
                is_cidr=True,
                cidr_prefix=24,
                active=True,
                expires_at=None
            )
        ]
        
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = entries
        
        # Force cache reload
        ip_whitelist_service._last_cache_update = None
        
        # Check IP in range
        result = await ip_whitelist_service.check_ip(
            session=mock_db_session,
            ip_address="10.0.0.50",
            environment="production"
        )
        assert result is True
        
        # Check IP outside range
        result = await ip_whitelist_service.check_ip(
            session=mock_db_session,
            ip_address="10.0.1.50",
            environment="production"
        )
        assert result is False
    
    async def test_check_ip_expired_entry(self, ip_whitelist_service, mock_db_session):
        """Test expired entries are ignored."""
        # Mock expired entry
        entries = [
            Mock(
                ip_address="192.168.1.100",
                is_cidr=False,
                active=True,
                expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
            )
        ]
        
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = entries
        
        # Force cache reload
        ip_whitelist_service._last_cache_update = None
        
        # Check expired IP
        result = await ip_whitelist_service.check_ip(
            session=mock_db_session,
            ip_address="192.168.1.100",
            environment="production"
        )
        assert result is False
    
    async def test_remove_ip(self, ip_whitelist_service, mock_db_session):
        """Test removing IP from whitelist."""
        # Mock delete result
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_db_session.execute.return_value = mock_result
        
        # Remove IP
        result = await ip_whitelist_service.remove_ip(
            session=mock_db_session,
            ip_address="192.168.1.100",
            environment="production"
        )
        
        assert result is True
        mock_db_session.commit.assert_called_once()
    
    async def test_update_ip(self, ip_whitelist_service, mock_db_session):
        """Test updating whitelist entry."""
        # Mock existing entry
        entry = Mock(spec=IPWhitelist)
        entry.ip_address = "192.168.1.100"
        entry.active = True
        entry.description = "Old description"
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = entry
        
        # Update entry
        result = await ip_whitelist_service.update_ip(
            session=mock_db_session,
            ip_address="192.168.1.100",
            environment="production",
            active=False,
            description="New description"
        )
        
        assert result is not None
        assert entry.active is False
        assert entry.description == "New description"
        mock_db_session.commit.assert_called_once()
    
    def test_get_default_whitelist_development(self, ip_whitelist_service):
        """Test default whitelist for development."""
        with patch.object(settings, 'is_development', True):
            defaults = ip_whitelist_service.get_default_whitelist()
            
            # Should include localhost and private networks
            assert "127.0.0.1" in defaults
            assert "::1" in defaults
            assert "10.0.0.0/8" in defaults
            assert "192.168.0.0/16" in defaults
    
    def test_get_default_whitelist_production(self, ip_whitelist_service):
        """Test default whitelist for production."""
        with patch.object(settings, 'is_production', True):
            defaults = ip_whitelist_service.get_default_whitelist()
            
            # Should include localhost and service IPs
            assert "127.0.0.1" in defaults
            assert "::1" in defaults
            # Should have cloud provider ranges
            assert any("76." in ip for ip in defaults)  # Vercel
            assert any("34." in ip for ip in defaults)  # Google Cloud
    
    async def test_cleanup_expired(self, ip_whitelist_service, mock_db_session):
        """Test cleaning up expired entries."""
        # Mock delete result
        mock_result = Mock()
        mock_result.rowcount = 5
        mock_db_session.execute.return_value = mock_result
        
        # Cleanup
        count = await ip_whitelist_service.cleanup_expired(
            session=mock_db_session,
            environment="production"
        )
        
        assert count == 5
        mock_db_session.commit.assert_called_once()
    
    def test_ip_whitelist_model_matches(self):
        """Test IPWhitelist model matching logic."""
        # Test exact match
        entry = IPWhitelist(
            id="test",
            ip_address="192.168.1.100",
            is_cidr=False,
            active=True,
            created_by="test"
        )
        assert entry.matches("192.168.1.100") is True
        assert entry.matches("192.168.1.101") is False
        
        # Test CIDR match
        entry_cidr = IPWhitelist(
            id="test",
            ip_address="10.0.0.0",
            is_cidr=True,
            cidr_prefix=24,
            active=True,
            created_by="test"
        )
        assert entry_cidr.matches("10.0.0.1") is True
        assert entry_cidr.matches("10.0.0.255") is True
        assert entry_cidr.matches("10.0.1.1") is False
        
        # Test inactive entry
        entry.active = False
        assert entry.matches("192.168.1.100") is False