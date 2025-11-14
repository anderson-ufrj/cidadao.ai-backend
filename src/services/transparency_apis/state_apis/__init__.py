"""
State Transparency APIs

API clients for Brazilian state-level transparency portals.

Supported states:
- Rondônia (RO): Direct REST API
- São Paulo (SP): CKAN portal
- Rio de Janeiro (RJ): CKAN portal
- Rio Grande do Sul (RS): CKAN portal
- Santa Catarina (SC): CKAN portal
- Bahia (BA): CKAN portal

Author: Anderson Henrique da Silva
Created: 2025-10-09 14:17:30 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

from .ckan_client import CKANClient
from .rondonia_cge_client import RondoniaCGEClient

__all__ = [
    "CKANClient",
    "RondoniaCGEClient",
]

__version__ = "1.0.0"
