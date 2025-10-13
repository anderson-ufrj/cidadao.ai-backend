"""Rate limiting middleware with distributed Redis backend"""

import time

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core import get_logger
from src.services.rate_limit_service import get_rate_limiter

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using distributed Redis backend"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.rate_limiter = get_rate_limiter()

    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting to requests"""

        # Get client identifier (IP address)
        client_ip = self._get_client_ip(request)

        # Skip rate limiting for health checks and metrics
        if request.url.path in [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]:
            return await call_next(request)

        # Check rate limit
        allowed, rate_info = await self.rate_limiter.is_allowed(
            identifier=client_ip, endpoint=request.url.path
        )

        if not allowed:
            # Log rate limit violation
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {request.url.path}",
                extra={
                    "client_ip": client_ip,
                    "endpoint": request.url.path,
                    "rate_info": rate_info,
                },
            )

            # Return 429 response
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "error": rate_info.get("reason", "rate_limit_exceeded"),
                    "retry_after": rate_info.get("reset_in", 60),
                },
                headers={
                    "Retry-After": str(rate_info.get("reset_in", 60)),
                    "X-RateLimit-Limit": str(rate_info.get("limit", 60)),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(
                        int(time.time() + rate_info.get("reset_in", 60))
                    ),
                },
            )

        # Process request and add rate limit headers
        response = await call_next(request)

        # Add rate limit headers to response
        if "limits" in rate_info:
            response.headers["X-RateLimit-Limit-Minute"] = str(
                rate_info["limits"]["per_minute"]
            )
            response.headers["X-RateLimit-Limit-Hour"] = str(
                rate_info["limits"]["per_hour"]
            )
            response.headers["X-RateLimit-Limit-Day"] = str(
                rate_info["limits"]["per_day"]
            )

        if "minute_count" in rate_info:
            response.headers["X-RateLimit-Used-Minute"] = str(rate_info["minute_count"])
            response.headers["X-RateLimit-Remaining-Minute"] = str(
                rate_info["limits"]["per_minute"] - rate_info["minute_count"]
            )

        if "burst_remaining" in rate_info:
            response.headers["X-RateLimit-Burst-Remaining"] = str(
                rate_info["burst_remaining"]
            )

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address considering proxies"""

        # Check X-Forwarded-For header (reverse proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP (original client)
            ip = forwarded_for.split(",")[0].strip()
            return ip

        # Check X-Real-IP header (nginx)
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to client address
        if request.client and request.client.host:
            return request.client.host

        return "unknown"
