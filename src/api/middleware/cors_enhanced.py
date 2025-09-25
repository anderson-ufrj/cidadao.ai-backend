"""
Module: api.middleware.cors_enhanced
Description: Enhanced CORS middleware for Vercel frontend integration
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import re
from typing import List, Optional, Set
from urllib.parse import urlparse

from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, PlainTextResponse
from starlette.types import ASGIApp

from src.core import get_logger
from src.core.config import settings

logger = get_logger(__name__)


class EnhancedCORSMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS middleware with dynamic origin validation.
    
    Features:
    - Wildcard subdomain support
    - Vercel preview deployment support
    - Development/production mode awareness
    - Custom header handling
    - Preflight optimization
    """
    
    def __init__(
        self,
        app,
        allowed_origins: Optional[List[str]] = None,
        allowed_origin_patterns: Optional[List[str]] = None,
        allow_credentials: bool = True,
        allowed_methods: Optional[List[str]] = None,
        allowed_headers: Optional[List[str]] = None,
        exposed_headers: Optional[List[str]] = None,
        max_age: int = 3600
    ):
        """Initialize enhanced CORS middleware."""
        super().__init__(app)
        
        # Use settings if not provided
        self.allowed_origins = set(allowed_origins or settings.cors_origins)
        self.allowed_origin_patterns = allowed_origin_patterns or []
        self.allow_credentials = allow_credentials
        self.allowed_methods = allowed_methods or settings.cors_allow_methods
        self.allowed_headers = allowed_headers or settings.cors_allow_headers
        self.exposed_headers = exposed_headers or [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining", 
            "X-RateLimit-Reset",
            "X-Request-ID",
            "X-Correlation-ID"
        ]
        self.max_age = max_age
        
        # Compile regex patterns
        self.origin_patterns = []
        for pattern in self.allowed_origin_patterns:
            try:
                self.origin_patterns.append(re.compile(pattern))
            except re.error as e:
                logger.error(f"Invalid CORS pattern: {pattern} - {e}")
        
        # Add default Vercel patterns
        self._add_vercel_patterns()
        
        logger.info(
            "enhanced_cors_initialized",
            allowed_origins=list(self.allowed_origins),
            pattern_count=len(self.origin_patterns),
            allow_credentials=self.allow_credentials
        )
    
    def _add_vercel_patterns(self):
        """Add Vercel-specific patterns."""
        # Vercel preview deployments
        vercel_patterns = [
            r"^https://cidadao-ai-frontend-[a-zA-Z0-9]+-neural-thinker\.vercel\.app$",
            r"^https://cidadao-ai-[a-zA-Z0-9]+-neural-thinker\.vercel\.app$",
            r"^https://[a-zA-Z0-9-]+\.neural-thinker\.vercel\.app$"
        ]
        
        for pattern in vercel_patterns:
            try:
                self.origin_patterns.append(re.compile(pattern))
            except re.error:
                pass
    
    async def dispatch(self, request: Request, call_next):
        """Process request with enhanced CORS handling."""
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = await self._handle_preflight(request, origin)
            if response:
                return response
        
        # Process regular request
        response = await call_next(request)
        
        # Add CORS headers if origin is allowed
        if origin and self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = str(self.allow_credentials).lower()
            
            # Add exposed headers
            if self.exposed_headers:
                response.headers["Access-Control-Expose-Headers"] = ", ".join(self.exposed_headers)
            
            # Add Vary header for caching
            vary_headers = response.headers.get("Vary", "").split(", ")
            if "Origin" not in vary_headers:
                vary_headers.append("Origin")
            response.headers["Vary"] = ", ".join(filter(None, vary_headers))
        
        return response
    
    async def _handle_preflight(self, request: Request, origin: Optional[str]) -> Optional[Response]:
        """Handle preflight OPTIONS requests."""
        if not origin or not self._is_origin_allowed(origin):
            return None
        
        # Get requested method and headers
        requested_method = request.headers.get("Access-Control-Request-Method")
        requested_headers = request.headers.get("Access-Control-Request-Headers", "").split(", ")
        
        # Validate method
        if requested_method and requested_method not in self.allowed_methods:
            logger.warning(
                "cors_preflight_method_denied",
                origin=origin,
                method=requested_method
            )
            return PlainTextResponse(
                "Method not allowed",
                status_code=403
            )
        
        # Build response
        response = PlainTextResponse("OK", status_code=200)
        
        # Set CORS headers
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self._get_allowed_headers(requested_headers))
        response.headers["Access-Control-Allow-Credentials"] = str(self.allow_credentials).lower()
        response.headers["Access-Control-Max-Age"] = str(self.max_age)
        
        return response
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed."""
        # Exact match
        if origin in self.allowed_origins:
            return True
        
        # Wildcard check (for backwards compatibility)
        for allowed in self.allowed_origins:
            if allowed == "*":
                return True
            if allowed.startswith("https://*.") or allowed.startswith("http://*."):
                # Simple wildcard subdomain check
                base_domain = allowed.replace("https://*.", "").replace("http://*.", "")
                parsed = urlparse(origin)
                if parsed.hostname and parsed.hostname.endswith(base_domain):
                    return True
        
        # Regex pattern match
        for pattern in self.origin_patterns:
            if pattern.match(origin):
                return True
        
        # Development mode - allow localhost
        if settings.is_development:
            parsed = urlparse(origin)
            if parsed.hostname in ["localhost", "127.0.0.1", "::1"]:
                return True
        
        logger.debug(
            "cors_origin_denied",
            origin=origin,
            allowed_count=len(self.allowed_origins)
        )
        
        return False
    
    def _get_allowed_headers(self, requested_headers: List[str]) -> List[str]:
        """Get allowed headers for response."""
        if "*" in self.allowed_headers:
            # Allow all requested headers
            return requested_headers
        
        # Filter to allowed headers
        allowed = set(h.lower() for h in self.allowed_headers)
        return [h for h in requested_headers if h.lower() in allowed]


def setup_cors(app: ASGIApp) -> None:
    """
    Setup CORS for the application with enhanced configuration.
    
    This replaces the default CORSMiddleware with our enhanced version.
    """
    # Remove existing CORS middleware if present
    middlewares = []
    for middleware in app.middleware:
        if not isinstance(middleware, CORSMiddleware):
            middlewares.append(middleware)
    app.middleware = middlewares
    
    # Add enhanced CORS middleware
    app.add_middleware(
        EnhancedCORSMiddleware,
        allowed_origins=settings.cors_origins,
        allowed_origin_patterns=[
            # Vercel preview deployments
            r"^https://cidadao-ai-frontend-[a-zA-Z0-9]+-.*\.vercel\.app$",
            r"^https://cidadao-ai-[a-zA-Z0-9]+-.*\.vercel\.app$",
            # GitHub Codespaces
            r"^https://.*\.github\.dev$",
            r"^https://.*\.gitpod\.io$",
            # Local development with custom ports
            r"^http://localhost:[0-9]+$",
            r"^http://127\.0\.0\.1:[0-9]+$"
        ],
        allow_credentials=settings.cors_allow_credentials,
        allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
        allowed_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language", 
            "Content-Type",
            "Authorization",
            "X-API-Key",
            "X-Request-ID",
            "X-Correlation-ID",
            "X-CSRF-Token",
            "X-Requested-With",
            "Cache-Control",
            "If-Match",
            "If-None-Match",
            "If-Modified-Since",
            "If-Unmodified-Since"
        ],
        exposed_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-RateLimit-Window",
            "X-Request-ID",
            "X-Correlation-ID",
            "X-Total-Count",
            "Link",
            "ETag",
            "Last-Modified",
            "Cache-Control"
        ],
        max_age=86400  # 24 hours for production
    )