"""Tests for compression middleware and service."""

import pytest
import gzip
import json
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from httpx import AsyncClient
import asyncio

from src.services.compression_service import CompressionService, CompressionAlgorithm
from src.api.middleware.compression import CompressionMiddleware
from src.api.middleware.streaming_compression import compress_streaming_response


class TestCompressionService:
    """Test compression service."""
    
    @pytest.fixture
    def compression_service(self):
        """Create compression service instance."""
        return CompressionService()
    
    def test_compress_gzip(self, compression_service):
        """Test gzip compression."""
        data = b"Hello World! " * 100  # Repeat to ensure compression
        
        compressed, encoding, metrics = compression_service.compress(
            data=data,
            content_type="text/plain",
            accept_encoding="gzip"
        )
        
        assert encoding == "gzip"
        assert len(compressed) < len(data)
        assert metrics["algorithm"] == CompressionAlgorithm.GZIP
        assert metrics["ratio"] > 0.5  # Should achieve >50% compression
        
        # Verify can decompress
        decompressed = gzip.decompress(compressed)
        assert decompressed == data
    
    def test_compress_below_threshold(self, compression_service):
        """Test compression with data below threshold."""
        data = b"Small"
        
        compressed, encoding, metrics = compression_service.compress(
            data=data,
            content_type="text/plain",
            accept_encoding="gzip"
        )
        
        assert encoding == "identity"
        assert compressed == data
        assert metrics["reason"] == "below_min_size"
    
    def test_algorithm_selection(self, compression_service):
        """Test algorithm selection based on accept-encoding."""
        data = b"Test data " * 100
        
        # Test with multiple encodings
        compressed, encoding, metrics = compression_service.compress(
            data=data,
            content_type="application/json",
            accept_encoding="gzip, deflate, br;q=0.9"
        )
        
        # Should prefer br if available, otherwise gzip
        assert encoding in ["br", "gzip"]
        assert len(compressed) < len(data)
    
    def test_content_type_profiles(self, compression_service):
        """Test different compression profiles for content types."""
        data = b'{"key": "value"}' * 100
        
        # JSON should use optimal settings
        compressed, encoding, metrics = compression_service.compress(
            data=data,
            content_type="application/json",
            accept_encoding="gzip"
        )
        
        assert encoding == "gzip"
        assert metrics["ratio"] > 0.8  # JSON compresses very well
    
    def test_metrics_tracking(self, compression_service):
        """Test metrics tracking."""
        # Perform several compressions
        for _ in range(5):
            compression_service.compress(
                data=b"Test data " * 100,
                content_type="text/plain",
                accept_encoding="gzip"
            )
        
        metrics = compression_service.get_metrics()
        
        assert metrics["total_requests"] == 5
        assert metrics["total_bytes_saved"] > 0
        assert "text/plain" in metrics["content_types"]
        assert CompressionAlgorithm.GZIP in metrics["algorithms"]


@pytest.mark.asyncio
class TestCompressionMiddleware:
    """Test compression middleware."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI app."""
        app = FastAPI()
        
        # Add compression middleware
        app.add_middleware(
            CompressionMiddleware,
            minimum_size=100,
            gzip_level=6
        )
        
        @app.get("/text")
        def get_text():
            return Response(
                content="Hello World! " * 50,
                media_type="text/plain"
            )
        
        @app.get("/json")
        def get_json():
            return {"data": "value " * 50}
        
        @app.get("/small")
        def get_small():
            return "Small"
        
        @app.get("/stream")
        async def get_stream():
            async def generate():
                for i in range(10):
                    yield f"Chunk {i}\n" * 10
                    await asyncio.sleep(0.01)
            
            return compress_streaming_response(
                generate(),
                content_type="text/plain"
            )
        
        return app
    
    async def test_text_compression(self, app):
        """Test text response compression."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/text",
                headers={"Accept-Encoding": "gzip"}
            )
            
            assert response.status_code == 200
            assert response.headers.get("content-encoding") == "gzip"
            assert "vary" in response.headers
            
            # Content should be compressed
            assert len(response.content) < len("Hello World! " * 50)
    
    async def test_json_compression(self, app):
        """Test JSON response compression."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/json",
                headers={"Accept-Encoding": "gzip"}
            )
            
            assert response.status_code == 200
            assert response.headers.get("content-encoding") == "gzip"
            
            # Should be able to decode JSON
            data = response.json()
            assert "data" in data
    
    async def test_no_compression_small(self, app):
        """Test no compression for small responses."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/small",
                headers={"Accept-Encoding": "gzip"}
            )
            
            assert response.status_code == 200
            assert response.headers.get("content-encoding") is None
            assert response.text == "Small"
    
    async def test_no_accept_encoding(self, app):
        """Test response without accept-encoding."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/text")
            
            assert response.status_code == 200
            assert response.headers.get("content-encoding") is None
    
    async def test_streaming_compression(self, app):
        """Test streaming response compression."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/stream",
                headers={"Accept-Encoding": "gzip"}
            )
            
            assert response.status_code == 200
            assert response.headers.get("content-encoding") == "gzip"
            
            # Decompress and verify content
            content = gzip.decompress(response.content).decode()
            assert "Chunk 0" in content
            assert "Chunk 9" in content