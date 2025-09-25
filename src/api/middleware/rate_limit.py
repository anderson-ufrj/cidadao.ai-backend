"""
Module: api.middleware.rate_limit
Description: Rate limiting middleware for API endpoints
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.core import get_logger
from src.infrastructure.rate_limiter import (
    rate_limiter,
    RateLimitTier,
    RateLimitStrategy
)
from src.models.api_key import APIKey

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    
    Supports multiple identification methods:
    - API Key (preferred)
    - User ID (authenticated users)
    - IP Address (fallback)
    """
    
    def __init__(
        self,
        app,
        default_tier: RateLimitTier = RateLimitTier.FREE,
        strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    ):
        """Initialize rate limit middleware."""
        super().__init__(app)
        self.default_tier = default_tier
        self.rate_limiter = rate_limiter
        self.rate_limiter.strategy = strategy
        
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for certain paths
        if self._should_skip(request.url.path):
            return await call_next(request)
        
        # Get rate limit key and tier
        key, tier, custom_limits = self._get_rate_limit_info(request)
        
        if not key:
            # No identifier available, skip rate limiting
            logger.warning(
                "rate_limit_no_identifier",
                path=request.url.path,
                method=request.method
            )
            return await call_next(request)
        
        # Check rate limit
        try:
            allowed, results = await self.rate_limiter.check_rate_limit(
                key=key,
                endpoint=request.url.path,
                tier=tier,
                custom_limits=custom_limits
            )
            
            if not allowed:
                # Rate limit exceeded
                headers = self.rate_limiter.get_headers(results)
                
                # Find which limit was exceeded
                exceeded_window = None
                for window, data in results.items():
                    if not data.get("allowed", True):
                        exceeded_window = window
                        break
                
                logger.warning(
                    "rate_limit_exceeded",
                    key=key,
                    endpoint=request.url.path,
                    window=exceeded_window,
                    tier=tier
                )
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": f"Rate limit exceeded for {exceeded_window}",
                        "error": "RATE_LIMIT_EXCEEDED",
                        "limits": results
                    },
                    headers=headers
                )
            
            # Add rate limit headers to response
            response = await call_next(request)
            
            # Add headers
            headers = self.rate_limiter.get_headers(results)
            for header, value in headers.items():
                response.headers[header] = value
            
            # Log high usage
            for window, data in results.items():
                if data["remaining"] < data["limit"] * 0.1:  # Less than 10% remaining
                    logger.info(
                        "rate_limit_warning",
                        key=key,
                        endpoint=request.url.path,
                        window=window,
                        remaining=data["remaining"],
                        limit=data["limit"]
                    )
            
            return response
            
        except Exception as e:
            logger.error(
                "rate_limit_error",
                error=str(e),
                exc_info=True
            )
            # On error, allow request to proceed
            return await call_next(request)
    
    def _should_skip(self, path: str) -> bool:
        """Check if path should skip rate limiting."""
        skip_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/favicon.ico",
            "/_next",  # Next.js assets
            "/static",
        ]
        
        for skip_path in skip_paths:
            if path.startswith(skip_path):
                return True
        
        return False
    
    def _get_rate_limit_info(
        self,
        request: Request
    ) -> tuple[Optional[str], RateLimitTier, Optional[Dict[str, int]]]:
        """
        Get rate limit key, tier, and custom limits from request.
        
        Returns:
            Tuple of (key, tier, custom_limits)
        """
        # Priority 1: API Key
        api_key = getattr(request.state, "api_key", None)
        if api_key and isinstance(api_key, APIKey):
            key = f"api_key:{api_key.id}"
            tier = RateLimitTier(api_key.tier)
            
            # Get custom limits if set
            custom_limits = {}
            if api_key.rate_limit_per_minute:
                custom_limits["per_minute"] = api_key.rate_limit_per_minute
            if api_key.rate_limit_per_hour:
                custom_limits["per_hour"] = api_key.rate_limit_per_hour
            if api_key.rate_limit_per_day:
                custom_limits["per_day"] = api_key.rate_limit_per_day
            
            return key, tier, custom_limits if custom_limits else None
        
        # Priority 2: Authenticated User
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            key = f"user:{user_id}"
            
            # Check user role for tier
            user = getattr(request.state, "user", {})
            role = user.get("role", "").lower()
            
            if role == "admin" or user.get("is_superuser"):
                tier = RateLimitTier.UNLIMITED
            elif role == "pro":
                tier = RateLimitTier.PRO
            elif role == "basic":
                tier = RateLimitTier.BASIC
            else:
                tier = RateLimitTier.FREE
            
            return key, tier, None
        
        # Priority 3: IP Address
        client_ip = None
        if request.client:
            client_ip = request.client.host
        
        # Check for proxy headers
        if not client_ip:
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()
        
        if not client_ip:
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                client_ip = real_ip
        
        if client_ip:
            key = f"ip:{client_ip}"
            return key, self.default_tier, None
        
        return None, self.default_tier, None


def get_rate_limit_decorator(
    tier: Optional[RateLimitTier] = None,
    custom_limits: Optional[Dict[str, int]] = None
):
    """
    Decorator for endpoint-specific rate limiting.
    
    Usage:
        @router.get("/expensive")
        @rate_limit(tier=RateLimitTier.PRO, custom_limits={"per_minute": 5})
        async def expensive_endpoint():
            ...
    """
    def decorator(func):
        # Store rate limit info on function
        func._rate_limit_tier = tier
        func._rate_limit_custom = custom_limits
        return func
    
    return decorator


# Convenience decorator
rate_limit = get_rate_limit_decorator