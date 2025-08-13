"""
Module: api.middleware.logging_middleware
Description: Logging middleware for API request/response tracking
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core import get_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging API requests and responses."""
    
    def __init__(self, app):
        """Initialize logging middleware."""
        super().__init__(app)
        self.logger = get_logger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with comprehensive logging."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Extract request information
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "Unknown")
        content_length = request.headers.get("Content-Length", "0")
        
        # Log request start
        self.logger.info(
            "api_request_started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            query_params=dict(request.query_params),
            client_ip=client_ip,
            user_agent=user_agent,
            content_length=content_length,
        )
        
        # Store request ID in state for other middleware
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Log successful response
            self.logger.info(
                "api_request_completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time=process_time,
                response_size=response.headers.get("Content-Length", "unknown"),
                client_ip=client_ip,
            )
            
            # Add response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            return response
            
        except Exception as exc:
            # Calculate error response time
            process_time = time.time() - start_time
            
            # Log error
            self.logger.error(
                "api_request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error_type=type(exc).__name__,
                error_message=str(exc),
                process_time=process_time,
                client_ip=client_ip,
            )
            
            # Re-raise the exception
            raise exc
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first (for proxy/load balancer setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        return request.client.host if request.client else "unknown"
    
    def _should_log_body(self, request: Request) -> bool:
        """Determine if request body should be logged."""
        # Skip logging body for certain content types or large requests
        content_type = request.headers.get("Content-Type", "")
        content_length = int(request.headers.get("Content-Length", "0"))
        
        # Don't log binary content or large payloads
        if content_length > 10240:  # 10KB limit
            return False
        
        # Don't log file uploads or binary data
        if any(ct in content_type.lower() for ct in ["multipart/", "application/octet-stream", "image/", "video/", "audio/"]):
            return False
        
        return True
    
    def _sanitize_headers(self, headers: dict) -> dict:
        """Remove sensitive information from headers."""
        sensitive_headers = {
            "authorization", "x-api-key", "cookie", "set-cookie",
            "x-auth-token", "x-access-token", "x-csrf-token"
        }
        
        return {
            key: "***REDACTED***" if key.lower() in sensitive_headers else value
            for key, value in headers.items()
        }