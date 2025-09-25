"""
Module: api.middleware.query_tracking
Description: Middleware to track query patterns for cache warming
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from typing import Dict, Any
import json
import hashlib

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core import get_logger
from src.services.cache_warming_service import cache_warming_service

logger = get_logger(__name__)


class QueryTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track query patterns for cache optimization.
    
    Tracks:
    - API endpoint access frequency
    - Query parameters
    - Response times
    - Cache hit/miss patterns
    """
    
    def __init__(
        self,
        app,
        tracked_paths: list = None,
        sample_rate: float = 1.0
    ):
        """
        Initialize query tracking middleware.
        
        Args:
            app: FastAPI application
            tracked_paths: List of paths to track (None = all)
            sample_rate: Sampling rate (0.0 to 1.0)
        """
        super().__init__(app)
        self.tracked_paths = tracked_paths or [
            "/api/v1/investigations",
            "/api/v1/contracts",
            "/api/v1/analysis",
            "/api/v1/reports",
            "/api/v1/chat"
        ]
        self.sample_rate = sample_rate
        
    async def dispatch(self, request: Request, call_next):
        """Process request with query tracking."""
        # Check if we should track this request
        if not self._should_track(request):
            return await call_next(request)
        
        # Extract query information
        query_info = self._extract_query_info(request)
        
        # Process request
        response = await call_next(request)
        
        # Track query in background
        try:
            cache_warming_service.track_query(query_info)
        except Exception as e:
            logger.error(
                "query_tracking_error",
                error=str(e),
                query_info=query_info
            )
        
        return response
    
    def _should_track(self, request: Request) -> bool:
        """Check if request should be tracked."""
        # Check sampling rate
        import random
        if random.random() > self.sample_rate:
            return False
        
        # Check path
        path = request.url.path
        for tracked_path in self.tracked_paths:
            if path.startswith(tracked_path):
                return True
        
        return False
    
    def _extract_query_info(self, request: Request) -> Dict[str, Any]:
        """Extract query information from request."""
        query_info = {
            "path": request.url.path,
            "method": request.method,
            "query_params": dict(request.query_params),
            "timestamp": None  # Will be set by service
        }
        
        # Add path parameters if available
        if hasattr(request, "path_params"):
            query_info["path_params"] = request.path_params
        
        # Generate query hash for deduplication
        query_str = json.dumps(query_info, sort_keys=True)
        query_info["hash"] = hashlib.md5(query_str.encode()).hexdigest()
        
        return query_info