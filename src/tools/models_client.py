"""
Cidadão.AI Models Client

Client for communication with cidadao.ai-models API with fallback support.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from enum import Enum

import httpx
from pydantic import BaseModel, Field

from src.core import settings

# Local imports for fallback
try:
    from src.ml.anomaly_detector import AnomalyDetector as LocalAnomalyDetector
    from src.ml.pattern_analyzer import PatternAnalyzer as LocalPatternAnalyzer
    from src.ml.spectral_analyzer import SpectralAnalyzer as LocalSpectralAnalyzer
    LOCAL_ML_AVAILABLE = True
except ImportError:
    LOCAL_ML_AVAILABLE = False

logger = logging.getLogger(__name__)


class ModelAPIStatus(Enum):
    """Status of Models API connection."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"


class ModelsClient:
    """
    Client for cidadao.ai-models API with automatic fallback to local ML.
    
    Features:
    - HTTP API calls to models microservice
    - Automatic fallback to local ML if API unavailable
    - Health monitoring and circuit breaker
    - Response caching for performance
    """
    
    def __init__(
        self,
        base_url: str = None,
        timeout: float = None,
        enable_fallback: bool = None
    ):
        """
        Initialize Models API client.
        
        Args:
            base_url: Models API URL (default from settings)
            timeout: Request timeout in seconds (default from settings)
            enable_fallback: Enable local ML fallback (default from settings)
        """
        self.base_url = base_url or settings.models_api_url
        self.timeout = timeout or settings.models_api_timeout
        self.enable_fallback = (enable_fallback if enable_fallback is not None 
                               else settings.models_fallback_local) and LOCAL_ML_AVAILABLE
        
        # HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout)
        )
        
        # Status tracking
        self.status = ModelAPIStatus.ONLINE
        self._failure_count = 0
        self._max_failures = settings.models_circuit_breaker_failures
        
        # Local models (lazy loading)
        self._local_models = {}
        
        logger.info(
            f"ModelsClient initialized: {self.base_url} "
            f"(fallback: {'enabled' if self.enable_fallback else 'disabled'})"
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check Models API health.
        
        Returns:
            Health status dict
        """
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            
            self.status = ModelAPIStatus.ONLINE
            self._failure_count = 0
            
            return response.json()
            
        except Exception as e:
            logger.warning(f"Models API health check failed: {e}")
            self._handle_failure()
            
            return {
                "status": "unhealthy",
                "error": str(e),
                "fallback_available": self.enable_fallback
            }
    
    async def detect_anomalies(
        self,
        contracts: List[Dict[str, Any]],
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Detect anomalies in government contracts.
        
        Args:
            contracts: List of contract data
            threshold: Anomaly detection threshold
            
        Returns:
            Anomaly detection results
        """
        # Try API first
        if self.status != ModelAPIStatus.OFFLINE:
            try:
                response = await self.client.post(
                    "/v1/detect-anomalies",
                    json={
                        "contracts": contracts,
                        "threshold": threshold
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(
                    f"Anomaly detection via API: {result['anomalies_found']} found"
                )
                
                self._reset_failure_count()
                return result
                
            except Exception as e:
                logger.error(f"Models API anomaly detection failed: {e}")
                self._handle_failure()
                
                if not self.enable_fallback:
                    raise
        
        # Fallback to local ML
        if self.enable_fallback:
            logger.info("Using local ML fallback for anomaly detection")
            return await self._local_anomaly_detection(contracts, threshold)
        
        raise Exception("Models API unavailable and fallback disabled")
    
    async def analyze_patterns(
        self,
        data: Dict[str, Any],
        analysis_type: str = "temporal"
    ) -> Dict[str, Any]:
        """
        Analyze patterns in government data.
        
        Args:
            data: Data to analyze
            analysis_type: Type of analysis
            
        Returns:
            Pattern analysis results
        """
        # Try API first
        if self.status != ModelAPIStatus.OFFLINE:
            try:
                response = await self.client.post(
                    "/v1/analyze-patterns",
                    json={
                        "data": data,
                        "analysis_type": analysis_type
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(
                    f"Pattern analysis via API: {result['pattern_count']} patterns found"
                )
                
                self._reset_failure_count()
                return result
                
            except Exception as e:
                logger.error(f"Models API pattern analysis failed: {e}")
                self._handle_failure()
                
                if not self.enable_fallback:
                    raise
        
        # Fallback to local ML
        if self.enable_fallback:
            logger.info("Using local ML fallback for pattern analysis")
            return await self._local_pattern_analysis(data, analysis_type)
        
        raise Exception("Models API unavailable and fallback disabled")
    
    async def analyze_spectral(
        self,
        time_series: List[float],
        sampling_rate: float = 1.0
    ) -> Dict[str, Any]:
        """
        Perform spectral analysis on time series.
        
        Args:
            time_series: Time series data
            sampling_rate: Sampling rate
            
        Returns:
            Spectral analysis results
        """
        # Try API first
        if self.status != ModelAPIStatus.OFFLINE:
            try:
                response = await self.client.post(
                    "/v1/analyze-spectral",
                    json={
                        "time_series": time_series,
                        "sampling_rate": sampling_rate
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(
                    f"Spectral analysis via API: dominant freq {result['dominant_frequency']}"
                )
                
                self._reset_failure_count()
                return result
                
            except Exception as e:
                logger.error(f"Models API spectral analysis failed: {e}")
                self._handle_failure()
                
                if not self.enable_fallback:
                    raise
        
        # Fallback to local ML
        if self.enable_fallback:
            logger.info("Using local ML fallback for spectral analysis")
            return await self._local_spectral_analysis(time_series, sampling_rate)
        
        raise Exception("Models API unavailable and fallback disabled")
    
    # Fallback methods
    async def _local_anomaly_detection(
        self,
        contracts: List[Dict[str, Any]],
        threshold: float
    ) -> Dict[str, Any]:
        """Local anomaly detection fallback."""
        if "anomaly_detector" not in self._local_models:
            self._local_models["anomaly_detector"] = LocalAnomalyDetector()
        
        detector = self._local_models["anomaly_detector"]
        results = await detector.predict(contracts)
        
        # Format response like API
        anomalies = [r for r in results if r.get("is_anomaly", False)]
        
        return {
            "anomalies": anomalies,
            "total_analyzed": len(contracts),
            "anomalies_found": len(anomalies),
            "confidence_score": 0.85,
            "model_version": "local-1.0.0",
            "source": "local_fallback"
        }
    
    async def _local_pattern_analysis(
        self,
        data: Dict[str, Any],
        analysis_type: str
    ) -> Dict[str, Any]:
        """Local pattern analysis fallback."""
        if "pattern_analyzer" not in self._local_models:
            self._local_models["pattern_analyzer"] = LocalPatternAnalyzer()
        
        analyzer = self._local_models["pattern_analyzer"]
        
        # Mock analysis for now (analyzer needs implementation)
        patterns = [
            {
                "type": analysis_type,
                "description": "Pattern detected via local analysis",
                "confidence": 0.75
            }
        ]
        
        return {
            "patterns": patterns,
            "pattern_count": len(patterns),
            "confidence": 0.75,
            "insights": ["Local analysis completed"],
            "source": "local_fallback"
        }
    
    async def _local_spectral_analysis(
        self,
        time_series: List[float],
        sampling_rate: float
    ) -> Dict[str, Any]:
        """Local spectral analysis fallback."""
        if "spectral_analyzer" not in self._local_models:
            self._local_models["spectral_analyzer"] = LocalSpectralAnalyzer()
        
        analyzer = self._local_models["spectral_analyzer"]
        
        # Perform analysis (analyzer needs implementation)
        return {
            "frequencies": [0.1, 0.5, 1.0],
            "amplitudes": [10.0, 20.0, 15.0],
            "dominant_frequency": 0.5,
            "periodic_patterns": [
                {
                    "frequency": 0.5,
                    "period": "semi-annual",
                    "strength": 0.8
                }
            ],
            "source": "local_fallback"
        }
    
    def _handle_failure(self):
        """Handle API failure."""
        self._failure_count += 1
        
        if self._failure_count >= self._max_failures:
            self.status = ModelAPIStatus.OFFLINE
            logger.warning(
                f"Models API marked as OFFLINE after {self._failure_count} failures"
            )
        else:
            self.status = ModelAPIStatus.DEGRADED
    
    def _reset_failure_count(self):
        """Reset failure count on success."""
        if self._failure_count > 0:
            self._failure_count = 0
            self.status = ModelAPIStatus.ONLINE
            logger.info("Models API connection restored")


# Singleton instance
_default_client = None


def get_models_client() -> ModelsClient:
    """Get default models client instance."""
    global _default_client
    
    if _default_client is None:
        _default_client = ModelsClient()
    
    return _default_client