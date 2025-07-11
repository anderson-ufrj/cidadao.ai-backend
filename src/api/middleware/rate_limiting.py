"""
Module: api.middleware.rate_limiting
Description: Rate limiting middleware for API endpoints
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import time
from typing import Dict, Tuple
from collections import defaultdict

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from src.core import get_logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""
    
    def __init__(
        self,
        app,
        calls: int = 60,
        period: int = 60,
        per_minute: int = 60,
        per_hour: int = 1000,
        per_day: int = 10000,
    ):
        """
        Initialize rate limiting middleware.
        
        Args:
            app: FastAPI application
            calls: Number of calls allowed per period
            period: Time period in seconds
            per_minute: Calls per minute
            per_hour: Calls per hour  
            per_day: Calls per day
        """
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.per_minute = per_minute
        self.per_hour = per_hour
        self.per_day = per_day
        
        # Storage for rate limit data
        self.clients: Dict[str, Dict[str, list]] = defaultdict(lambda: {
            "minute": [],
            "hour": [],
            "day": []
        })
        
        self.logger = get_logger(__name__)
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Check rate limits
        if not self._check_rate_limits(client_ip, current_time):
            self.logger.warning(
                "rate_limit_exceeded",
                client_ip=client_ip,
                path=request.url.path,
                method=request.method,
            )
            
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Too many requests.",
                headers={"Retry-After": "60"}
            )
        
        # Record the request
        self._record_request(client_ip, current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        limits = self._get_remaining_limits(client_ip, current_time)
        response.headers["X-RateLimit-Limit-Minute"] = str(self.per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.per_hour)
        response.headers["X-RateLimit-Limit-Day"] = str(self.per_day)
        response.headers["X-RateLimit-Remaining-Minute"] = str(limits["minute"])
        response.headers["X-RateLimit-Remaining-Hour"] = str(limits["hour"])
        response.headers["X-RateLimit-Remaining-Day"] = str(limits["day"])
        response.headers["X-RateLimit-Reset"] = str(int(current_time) + 60)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limits(self, client_ip: str, current_time: float) -> bool:
        """Check if client is within rate limits."""
        client_data = self.clients[client_ip]
        
        # Clean old requests
        self._clean_old_requests(client_data, current_time)
        
        # Check each time window
        if len(client_data["minute"]) >= self.per_minute:
            return False
        
        if len(client_data["hour"]) >= self.per_hour:
            return False
        
        if len(client_data["day"]) >= self.per_day:
            return False
        
        return True
    
    def _record_request(self, client_ip: str, current_time: float):
        """Record a request for rate limiting."""
        client_data = self.clients[client_ip]
        
        client_data["minute"].append(current_time)
        client_data["hour"].append(current_time)
        client_data["day"].append(current_time)
    
    def _clean_old_requests(self, client_data: Dict[str, list], current_time: float):
        """Remove old requests outside the time windows."""
        # Clean minute window
        client_data["minute"] = [
            t for t in client_data["minute"]
            if current_time - t < 60
        ]
        
        # Clean hour window
        client_data["hour"] = [
            t for t in client_data["hour"]
            if current_time - t < 3600
        ]
        
        # Clean day window
        client_data["day"] = [
            t for t in client_data["day"]
            if current_time - t < 86400
        ]
    
    def _get_remaining_limits(self, client_ip: str, current_time: float) -> Dict[str, int]:
        """Get remaining requests for each time window."""
        client_data = self.clients[client_ip]
        self._clean_old_requests(client_data, current_time)
        
        return {
            "minute": max(0, self.per_minute - len(client_data["minute"])),
            "hour": max(0, self.per_hour - len(client_data["hour"])),
            "day": max(0, self.per_day - len(client_data["day"])),
        }