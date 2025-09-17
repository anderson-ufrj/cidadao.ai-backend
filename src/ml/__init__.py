"""Machine Learning models and utilities for Cidadao.AI.

This module provides ML capabilities including:
- Anomaly detection algorithms
- Pattern analysis and correlation detection
- Predictive models for spending analysis

Status: Stub implementation - Full ML models planned for enhancement phase.
"""

from .anomaly_detector import AnomalyDetector
from .pattern_analyzer import PatternAnalyzer
from .models import MLModel

__all__ = [
    "AnomalyDetector",
    "PatternAnalyzer", 
    "MLModel"
]