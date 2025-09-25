"""
Module: api.routes.admin.compression
Description: Admin routes for compression monitoring and configuration
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.core import get_logger
from src.api.dependencies import require_admin
from src.services.compression_service import compression_service

logger = get_logger(__name__)

router = APIRouter(prefix="/compression", tags=["Admin - Compression"])


@router.get("/metrics")
async def get_compression_metrics(
    admin_user=Depends(require_admin)
):
    """
    Get compression metrics and statistics.
    
    Requires admin privileges.
    """
    try:
        metrics = compression_service.get_metrics()
        
        # Calculate bandwidth savings
        if metrics["total_bytes_saved"] > 0:
            # Assume average bandwidth cost of $0.09 per GB
            gb_saved = metrics["total_bytes_saved"] / (1024 ** 3)
            estimated_savings = gb_saved * 0.09
            
            metrics["bandwidth_savings"] = {
                "gb_saved": round(gb_saved, 2),
                "estimated_cost_savings_usd": round(estimated_savings, 2)
            }
        
        return metrics
        
    except Exception as e:
        logger.error(
            "compression_metrics_error",
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get compression metrics"
        )


@router.get("/optimize")
async def get_optimization_suggestions(
    admin_user=Depends(require_admin)
):
    """
    Get compression optimization suggestions.
    
    Requires admin privileges.
    """
    try:
        optimization = compression_service.optimize_settings()
        
        logger.info(
            "admin_compression_optimization_requested",
            admin=admin_user.get("email"),
            suggestions_count=len(optimization["suggestions"])
        )
        
        return optimization
        
    except Exception as e:
        logger.error(
            "compression_optimization_error",
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get optimization suggestions"
        )


@router.get("/algorithms")
async def get_available_algorithms(
    admin_user=Depends(require_admin)
):
    """
    Get available compression algorithms.
    
    Requires admin privileges.
    """
    algorithms = {
        "gzip": {
            "available": True,
            "description": "Standard gzip compression",
            "levels": "1-9",
            "pros": ["Universal support", "Good compression ratio"],
            "cons": ["Slower than newer algorithms"]
        },
        "deflate": {
            "available": True,
            "description": "Raw deflate compression",
            "levels": "1-9",
            "pros": ["Widely supported", "Fast"],
            "cons": ["Slightly worse ratio than gzip"]
        }
    }
    
    # Check Brotli
    try:
        import brotli
        algorithms["br"] = {
            "available": True,
            "description": "Google's Brotli compression",
            "levels": "0-11",
            "pros": ["Best compression ratio", "Good for text"],
            "cons": ["Slower compression", "Less browser support"]
        }
    except ImportError:
        algorithms["br"] = {
            "available": False,
            "description": "Google's Brotli compression",
            "install": "pip install brotli"
        }
    
    # Check Zstandard
    try:
        import zstandard
        algorithms["zstd"] = {
            "available": True,
            "description": "Facebook's Zstandard compression",
            "levels": "1-22",
            "pros": ["Very fast", "Good ratio", "Streaming support"],
            "cons": ["Limited browser support"]
        }
    except ImportError:
        algorithms["zstd"] = {
            "available": False,
            "description": "Facebook's Zstandard compression",
            "install": "pip install zstandard"
        }
    
    return {
        "algorithms": algorithms,
        "recommended": "br" if algorithms["br"]["available"] else "gzip"
    }


@router.get("/test")
async def test_compression(
    text: str = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100,
    admin_user=Depends(require_admin)
):
    """
    Test compression with sample text.
    
    Requires admin privileges.
    """
    test_data = text.encode('utf-8')
    results = {}
    
    # Test different algorithms
    for accept_encoding in ["gzip", "br", "zstd", "deflate", "gzip, br"]:
        compressed, encoding, metrics = compression_service.compress(
            data=test_data,
            content_type="text/plain",
            accept_encoding=accept_encoding
        )
        
        if encoding != "identity":
            results[accept_encoding] = {
                "encoding_used": encoding,
                "original_size": len(test_data),
                "compressed_size": len(compressed),
                "compression_ratio": f"{metrics.get('ratio', 0):.1%}",
                "time_ms": f"{metrics.get('compression_time_ms', 0):.2f}",
                "throughput_mbps": f"{metrics.get('throughput_mbps', 0):.1f}"
            }
    
    return {
        "test_results": results,
        "test_data_info": {
            "content": text[:50] + "...",
            "size_bytes": len(test_data),
            "content_type": "text/plain"
        }
    }