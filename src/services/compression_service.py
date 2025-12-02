"""
Module: services.compression_service
Description: Advanced compression service with metrics and optimization
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import gzip
import time
import zlib
from collections import defaultdict
from enum import Enum
from typing import Any

from src.core import get_logger

logger = get_logger(__name__)

try:
    import brotli

    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False
    brotli = None

try:
    import zstandard as zstd

    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False
    zstd = None


class CompressionAlgorithm(str, Enum):
    """Available compression algorithms."""

    GZIP = "gzip"
    BROTLI = "br"
    ZSTD = "zstd"
    DEFLATE = "deflate"
    IDENTITY = "identity"  # No compression


class CompressionProfile:
    """Compression profile for different content types."""

    def __init__(
        self,
        algorithm: CompressionAlgorithm,
        level: int,
        min_size: int = 1024,
        max_size: int | None = None,
    ):
        self.algorithm = algorithm
        self.level = level
        self.min_size = min_size
        self.max_size = max_size


class CompressionService:
    """Service for managing response compression."""

    # Default compression profiles by content type
    DEFAULT_PROFILES = {
        "application/json": CompressionProfile(
            CompressionAlgorithm.BROTLI if HAS_BROTLI else CompressionAlgorithm.GZIP,
            level=4,
            min_size=1024,
        ),
        "text/html": CompressionProfile(
            CompressionAlgorithm.BROTLI if HAS_BROTLI else CompressionAlgorithm.GZIP,
            level=6,
            min_size=512,
        ),
        "text/plain": CompressionProfile(
            CompressionAlgorithm.GZIP, level=6, min_size=1024
        ),
        "application/javascript": CompressionProfile(
            CompressionAlgorithm.BROTLI if HAS_BROTLI else CompressionAlgorithm.GZIP,
            level=5,
            min_size=512,
        ),
        "text/css": CompressionProfile(
            CompressionAlgorithm.BROTLI if HAS_BROTLI else CompressionAlgorithm.GZIP,
            level=6,
            min_size=256,
        ),
        "application/xml": CompressionProfile(
            CompressionAlgorithm.GZIP, level=6, min_size=1024
        ),
        "text/csv": CompressionProfile(
            CompressionAlgorithm.GZIP, level=9, min_size=2048  # CSVs compress very well
        ),
    }

    def __init__(self):
        """Initialize compression service."""
        self._metrics = defaultdict(
            lambda: {
                "total_bytes": 0,
                "compressed_bytes": 0,
                "compression_time": 0,
                "count": 0,
            }
        )
        self._algorithm_stats = defaultdict(
            lambda: {"used": 0, "total_saved": 0, "avg_ratio": 0}
        )
        self._content_type_stats = defaultdict(
            lambda: {"count": 0, "avg_size": 0, "avg_compressed": 0}
        )

    def compress(
        self,
        data: bytes,
        content_type: str,
        accept_encoding: str,
        force_algorithm: CompressionAlgorithm | None = None,
    ) -> tuple[bytes, str, dict[str, Any]]:
        """
        Compress data using the best available algorithm.

        Returns:
            Tuple of (compressed_data, encoding, metrics)
        """
        start_time = time.time()
        original_size = len(data)

        # Get compression profile
        profile = self._get_profile(content_type)

        # Check size limits
        if original_size < profile.min_size:
            return (
                data,
                "identity",
                {
                    "reason": "below_min_size",
                    "original_size": original_size,
                    "min_size": profile.min_size,
                },
            )

        if profile.max_size and original_size > profile.max_size:
            return (
                data,
                "identity",
                {
                    "reason": "above_max_size",
                    "original_size": original_size,
                    "max_size": profile.max_size,
                },
            )

        # Choose algorithm
        if force_algorithm:
            algorithm = force_algorithm
        else:
            algorithm = self._choose_algorithm(accept_encoding, profile)

        # Compress
        try:
            compressed_data, encoding = self._compress_with_algorithm(
                data, algorithm, profile.level
            )

            compression_time = time.time() - start_time
            compressed_size = len(compressed_data)
            ratio = 1 - (compressed_size / original_size)

            # Update metrics
            self._update_metrics(
                content_type,
                algorithm,
                original_size,
                compressed_size,
                compression_time,
            )

            metrics = {
                "algorithm": algorithm,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "ratio": ratio,
                "saved_bytes": original_size - compressed_size,
                "compression_time_ms": compression_time * 1000,
                "throughput_mbps": (
                    (original_size / compression_time / 1024 / 1024)
                    if compression_time > 0
                    else 0
                ),
            }

            logger.debug(
                "compression_completed",
                content_type=content_type,
                algorithm=algorithm,
                ratio=f"{ratio:.1%}",
                time_ms=f"{compression_time * 1000:.1f}",
            )

            return compressed_data, encoding, metrics

        except Exception as e:
            logger.error("compression_failed", algorithm=algorithm, error=str(e))
            return data, "identity", {"error": str(e)}

    def _get_profile(self, content_type: str) -> CompressionProfile:
        """Get compression profile for content type."""
        # Extract base content type
        base_type = content_type.split(";")[0].strip().lower()

        # Check exact match
        if base_type in self.DEFAULT_PROFILES:
            return self.DEFAULT_PROFILES[base_type]

        # Check prefix match
        if base_type.startswith("text/"):
            return CompressionProfile(CompressionAlgorithm.GZIP, level=6)

        if base_type.startswith("application/") and "json" in base_type:
            return CompressionProfile(CompressionAlgorithm.GZIP, level=6)

        # Default profile
        return CompressionProfile(CompressionAlgorithm.GZIP, level=5)

    def _choose_algorithm(
        self, accept_encoding: str, profile: CompressionProfile
    ) -> CompressionAlgorithm:
        """Choose best algorithm based on client support and profile."""
        accept_encoding = accept_encoding.lower()

        # Parse quality values
        encodings = {}
        for encoding in accept_encoding.split(","):
            parts = encoding.strip().split(";")
            name = parts[0].strip()
            quality = 1.0

            if len(parts) > 1:
                for param in parts[1:]:
                    if param.strip().startswith("q="):
                        try:
                            quality = float(param.split("=")[1])
                        except:
                            pass

            encodings[name] = quality

        # Prefer profile algorithm if supported
        if profile.algorithm == CompressionAlgorithm.BROTLI and "br" in encodings:
            return CompressionAlgorithm.BROTLI

        if (
            profile.algorithm == CompressionAlgorithm.ZSTD
            and "zstd" in encodings
            and HAS_ZSTD
        ):
            return CompressionAlgorithm.ZSTD

        # Check alternatives in order of preference
        if "br" in encodings and HAS_BROTLI and encodings.get("br", 0) > 0:
            return CompressionAlgorithm.BROTLI

        if "zstd" in encodings and HAS_ZSTD and encodings.get("zstd", 0) > 0:
            return CompressionAlgorithm.ZSTD

        if "gzip" in encodings and encodings.get("gzip", 0) > 0:
            return CompressionAlgorithm.GZIP

        if "deflate" in encodings and encodings.get("deflate", 0) > 0:
            return CompressionAlgorithm.DEFLATE

        # Default to gzip if nothing else
        return CompressionAlgorithm.GZIP

    def _compress_with_algorithm(
        self, data: bytes, algorithm: CompressionAlgorithm, level: int
    ) -> tuple[bytes, str]:
        """Compress data with specified algorithm."""
        if algorithm == CompressionAlgorithm.GZIP:
            return gzip.compress(data, compresslevel=level), "gzip"

        if algorithm == CompressionAlgorithm.BROTLI:
            if not HAS_BROTLI:
                raise RuntimeError("Brotli not available")
            return brotli.compress(data, quality=level), "br"

        if algorithm == CompressionAlgorithm.ZSTD:
            if not HAS_ZSTD:
                raise RuntimeError("Zstandard not available")
            cctx = zstd.ZstdCompressor(level=level)
            return cctx.compress(data), "zstd"

        if algorithm == CompressionAlgorithm.DEFLATE:
            return zlib.compress(data, level=level), "deflate"

        return data, "identity"

    def _update_metrics(
        self,
        content_type: str,
        algorithm: CompressionAlgorithm,
        original_size: int,
        compressed_size: int,
        compression_time: float,
    ):
        """Update compression metrics."""
        # Overall metrics
        metrics = self._metrics["overall"]
        metrics["total_bytes"] += original_size
        metrics["compressed_bytes"] += compressed_size
        metrics["compression_time"] += compression_time
        metrics["count"] += 1

        # Per content type metrics
        ct_metrics = self._metrics[content_type]
        ct_metrics["total_bytes"] += original_size
        ct_metrics["compressed_bytes"] += compressed_size
        ct_metrics["compression_time"] += compression_time
        ct_metrics["count"] += 1

        # Algorithm statistics
        algo_stats = self._algorithm_stats[algorithm]
        algo_stats["used"] += 1
        algo_stats["total_saved"] += original_size - compressed_size

        # Content type statistics
        ct_stats = self._content_type_stats[content_type]
        ct_stats["count"] += 1
        ct_stats["avg_size"] = (
            ct_stats["avg_size"] * (ct_stats["count"] - 1) + original_size
        ) / ct_stats["count"]
        ct_stats["avg_compressed"] = (
            ct_stats["avg_compressed"] * (ct_stats["count"] - 1) + compressed_size
        ) / ct_stats["count"]

    def get_metrics(self) -> dict[str, Any]:
        """Get compression metrics."""
        overall = self._metrics["overall"]

        if overall["count"] == 0:
            return {
                "enabled": True,
                "algorithms_available": self._get_available_algorithms(),
                "total_requests": 0,
            }

        total_saved = overall["total_bytes"] - overall["compressed_bytes"]
        avg_ratio = (
            total_saved / overall["total_bytes"] if overall["total_bytes"] > 0 else 0
        )

        return {
            "enabled": True,
            "algorithms_available": self._get_available_algorithms(),
            "total_requests": overall["count"],
            "total_bytes_original": overall["total_bytes"],
            "total_bytes_compressed": overall["compressed_bytes"],
            "total_bytes_saved": total_saved,
            "average_compression_ratio": avg_ratio,
            "average_compression_time_ms": (
                (overall["compression_time"] / overall["count"] * 1000)
                if overall["count"] > 0
                else 0
            ),
            "content_types": self._get_content_type_metrics(),
            "algorithms": self._get_algorithm_metrics(),
        }

    def _get_available_algorithms(self) -> list[str]:
        """Get list of available compression algorithms."""
        algorithms = ["gzip", "deflate"]
        if HAS_BROTLI:
            algorithms.append("br")
        if HAS_ZSTD:
            algorithms.append("zstd")
        return algorithms

    def _get_content_type_metrics(self) -> dict[str, Any]:
        """Get metrics grouped by content type."""
        result = {}

        for content_type, metrics in self._metrics.items():
            if content_type == "overall" or metrics["count"] == 0:
                continue

            saved = metrics["total_bytes"] - metrics["compressed_bytes"]
            ratio = saved / metrics["total_bytes"] if metrics["total_bytes"] > 0 else 0

            result[content_type] = {
                "requests": metrics["count"],
                "total_size": metrics["total_bytes"],
                "compressed_size": metrics["compressed_bytes"],
                "saved_bytes": saved,
                "compression_ratio": ratio,
                "avg_time_ms": (metrics["compression_time"] / metrics["count"] * 1000),
            }

        return result

    def _get_algorithm_metrics(self) -> dict[str, Any]:
        """Get metrics grouped by algorithm."""
        result = {}

        for algorithm, stats in self._algorithm_stats.items():
            if stats["used"] == 0:
                continue

            result[algorithm] = {
                "times_used": stats["used"],
                "total_bytes_saved": stats["total_saved"],
                "avg_bytes_saved": stats["total_saved"] / stats["used"],
            }

        return result

    def optimize_settings(self) -> dict[str, Any]:
        """Analyze metrics and suggest optimizations."""
        suggestions = []

        # Check if Brotli should be enabled
        if not HAS_BROTLI:
            suggestions.append(
                {
                    "type": "install_brotli",
                    "reason": "Brotli provides better compression ratios",
                    "command": "pip install brotli",
                }
            )

        # Check compression ratios by content type
        for content_type, stats in self._content_type_stats.items():
            if stats["count"] < 10:
                continue

            avg_ratio = (
                1 - (stats["avg_compressed"] / stats["avg_size"])
                if stats["avg_size"] > 0
                else 0
            )

            if avg_ratio < 0.2:
                suggestions.append(
                    {
                        "type": "adjust_min_size",
                        "content_type": content_type,
                        "reason": f"Low compression ratio ({avg_ratio:.1%})",
                        "current_avg_size": stats["avg_size"],
                        "suggestion": "Consider increasing minimum size threshold",
                    }
                )

        # Check algorithm usage
        gzip_stats = self._algorithm_stats.get(CompressionAlgorithm.GZIP, {"used": 0})
        brotli_stats = self._algorithm_stats.get(
            CompressionAlgorithm.BROTLI, {"used": 0}
        )

        if HAS_BROTLI and brotli_stats["used"] < gzip_stats["used"] * 0.1:
            suggestions.append(
                {
                    "type": "promote_brotli",
                    "reason": "Brotli underutilized despite being available",
                    "suggestion": "Check client Accept-Encoding headers",
                }
            )

        return {
            "suggestions": suggestions,
            "optimal_settings": self._calculate_optimal_settings(),
        }

    def _calculate_optimal_settings(self) -> dict[str, Any]:
        """Calculate optimal compression settings based on metrics."""
        settings = {}

        # Recommend levels based on average compression time
        overall = self._metrics["overall"]
        if overall["count"] > 0:
            avg_time = overall["compression_time"] / overall["count"]

            if avg_time < 0.001:  # < 1ms
                settings["recommended_gzip_level"] = 9
                settings["recommended_brotli_quality"] = 6
            elif avg_time < 0.005:  # < 5ms
                settings["recommended_gzip_level"] = 6
                settings["recommended_brotli_quality"] = 4
            else:
                settings["recommended_gzip_level"] = 4
                settings["recommended_brotli_quality"] = 2

        return settings


# Global instance
compression_service = CompressionService()
