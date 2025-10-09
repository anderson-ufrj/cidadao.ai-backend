"""
Transparency API Registry

Central registry for all Brazilian transparency APIs.
Provides auto-detection and unified access to federal, state, and TCE APIs.

Author: Anderson Henrique da Silva
Created: 2025-10-09 14:25:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

from typing import Dict, List, Optional, Type
from enum import Enum

from .base import TransparencyAPIClient
from .state_apis.rondonia import RondoniaAPIClient
from .state_apis.ckan_client import CKANClient
from .tce_apis.tce_pe import TCEPernambucoClient
from .tce_apis.tce_ce import TCECearaClient


class APIType(Enum):
    """Types of transparency APIs."""
    FEDERAL = "federal"
    STATE = "state"
    TCE = "tce"
    CKAN = "ckan"


class TransparencyAPIRegistry:
    """
    Central registry for transparency APIs.

    Manages all available API clients and provides methods to:
    - List available APIs
    - Get API client by state/type
    - Auto-detect best API for a query
    """

    def __init__(self):
        """Initialize API registry."""
        self._clients: Dict[str, Type[TransparencyAPIClient]] = {}
        self._instances: Dict[str, TransparencyAPIClient] = {}

        # Register all available APIs
        self._register_default_apis()

    def _register_default_apis(self) -> None:
        """Register all default API clients."""

        # State APIs
        self.register("RO-state", RondoniaAPIClient, APIType.STATE)

        # TCE APIs
        self.register("PE-tce", TCEPernambucoClient, APIType.TCE)
        self.register("CE-tce", TCECearaClient, APIType.TCE)

        # CKAN states (will be instantiated on demand)
        ckan_states = {
            "SP": "https://dadosabertos.sp.gov.br",
            "RJ": "https://dadosabertos.rj.gov.br",
            "RS": "https://dados.rs.gov.br",
            "SC": "https://dados.sc.gov.br",
            "BA": "https://dados.ba.gov.br"
        }

        for state_code, base_url in ckan_states.items():
            # Register CKAN factory
            self._clients[f"{state_code}-ckan"] = (CKANClient, base_url, state_code)

    def register(
        self,
        key: str,
        client_class: Type[TransparencyAPIClient],
        api_type: APIType
    ) -> None:
        """
        Register an API client.

        Args:
            key: Unique identifier (e.g., "SP-state", "PE-tce")
            client_class: Client class
            api_type: Type of API
        """
        self._clients[key] = client_class

    def get_client(self, key: str) -> Optional[TransparencyAPIClient]:
        """
        Get API client instance by key.

        Args:
            key: API identifier

        Returns:
            API client instance or None if not found
        """
        # Check if already instantiated
        if key in self._instances:
            return self._instances[key]

        # Check if registered
        if key not in self._clients:
            return None

        # Instantiate client
        client_info = self._clients[key]

        if isinstance(client_info, tuple):
            # CKAN factory
            client_class, base_url, state_code = client_info
            instance = client_class(base_url, state_code)
        else:
            # Regular class
            instance = client_info()

        # Cache instance
        self._instances[key] = instance

        return instance

    def get_state_apis(self, state_code: str) -> List[TransparencyAPIClient]:
        """
        Get all available APIs for a state.

        Args:
            state_code: Two-letter state code (e.g., "SP", "RJ")

        Returns:
            List of API clients for the state
        """
        clients = []

        # Check for state API
        state_key = f"{state_code}-state"
        if state_key in self._clients:
            client = self.get_client(state_key)
            if client:
                clients.append(client)

        # Check for TCE API
        tce_key = f"{state_code}-tce"
        if tce_key in self._clients:
            client = self.get_client(tce_key)
            if client:
                clients.append(client)

        # Check for CKAN API
        ckan_key = f"{state_code}-ckan"
        if ckan_key in self._clients:
            client = self.get_client(ckan_key)
            if client:
                clients.append(client)

        return clients

    def list_available_apis(self) -> List[str]:
        """
        List all registered API keys.

        Returns:
            List of API identifiers
        """
        return list(self._clients.keys())

    def get_coverage_stats(self) -> Dict[str, int]:
        """
        Get API coverage statistics.

        Returns:
            Dict with counts by API type
        """
        stats = {
            "total": len(self._clients),
            "states": 0,
            "tces": 0,
            "ckan": 0
        }

        for key in self._clients.keys():
            if "-state" in key:
                stats["states"] += 1
            elif "-tce" in key:
                stats["tces"] += 1
            elif "-ckan" in key:
                stats["ckan"] += 1

        return stats


# Global registry instance
registry = TransparencyAPIRegistry()
