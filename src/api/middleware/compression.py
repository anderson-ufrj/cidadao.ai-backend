"""
Advanced compression middleware for API responses with Gzip and Brotli support.

This middleware compresses responses to reduce bandwidth usage,
especially important for mobile applications and slow connections.
"""

import gzip
from collections.abc import Callable
from typing import Optional

from fastapi import Request, Response
from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.core import get_logger
from src.services.compression_service import compression_service

try:
    import brotli

    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False
    brotli = None

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
        gzip_level: int = 6,
        brotli_quality: int = 4,
        brotli_mode: str = "text",
        exclude_paths: Optional[set] = None,
    ):
        """
        Initialize compression middleware.

        Args:
            app: ASGI application
            minimum_size: Minimum response size to compress (bytes)
            gzip_level: Gzip compression level (1-9)
            brotli_quality: Brotli quality level (0-11)
            brotli_mode: Brotli mode - "text", "font", or "generic"
            exclude_paths: Set of paths to exclude from compression
        """
        super().__init__(app)
        self.minimum_size = minimum_size
        self.gzip_level = gzip_level
        self.brotli_quality = brotli_quality
        self.brotli_mode = brotli_mode
        self.exclude_paths = exclude_paths or {"/metrics", "/health", "/health/metrics"}

        # Brotli mode mapping
        if HAS_BROTLI:
            self.brotli_modes = {
                "text": brotli.MODE_TEXT,
                "font": brotli.MODE_FONT,
                "generic": brotli.MODE_GENERIC,
            }

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
        # Skip compression for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Check client's accepted encodings
        accept_encoding = request.headers.get("accept-encoding", "").lower()
        accepts_br = HAS_BROTLI and "br" in accept_encoding
        accepts_gzip = "gzip" in accept_encoding

        if not (accepts_br or accepts_gzip):
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

        # Use compression service for optimal compression
        compressed_body, encoding, metrics = compression_service.compress(
            data=body,
            content_type=response.media_type or "application/octet-stream",
            accept_encoding=accept_encoding,
        )

        # If no compression applied, return original
        if encoding == "identity":
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Log compression metrics
        if metrics.get("ratio"):
            logger.debug(
                f"Compressed response with {encoding}: {metrics['original_size']} → {metrics['compressed_size']} bytes "
                f"({metrics['ratio']:.1%} reduction, {metrics.get('compression_time_ms', 0):.1f}ms)"
            )

        # Update headers
        headers = MutableHeaders(response.headers)
        headers["content-encoding"] = encoding
        headers["content-length"] = str(len(compressed_body))
        headers["vary"] = "Accept-Encoding"

        # Optional debug headers
        if logger.isEnabledFor(10):  # DEBUG level
            headers["x-uncompressed-size"] = str(len(body))
            headers["x-compression-ratio"] = f"{compression_ratio:.1f}%"

        # Remove content-length if streaming
        if "transfer-encoding" in headers:
            headers.pop("content-length", None)

        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
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

    def _compress_gzip(self, data: bytes) -> bytes:
        """Compress data using gzip."""
        return gzip.compress(data, compresslevel=self.gzip_level)

    def _compress_brotli(self, data: bytes) -> bytes:
        """Compress data using brotli."""
        if not HAS_BROTLI:
            raise RuntimeError("Brotli not available")

        mode = self.brotli_modes.get(self.brotli_mode, brotli.MODE_TEXT)
        return brotli.compress(data, quality=self.brotli_quality, mode=mode)


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


def add_compression_middleware(
    app,
    minimum_size: int = 1024,
    gzip_level: int = 6,
    brotli_quality: int = 4,
    exclude_paths: Optional[set] = None,
):
    """
    Add compression middleware to FastAPI app.

    Args:
        app: FastAPI application
        minimum_size: Minimum size to compress (bytes)
        gzip_level: Gzip compression level (1-9)
        brotli_quality: Brotli quality (0-11)
        exclude_paths: Paths to exclude from compression
    """
    app.add_middleware(
        CompressionMiddleware,
        minimum_size=minimum_size,
        gzip_level=gzip_level,
        brotli_quality=brotli_quality,
        exclude_paths=exclude_paths,
    )

    logger.info(
        f"Compression middleware enabled "
        f"(min_size={minimum_size}, gzip_level={gzip_level}, "
        f"brotli={'enabled' if HAS_BROTLI else 'disabled'})"
    )
