"""
Federal Government APIs Module

This module provides clients for federal government data sources:
- IBGE (Brazilian Institute of Geography and Statistics)
- DataSUS (Health Ministry data)
- INEP (Education data)

Author: Anderson Henrique da Silva
Created: 2025-10-12
License: Proprietary - All rights reserved
"""

from .ibge_client import IBGEClient
from .datasus_client import DataSUSClient
from .inep_client import INEPClient

__all__ = [
    "IBGEClient",
    "DataSUSClient",
    "INEPClient",
]
