"""
Module: api.middleware.streaming_compression
Description: Compression middleware for streaming responses (SSE, WebSocket)
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import gzip
import asyncio
from typing import AsyncIterator, Optional
from io import BytesIO

from starlette.types import ASGIApp, Message, Receive, Scope, Send
from starlette.responses import StreamingResponse

from src.core import get_logger

logger = get_logger(__name__)


class GzipStream:
    """Streaming gzip compressor."""
    
    def __init__(self, level: int = 6):
        self.level = level
        self._buffer = BytesIO()
        self._gzip = gzip.GzipFile(
            fileobj=self._buffer,
            mode='wb',
            compresslevel=level
        )
        
    def compress(self, data: bytes) -> bytes:
        """Compress chunk of data."""
        self._gzip.write(data)
        self._gzip.flush()
        
        # Get compressed data
        self._buffer.seek(0)
        compressed = self._buffer.read()
        
        # Reset buffer
        self._buffer.seek(0)
        self._buffer.truncate()
        
        return compressed
    
    def close(self) -> bytes:
        """Finish compression and get final data."""
        self._gzip.close()
        self._buffer.seek(0)
        return self._buffer.read()


class StreamingCompressionMiddleware:
    """
    Middleware for compressing streaming responses.
    
    Handles:
    - Server-Sent Events (SSE)
    - Large file downloads
    - Chunked responses
    """
    
    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 256,
        compression_level: int = 6,
        chunk_size: int = 8192
    ):
        self.app = app
        self.minimum_size = minimum_size
        self.compression_level = compression_level
        self.chunk_size = chunk_size
        
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check accept-encoding
        headers = dict(scope.get("headers", []))
        accept_encoding = headers.get(b"accept-encoding", b"").decode().lower()
        
        if "gzip" not in accept_encoding:
            await self.app(scope, receive, send)
            return
        
        # Intercept send
        compressor = None
        content_type = None
        should_compress = False
        
        async def wrapped_send(message: Message) -> None:
            nonlocal compressor, content_type, should_compress
            
            if message["type"] == "http.response.start":
                # Check content type
                headers_dict = dict(message.get("headers", []))
                content_type = headers_dict.get(b"content-type", b"").decode()
                
                # Determine if we should compress
                if self._should_compress_stream(content_type):
                    should_compress = True
                    compressor = GzipStream(self.compression_level)
                    
                    # Update headers
                    new_headers = []
                    for name, value in message.get("headers", []):
                        # Skip content-length for streaming
                        if name.lower() not in (b"content-length", b"content-encoding"):
                            new_headers.append((name, value))
                    
                    new_headers.extend([
                        (b"content-encoding", b"gzip"),
                        (b"vary", b"Accept-Encoding")
                    ])
                    
                    message["headers"] = new_headers
                    
                    logger.debug(
                        "streaming_compression_enabled",
                        content_type=content_type
                    )
            
            elif message["type"] == "http.response.body" and should_compress:
                body = message.get("body", b"")
                more_body = message.get("more_body", False)
                
                if body:
                    # Compress chunk
                    compressed = compressor.compress(body)
                    message["body"] = compressed
                
                if not more_body and compressor:
                    # Final chunk - close compressor
                    final_data = compressor.close()
                    if final_data:
                        # Send final compressed data
                        await send({
                            "type": "http.response.body",
                            "body": final_data,
                            "more_body": True
                        })
                    compressor = None
            
            await send(message)
        
        await self.app(scope, receive, wrapped_send)
    
    def _should_compress_stream(self, content_type: str) -> bool:
        """Check if streaming content should be compressed."""
        content_type = content_type.lower()
        
        # Always compress SSE
        if "text/event-stream" in content_type:
            return True
        
        # Compress JSON streams
        if "application/json" in content_type and "stream" in content_type:
            return True
        
        # Compress text streams
        if content_type.startswith("text/") and "stream" in content_type:
            return True
        
        # Compress CSV exports
        if "text/csv" in content_type:
            return True
        
        # Compress NDJSON (newline-delimited JSON)
        if "application/x-ndjson" in content_type:
            return True
        
        return False


async def compress_streaming_response(
    response_iterator: AsyncIterator[str],
    content_type: str = "text/plain",
    encoding: str = "gzip"
) -> StreamingResponse:
    """
    Create a compressed streaming response.
    
    Args:
        response_iterator: Async iterator yielding response chunks
        content_type: Content type of response
        encoding: Compression encoding (only gzip supported currently)
    
    Returns:
        StreamingResponse with compression
    """
    async def compressed_iterator():
        compressor = GzipStream()
        
        try:
            async for chunk in response_iterator:
                if isinstance(chunk, str):
                    chunk = chunk.encode('utf-8')
                
                compressed = compressor.compress(chunk)
                if compressed:
                    yield compressed
            
            # Yield final compressed data
            final = compressor.close()
            if final:
                yield final
                
        except Exception as e:
            logger.error(
                "streaming_compression_error",
                error=str(e),
                exc_info=True
            )
            raise
    
    headers = {
        "Content-Type": content_type,
        "Content-Encoding": encoding,
        "Vary": "Accept-Encoding"
    }
    
    return StreamingResponse(
        compressed_iterator(),
        headers=headers
    )