"""
Gzip compression middleware for API responses.

This middleware compresses responses to reduce bandwidth usage,
especially important for mobile applications.
"""

import gzip
from typing import Callable, Optional
from io import BytesIO

from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.core import get_logger

logger = get_logger(__name__)


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to compress responses using gzip.
    
    Features:
    - Automatic compression for responses > 1KB
    - Respects Accept-Encoding header
    - Excludes already compressed content
    - Configurable compression level
    """
    
    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 1024,
        compression_level: int = 6
    ):
        """
        Initialize compression middleware.
        
        Args:
            app: ASGI application
            minimum_size: Minimum response size to compress (bytes)
            compression_level: Gzip compression level (1-9)
        """
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compression_level = compression_level
        
        # Content types to compress
        self.compressible_types = {
            "application/json",
            "text/html",
            "text/plain",
            "text/css",
            "text/javascript",
            "application/javascript",
            "application/xml",
            "text/xml",
        }
        
        # Content types to never compress
        self.excluded_types = {
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "video/mp4",
            "application/pdf",
            "application/zip",
            "application/gzip",
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and potentially compress response."""
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return await call_next(request)
        
        # Process request
        response = await call_next(request)
        
        # Check if we should compress
        if not self._should_compress(response):
            return response
        
        # Get response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
        # Check size threshold
        if len(body) < self.minimum_size:
            # Return original response
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # Compress body
        compressed_body = gzip.compress(body, compresslevel=self.compression_level)
        
        # Calculate compression ratio
        compression_ratio = (1 - len(compressed_body) / len(body)) * 100
        logger.debug(
            f"Compressed response: {len(body)} → {len(compressed_body)} bytes "
            f"({compression_ratio:.1f}% reduction)"
        )
        
        # Update headers
        headers = dict(response.headers)
        headers["content-encoding"] = "gzip"
        headers["content-length"] = str(len(compressed_body))
        headers["x-uncompressed-size"] = str(len(body))
        headers["x-compression-ratio"] = f"{compression_ratio:.1f}%"
        
        # Remove content-length if streaming
        if "transfer-encoding" in headers:
            headers.pop("content-length", None)
        
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )
    
    def _should_compress(self, response: Response) -> bool:
        """Determine if response should be compressed."""
        # Check if already compressed
        if response.headers.get("content-encoding"):
            return False
        
        # Check content type
        content_type = response.media_type or ""
        base_type = content_type.split(";")[0].strip().lower()
        
        # Skip if excluded type
        if base_type in self.excluded_types:
            return False
        
        # Compress if compressible type
        if base_type in self.compressible_types:
            return True
        
        # Compress text/* by default
        if base_type.startswith("text/"):
            return True
        
        # Skip everything else
        return False


class StreamingCompressionMiddleware:
    """
    Middleware for compressing streaming responses (like SSE).
    """
    
    def __init__(self, app: ASGIApp, compression_level: int = 6):
        self.app = app
        self.compression_level = compression_level
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check for gzip support
        headers = dict(scope.get("headers", []))
        accept_encoding = headers.get(b"accept-encoding", b"").decode()
        
        if "gzip" not in accept_encoding.lower():
            await self.app(scope, receive, send)
            return
        
        # Intercept send to compress streaming responses
        async def compressed_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                # Check if this is a streaming response
                headers = dict(message.get("headers", []))
                content_type = headers.get(b"content-type", b"").decode()
                
                if "text/event-stream" in content_type:
                    # Add compression header
                    new_headers = []
                    for name, value in message.get("headers", []):
                        if name.lower() != b"content-length":
                            new_headers.append((name, value))
                    
                    new_headers.append((b"content-encoding", b"gzip"))
                    message["headers"] = new_headers
            
            await send(message)
        
        await self.app(scope, receive, compressed_send)


def add_compression_middleware(app, minimum_size: int = 1024, level: int = 6):
    """
    Add compression middleware to FastAPI app.
    
    Args:
        app: FastAPI application
        minimum_size: Minimum size to compress (bytes)
        level: Compression level (1-9)
    """
    app.add_middleware(
        CompressionMiddleware,
        minimum_size=minimum_size,
        compression_level=level
    )
    
    logger.info(
        f"Compression middleware enabled "
        f"(min_size={minimum_size}, level={level})"
    )