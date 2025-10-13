"""
Transparency APIs Integration Module

This module provides unified access to Brazilian government transparency data
from federal, state, and municipal sources.

Supported sources:
- Portal da Transparência Federal
- TCEs (Tribunais de Contas Estaduais)
- State transparency portals
- CKAN-based open data portals
- IBGE APIs

Author: Anderson Henrique da Silva
Created: 2025-10-09 14:15:27 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

from .agent_integration import TransparencyDataCollector, get_transparency_collector
from .base import TransparencyAPIClient
from .cache import CacheTTL, TransparencyCache, get_cache
from .health_check import HealthMonitor, HealthStatus, get_health_monitor
from .registry import TransparencyAPIRegistry, registry
from .validators import AnomalyDetector, DataValidator

__version__ = "1.0.0"
__author__ = "Anderson Henrique da Silva"
__created__ = "2025-10-09 14:15:27 -03"

__all__ = [
    # Core registry and client
    "registry",
    "TransparencyAPIRegistry",
    "TransparencyAPIClient",
    # Caching
    "get_cache",
    "TransparencyCache",
    "CacheTTL",
    # Validation and anomaly detection
    "DataValidator",
    "AnomalyDetector",
    # Health monitoring
    "get_health_monitor",
    "HealthMonitor",
    "HealthStatus",
    # Agent integration
    "get_transparency_collector",
    "TransparencyDataCollector",
]
