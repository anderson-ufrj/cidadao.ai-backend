"""
Module: api.middleware.security
Description: Advanced security middleware for comprehensive protection
Author: Anderson H. Silva
Date: 2025-01-15
License: Proprietary - All rights reserved
"""

import time
import re
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict, deque
import hashlib
import hmac
import secrets

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core import get_logger, settings
from src.core.audit import audit_logger, AuditEventType, AuditSeverity, AuditContext


class SecurityConfig:
    """Security middleware configuration."""
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE = 60
    RATE_LIMIT_REQUESTS_PER_HOUR = 1000
    RATE_LIMIT_BURST_SIZE = 10
    
    # IP blocking
    MAX_FAILED_ATTEMPTS = 5
    BLOCK_DURATION_MINUTES = 30
    SUSPICIOUS_ACTIVITY_THRESHOLD = 20
    
    # Request validation
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_HEADER_SIZE = 8192  # 8KB
    MAX_URL_LENGTH = 2048
    
    # Content security
    ALLOWED_CONTENT_TYPES = {
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data",
        "text/plain"
    }
    
    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()"
    }
    
    # Suspicious patterns
    SUSPICIOUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # XSS
        r"javascript:",  # XSS
        r"on\w+\s*=",  # Event handlers
        r"union\s+select",  # SQL injection
        r"drop\s+table",  # SQL injection
        r"insert\s+into",  # SQL injection
        r"delete\s+from",  # SQL injection
        r"update\s+\w+\s+set",  # SQL injection
        r"exec\s*\(",  # Command injection
        r"system\s*\(",  # Command injection
        r"eval\s*\(",  # Code injection
        r"../",  # Path traversal
        r"\.\.\\",  # Path traversal (Windows)
        r"file://",  # Local file inclusion
        r"ftp://",  # FTP access
    ]


class IPBlockList:
    """IP address blocking management."""
    
    def __init__(self):
        self.blocked_ips: Dict[str, datetime] = {}
        self.failed_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.whitelist: Set[str] = {
            "127.0.0.1", "::1",  # Localhost
            "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"  # Private networks
        }
    
    def is_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted."""
        try:
            ip_addr = ipaddress.ip_address(ip)
            for whitelist_entry in self.whitelist:
                if "/" in whitelist_entry:
                    if ip_addr in ipaddress.ip_network(whitelist_entry, strict=False):
                        return True
                elif ip == whitelist_entry:
                    return True
            return False
        except ValueError:
            return False
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked."""
        if self.is_whitelisted(ip):
            return False
        
        if ip in self.blocked_ips:
            if datetime.utcnow() - self.blocked_ips[ip] < timedelta(minutes=SecurityConfig.BLOCK_DURATION_MINUTES):
                return True
            else:
                # Unblock expired IPs
                del self.blocked_ips[ip]
        
        return False
    
    def record_failed_attempt(self, ip: str):
        """Record a failed attempt from IP."""
        if self.is_whitelisted(ip):
            return
        
        now = datetime.utcnow()
        
        # Clean old attempts (older than 1 hour)
        self.failed_attempts[ip] = [
            attempt for attempt in self.failed_attempts[ip]
            if now - attempt < timedelta(hours=1)
        ]
        
        # Add new attempt
        self.failed_attempts[ip].append(now)
        
        # Check if should block
        if len(self.failed_attempts[ip]) >= SecurityConfig.MAX_FAILED_ATTEMPTS:
            self.blocked_ips[ip] = now
    
    def get_failed_attempts_count(self, ip: str, window_minutes: int = 60) -> int:
        """Get number of failed attempts in time window."""
        if ip not in self.failed_attempts:
            return 0
        
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        return sum(1 for attempt in self.failed_attempts[ip] if attempt > cutoff)


class RateLimiter:
    """Advanced rate limiting with multiple windows."""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.burst_tokens: Dict[str, int] = defaultdict(lambda: SecurityConfig.RATE_LIMIT_BURST_SIZE)
        self.last_refill: Dict[str, datetime] = defaultdict(lambda: datetime.utcnow())
    
    def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, any]]:
        """Check if request is allowed for identifier."""
        now = datetime.utcnow()
        
        # Refill burst tokens (token bucket algorithm)
        time_since_refill = (now - self.last_refill[identifier]).total_seconds()
        tokens_to_add = int(time_since_refill * SecurityConfig.RATE_LIMIT_REQUESTS_PER_MINUTE / 60)
        
        if tokens_to_add > 0:
            self.burst_tokens[identifier] = min(
                SecurityConfig.RATE_LIMIT_BURST_SIZE,
                self.burst_tokens[identifier] + tokens_to_add
            )
            self.last_refill[identifier] = now
        
        # Check burst limit
        if self.burst_tokens[identifier] <= 0:
            return False, {"reason": "burst_limit_exceeded"}
        
        # Clean old requests
        cutoff_minute = now - timedelta(minutes=1)
        cutoff_hour = now - timedelta(hours=1)
        
        while self.requests[identifier] and self.requests[identifier][0] < cutoff_hour:
            self.requests[identifier].popleft()
        
        # Count requests in windows
        requests_last_minute = sum(1 for req_time in self.requests[identifier] if req_time > cutoff_minute)
        requests_last_hour = len(self.requests[identifier])
        
        # Check limits
        if requests_last_minute >= SecurityConfig.RATE_LIMIT_REQUESTS_PER_MINUTE:
            return False, {"reason": "minute_limit_exceeded", "requests_last_minute": requests_last_minute}
        
        if requests_last_hour >= SecurityConfig.RATE_LIMIT_REQUESTS_PER_HOUR:
            return False, {"reason": "hour_limit_exceeded", "requests_last_hour": requests_last_hour}
        
        # Allow request
        self.requests[identifier].append(now)
        self.burst_tokens[identifier] -= 1
        
        return True, {
            "requests_last_minute": requests_last_minute + 1,
            "requests_last_hour": requests_last_hour + 1,
            "burst_tokens": self.burst_tokens[identifier]
        }


class RequestValidator:
    """Request validation and security scanning."""
    
    def __init__(self):
        self.suspicious_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in SecurityConfig.SUSPICIOUS_PATTERNS]
    
    def validate_request_size(self, request: Request) -> bool:
        """Validate request size."""
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                return size <= SecurityConfig.MAX_REQUEST_SIZE
            except ValueError:
                return False
        return True
    
    def validate_headers(self, request: Request) -> Tuple[bool, Optional[str]]:
        """Validate request headers."""
        
        # Check header size
        headers_size = sum(len(k) + len(v) for k, v in request.headers.items())
        if headers_size > SecurityConfig.MAX_HEADER_SIZE:
            return False, "Headers too large"
        
        # Check for suspicious headers (skip user-agent and common headers)
        skip_headers = {
            "user-agent", "accept", "accept-language", "accept-encoding", 
            "referer", "origin", "x-direct-url", "x-forwarded-for", 
            "x-forwarded-proto", "x-forwarded-host", "x-real-ip",
            "host", "connection", "upgrade-insecure-requests"
        }
        for name, value in request.headers.items():
            if name.lower() in skip_headers:
                continue
            if any(pattern.search(value) for pattern in self.suspicious_patterns):
                return False, f"Suspicious content in header {name}"
        
        return True, None
    
    def validate_url(self, request: Request) -> Tuple[bool, Optional[str]]:
        """Validate request URL."""
        
        url = str(request.url)
        
        # Check URL length
        if len(url) > SecurityConfig.MAX_URL_LENGTH:
            return False, "URL too long"
        
        # Only check path and query for suspicious patterns, not the full URL
        path_and_query = request.url.path
        if request.url.query:
            path_and_query += "?" + request.url.query
            
        # Check for suspicious patterns in path and query only
        for pattern in self.suspicious_patterns:
            if pattern.search(path_and_query):
                return False, "Suspicious pattern in URL"
        
        # Check for double encoding
        if "%25" in path_and_query:
            return False, "Double URL encoding detected"
        
        return True, None
    
    def validate_content_type(self, request: Request) -> bool:
        """Validate content type."""
        content_type = request.headers.get("content-type", "").split(";")[0].strip()
        
        if not content_type:
            return True  # Allow requests without content-type
        
        return content_type.lower() in SecurityConfig.ALLOWED_CONTENT_TYPES
    
    async def scan_request_body(self, body: bytes) -> Tuple[bool, Optional[str]]:
        """Scan request body for suspicious content."""
        if not body:
            return True, None
        
        try:
            body_text = body.decode("utf-8", errors="ignore")
            
            for pattern in self.suspicious_patterns:
                if pattern.search(body_text):
                    return False, "Suspicious pattern in request body"
            
            return True, None
            
        except Exception:
            return False, "Invalid request body encoding"


class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger(__name__)
        self.ip_blocklist = IPBlockList()
        self.rate_limiter = RateLimiter()
        self.request_validator = RequestValidator()
    
    async def dispatch(self, request: Request, call_next):
        """Process request through security checks."""
        
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        
        # Create audit context
        audit_context = AuditContext(
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            host=request.headers.get("host"),
            referer=request.headers.get("referer")
        )
        
        try:
            # 1. IP blocking check
            if self.ip_blocklist.is_blocked(client_ip):
                await self._log_security_event(
                    "IP address blocked",
                    AuditEventType.UNAUTHORIZED_ACCESS,
                    AuditSeverity.HIGH,
                    {"ip": client_ip, "reason": "blocked_ip"},
                    audit_context
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Access denied"}
                )
            
            # 2. Rate limiting
            allowed, rate_info = self.rate_limiter.is_allowed(client_ip)
            if not allowed:
                self.ip_blocklist.record_failed_attempt(client_ip)
                await self._log_security_event(
                    "Rate limit exceeded",
                    AuditEventType.RATE_LIMIT_EXCEEDED,
                    AuditSeverity.MEDIUM,
                    {"ip": client_ip, **rate_info},
                    audit_context
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded"},
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": str(SecurityConfig.RATE_LIMIT_REQUESTS_PER_MINUTE),
                        "X-RateLimit-Remaining": "0"
                    }
                )
            
            # 3. Request validation
            validation_result = await self._validate_request(request, audit_context)
            if validation_result:
                return validation_result
            
            # 4. Process request
            response = await call_next(request)
            
            # 5. Add security headers
            self._add_security_headers(response)
            
            # 6. Log successful request
            processing_time = time.time() - start_time
            
            if processing_time > 5.0:  # Log slow requests
                await self._log_security_event(
                    "Slow request detected",
                    AuditEventType.SUSPICIOUS_ACTIVITY,
                    AuditSeverity.LOW,
                    {
                        "ip": client_ip,
                        "path": request.url.path,
                        "method": request.method,
                        "processing_time": processing_time
                    },
                    audit_context
                )
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(SecurityConfig.RATE_LIMIT_REQUESTS_PER_MINUTE)
            response.headers["X-RateLimit-Remaining"] = str(rate_info.get("burst_tokens", 0))
            
            return response
            
        except Exception as e:
            # Log security middleware errors
            await self._log_security_event(
                f"Security middleware error: {str(e)}",
                AuditEventType.SYSTEM_STARTUP,  # Using system event for internal errors
                AuditSeverity.HIGH,
                {"ip": client_ip, "error": str(e)},
                audit_context
            )
            
            # Continue with request (fail open for availability)
            response = await call_next(request)
            self._add_security_headers(response)
            return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address considering proxies."""
        
        # Check X-Forwarded-For header (reverse proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP (original client)
            ip = forwarded_for.split(",")[0].strip()
            try:
                ipaddress.ip_address(ip)
                return ip
            except ValueError:
                pass
        
        # Check X-Real-IP header (nginx)
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            try:
                ipaddress.ip_address(real_ip)
                return real_ip
            except ValueError:
                pass
        
        # Fall back to client address
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    async def _validate_request(self, request: Request, audit_context: AuditContext) -> Optional[JSONResponse]:
        """Validate request and return error response if invalid."""
        
        # Validate request size
        if not self.request_validator.validate_request_size(request):
            await self._log_security_event(
                "Request size too large",
                AuditEventType.SUSPICIOUS_ACTIVITY,
                AuditSeverity.MEDIUM,
                {"ip": audit_context.ip_address, "path": request.url.path},
                audit_context
            )
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request too large"}
            )
        
        # Validate headers
        headers_valid, header_error = self.request_validator.validate_headers(request)
        if not headers_valid:
            await self._log_security_event(
                f"Invalid headers: {header_error}",
                AuditEventType.SUSPICIOUS_ACTIVITY,
                AuditSeverity.MEDIUM,
                {"ip": audit_context.ip_address, "error": header_error},
                audit_context
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid request headers"}
            )
        
        # Validate URL
        url_valid, url_error = self.request_validator.validate_url(request)
        if not url_valid:
            await self._log_security_event(
                f"Invalid URL: {url_error}",
                AuditEventType.SUSPICIOUS_ACTIVITY,
                AuditSeverity.HIGH,
                {"ip": audit_context.ip_address, "url": str(request.url), "error": url_error},
                audit_context
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid request URL"}
            )
        
        # Validate content type
        if not self.request_validator.validate_content_type(request):
            await self._log_security_event(
                "Unsupported content type",
                AuditEventType.SUSPICIOUS_ACTIVITY,
                AuditSeverity.MEDIUM,
                {
                    "ip": audit_context.ip_address,
                    "content_type": request.headers.get("content-type")
                },
                audit_context
            )
            return JSONResponse(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                content={"detail": "Unsupported content type"}
            )
        
        # Validate request body for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                body_valid, body_error = await self.request_validator.scan_request_body(body)
                
                if not body_valid:
                    await self._log_security_event(
                        f"Suspicious request body: {body_error}",
                        AuditEventType.SUSPICIOUS_ACTIVITY,
                        AuditSeverity.HIGH,
                        {"ip": audit_context.ip_address, "error": body_error},
                        audit_context
                    )
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"detail": "Invalid request content"}
                    )
                    
            except Exception as e:
                await self._log_security_event(
                    f"Request body validation error: {str(e)}",
                    AuditEventType.SUSPICIOUS_ACTIVITY,
                    AuditSeverity.MEDIUM,
                    {"ip": audit_context.ip_address, "error": str(e)},
                    audit_context
                )
        
        return None
    
    def _add_security_headers(self, response):
        """Add security headers to response."""
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Add CSP header
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.portaldatransparencia.gov.br; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
    
    async def _log_security_event(
        self,
        message: str,
        event_type: AuditEventType,
        severity: AuditSeverity,
        details: Dict,
        context: AuditContext
    ):
        """Log security event to audit system."""
        
        await audit_logger.log_event(
            event_type=event_type,
            message=message,
            severity=severity,
            details=details,
            context=context,
            success=False
        )


class CSRFProtection:
    """CSRF protection middleware."""
    
    def __init__(self):
        self.secret_key = settings.secret_key.get_secret_value()
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token for session."""
        timestamp = str(int(time.time()))
        message = f"{session_id}:{timestamp}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{timestamp}:{signature}"
    
    def validate_token(self, token: str, session_id: str, max_age: int = 3600) -> bool:
        """Validate CSRF token."""
        try:
            timestamp_str, signature = token.split(":", 1)
            timestamp = int(timestamp_str)
            
            # Check token age
            if time.time() - timestamp > max_age:
                return False
            
            # Verify signature
            message = f"{session_id}:{timestamp_str}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except (ValueError, IndexError):
            return False


# Global instances
csrf_protection = CSRFProtection()