"""Unit tests for security middleware."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import time

from src.api.middleware.security import (
    SecurityMiddleware,
    RateLimiter,
    IPBlocker,
    CSRFProtection,
    SecurityHeaders
)
from src.core.exceptions import RateLimitError, SecurityError


class TestSecurityMiddleware:
    """Test SecurityMiddleware class."""
    
    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        app = MagicMock()
        return SecurityMiddleware(app)
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.100"
        request.headers = {
            "user-agent": "Mozilla/5.0",
            "content-type": "application/json"
        }
        request.url.path = "/api/v1/test"
        request.method = "GET"
        return request
    
    @pytest.mark.asyncio
    async def test_security_headers_applied(self, middleware, mock_request):
        """Test security headers are applied to response."""
        # Mock call_next
        response = Response(content="test")
        call_next = AsyncMock(return_value=response)
        
        # Process request
        result = await middleware.dispatch(mock_request, call_next)
        
        # Check security headers
        assert "X-Content-Type-Options" in result.headers
        assert result.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in result.headers
        assert result.headers["X-Frame-Options"] == "DENY"
        assert "X-XSS-Protection" in result.headers
        assert "Strict-Transport-Security" in result.headers
    
    @pytest.mark.asyncio
    async def test_request_validation_sql_injection(self, middleware, mock_request):
        """Test SQL injection pattern detection."""
        # Add SQL injection pattern to request
        mock_request.url.path = "/api/v1/users?id=1' OR '1'='1"
        
        call_next = AsyncMock()
        
        # Should block the request
        response = await middleware.dispatch(mock_request, call_next)
        
        assert response.status_code == 400
        assert "Invalid request" in response.body.decode()
    
    @pytest.mark.asyncio
    async def test_request_validation_xss(self, middleware, mock_request):
        """Test XSS pattern detection."""
        # Add XSS pattern to request
        mock_request.url.path = "/api/v1/search?q=<script>alert('xss')</script>"
        
        call_next = AsyncMock()
        
        # Should block the request
        response = await middleware.dispatch(mock_request, call_next)
        
        assert response.status_code == 400
        assert "Invalid request" in response.body.decode()
    
    @pytest.mark.asyncio
    async def test_request_validation_path_traversal(self, middleware, mock_request):
        """Test path traversal pattern detection."""
        # Add path traversal pattern
        mock_request.url.path = "/api/v1/files/../../etc/passwd"
        
        call_next = AsyncMock()
        
        # Should block the request
        response = await middleware.dispatch(mock_request, call_next)
        
        assert response.status_code == 400
        assert "Invalid request" in response.body.decode()
    
    @pytest.mark.asyncio
    async def test_content_type_validation(self, middleware, mock_request):
        """Test content type validation."""
        # Set invalid content type for POST
        mock_request.method = "POST"
        mock_request.headers["content-type"] = "text/plain"
        
        call_next = AsyncMock()
        
        # Should require proper content type
        response = await middleware.dispatch(mock_request, call_next)
        
        assert response.status_code == 415
        assert "Unsupported media type" in response.body.decode()
    
    @pytest.mark.asyncio
    async def test_request_size_limit(self, middleware, mock_request):
        """Test request size limiting."""
        # Set large content length
        mock_request.headers["content-length"] = str(11 * 1024 * 1024)  # 11MB
        
        call_next = AsyncMock()
        
        # Should block large requests
        response = await middleware.dispatch(mock_request, call_next)
        
        assert response.status_code == 413
        assert "Request too large" in response.body.decode()


class TestRateLimiter:
    """Test RateLimiter class."""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance."""
        return RateLimiter(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000
        )
    
    def test_rate_limit_allows_initial_requests(self, rate_limiter):
        """Test rate limiter allows initial requests."""
        client_id = "test_client_1"
        
        # First few requests should be allowed
        for _ in range(5):
            assert rate_limiter.is_allowed(client_id) is True
    
    def test_rate_limit_minute_limit(self, rate_limiter):
        """Test per-minute rate limiting."""
        client_id = "test_client_2"
        
        # Make 60 requests (the limit)
        for _ in range(60):
            assert rate_limiter.is_allowed(client_id) is True
        
        # 61st request should be blocked
        assert rate_limiter.is_allowed(client_id) is False
    
    def test_rate_limit_reset_after_time(self, rate_limiter):
        """Test rate limit resets after time window."""
        client_id = "test_client_3"
        
        # Use up the minute limit
        rate_limiter._minute_requests[client_id] = 60
        rate_limiter._minute_window[client_id] = time.time()
        
        # Should be blocked
        assert rate_limiter.is_allowed(client_id) is False
        
        # Simulate time passing (61 seconds)
        rate_limiter._minute_window[client_id] = time.time() - 61
        
        # Should be allowed again
        assert rate_limiter.is_allowed(client_id) is True
    
    def test_rate_limit_different_clients(self, rate_limiter):
        """Test rate limits are per-client."""
        client1 = "client_1"
        client2 = "client_2"
        
        # Use up limit for client1
        for _ in range(60):
            rate_limiter.is_allowed(client1)
        
        # client1 should be blocked
        assert rate_limiter.is_allowed(client1) is False
        
        # client2 should still be allowed
        assert rate_limiter.is_allowed(client2) is True
    
    def test_token_bucket_burst(self, rate_limiter):
        """Test token bucket allows burst traffic."""
        client_id = "burst_client"
        
        # Should allow initial burst
        for _ in range(10):
            assert rate_limiter.is_allowed(client_id) is True
        
        # Wait a bit to accumulate tokens (simulate 1 second)
        time.sleep(0.1)  # Short sleep for testing
        
        # Should still be allowed due to token accumulation
        assert rate_limiter.is_allowed(client_id) is True


class TestIPBlocker:
    """Test IPBlocker class."""
    
    @pytest.fixture
    def ip_blocker(self):
        """Create IP blocker instance."""
        return IPBlocker()
    
    def test_ip_blocking_after_failures(self, ip_blocker):
        """Test IP gets blocked after multiple failures."""
        ip = "192.168.1.100"
        
        # Record failures
        for _ in range(5):
            ip_blocker.record_failure(ip)
        
        # IP should be blocked
        assert ip_blocker.is_blocked(ip) is True
    
    def test_ip_not_blocked_initially(self, ip_blocker):
        """Test IP is not blocked initially."""
        ip = "192.168.1.101"
        
        assert ip_blocker.is_blocked(ip) is False
    
    def test_ip_unblock_after_timeout(self, ip_blocker):
        """Test IP gets unblocked after timeout."""
        ip = "192.168.1.102"
        
        # Block the IP
        ip_blocker._blocked_ips[ip] = time.time() - 3601  # 1 hour + 1 second ago
        
        # Should be unblocked
        assert ip_blocker.is_blocked(ip) is False
    
    def test_whitelist_never_blocked(self, ip_blocker):
        """Test whitelisted IPs are never blocked."""
        # Add localhost to whitelist
        ip_blocker._whitelist.add("127.0.0.1")
        
        # Record many failures
        for _ in range(10):
            ip_blocker.record_failure("127.0.0.1")
        
        # Should not be blocked
        assert ip_blocker.is_blocked("127.0.0.1") is False
    
    def test_private_network_detection(self, ip_blocker):
        """Test private network IP detection."""
        private_ips = [
            "10.0.0.1",
            "172.16.0.1",
            "192.168.1.1",
            "127.0.0.1"
        ]
        
        for ip in private_ips:
            assert ip_blocker._is_private_network(ip) is True
        
        # Public IP should not be private
        assert ip_blocker._is_private_network("8.8.8.8") is False


class TestCSRFProtection:
    """Test CSRF protection."""
    
    @pytest.fixture
    def csrf_protection(self):
        """Create CSRF protection instance."""
        with patch("src.api.middleware.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test_secret_key"
            return CSRFProtection()
    
    def test_generate_csrf_token(self, csrf_protection):
        """Test CSRF token generation."""
        session_id = "test_session_123"
        
        token = csrf_protection.generate_token(session_id)
        
        assert token is not None
        assert len(token) > 20
        assert isinstance(token, str)
    
    def test_validate_csrf_token_valid(self, csrf_protection):
        """Test validating valid CSRF token."""
        session_id = "test_session_456"
        
        # Generate token
        token = csrf_protection.generate_token(session_id)
        
        # Validate same token
        assert csrf_protection.validate_token(session_id, token) is True
    
    def test_validate_csrf_token_invalid(self, csrf_protection):
        """Test validating invalid CSRF token."""
        session_id = "test_session_789"
        
        # Generate token for one session
        token = csrf_protection.generate_token(session_id)
        
        # Try to validate with different session
        assert csrf_protection.validate_token("different_session", token) is False
    
    def test_validate_csrf_token_tampered(self, csrf_protection):
        """Test validating tampered CSRF token."""
        session_id = "test_session_abc"
        
        # Generate token
        token = csrf_protection.generate_token(session_id)
        
        # Tamper with token
        tampered_token = token[:-5] + "xxxxx"
        
        # Should not validate
        assert csrf_protection.validate_token(session_id, tampered_token) is False
    
    @pytest.mark.asyncio
    async def test_csrf_check_safe_methods(self, csrf_protection):
        """Test CSRF check skips safe methods."""
        request = MagicMock()
        request.method = "GET"
        
        # Should return True for safe methods
        assert await csrf_protection.check_csrf(request) is True
        
        request.method = "HEAD"
        assert await csrf_protection.check_csrf(request) is True
        
        request.method = "OPTIONS"
        assert await csrf_protection.check_csrf(request) is True


class TestSecurityHeaders:
    """Test security headers."""
    
    def test_default_security_headers(self):
        """Test default security headers."""
        headers = SecurityHeaders()
        response = Response()
        
        headers.apply_headers(response)
        
        # Check all security headers are applied
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert response.headers["Permissions-Policy"] == "geolocation=(), microphone=(), camera=()"
    
    def test_custom_csp_header(self):
        """Test custom Content-Security-Policy."""
        custom_csp = "default-src 'self' https://trusted.com"
        headers = SecurityHeaders(csp=custom_csp)
        response = Response()
        
        headers.apply_headers(response)
        
        assert response.headers["Content-Security-Policy"] == custom_csp
    
    def test_remove_server_header(self):
        """Test server header removal."""
        headers = SecurityHeaders()
        response = Response()
        response.headers["Server"] = "FastAPI/0.100.0"
        
        headers.apply_headers(response)
        
        # Server header should be removed
        assert "Server" not in response.headers
    
    def test_cors_headers(self):
        """Test CORS headers when enabled."""
        headers = SecurityHeaders(cors_enabled=True, cors_origins=["https://app.example.com"])
        response = Response()
        
        headers.apply_headers(response)
        
        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Credentials"] == "true"