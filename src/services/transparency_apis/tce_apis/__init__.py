"""
TCE (Tribunal de Contas Estadual) APIs

API clients for Brazilian state audit courts (TCEs).
TCEs provide fiscal data for state and municipal governments.

Supported TCEs:
- TCE Bahia (BA): Fiscal audit data
- TCE Ceará (CE): REST API with CSV/JSON
- TCE Minas Gerais (MG): State fiscal data
- TCE Pernambuco (PE): REST API with XML/JSON
- TCE Rio de Janeiro (RJ): REST API v1
- TCE São Paulo (SP): Municipal data APIs

Author: Anderson Henrique da Silva
Created: 2025-10-09 14:18:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

from .tce_ba import TCEBahiaClient
from .tce_ce import TCECearaClient
from .tce_mg import TCEMinasGeraisClient
from .tce_pe import TCEPernambucoClient
from .tce_rj import TCERioDeJaneiroClient
from .tce_sp import TCESaoPauloClient

# Alias for shorter names
TCERioClient = TCERioDeJaneiroClient

__version__ = "1.0.0"

__all__ = [
    "TCEBahiaClient",
    "TCECearaClient",
    "TCEMinasGeraisClient",
    "TCEPernambucoClient",
    "TCERioDeJaneiroClient",
    "TCERioClient",  # Alias
    "TCESaoPauloClient",
]
