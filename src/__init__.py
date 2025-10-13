"""Cidadão.AI - Sistema multi-agente de IA para transparência pública brasileira.

This package provides a comprehensive multi-agent AI system designed specifically
for analyzing Brazilian government transparency data. Built with enterprise-grade
architecture and sophisticated AI capabilities.

Key Features:
- 17 specialized AI agents with Brazilian cultural identities
- Advanced anomaly detection in government contracts
- Multi-provider LLM support (Groq, Together, HuggingFace)
- Enterprise security with HashiCorp Vault integration
- Production-ready monitoring with Prometheus/Grafana
- Comprehensive audit logging and compliance tracking

Modules:
- agents: Multi-agent system with 17 specialized agents
- api: FastAPI-based REST API with enterprise security
- core: Core configuration, logging, and utilities
- infrastructure: System orchestration and management
- memory: Agent memory systems (episodic, semantic, conversational)
- services: Business logic and data processing services
- tools: Utility tools and external integrations
- cli: Command-line interface for system operations

Usage:
    # As a library
    from src.agents import ZumbiInvestigatorAgent
    from src.api.app import create_app

    # As a CLI tool
    cidadao investigate --help
    cidadao analyze --help

Author: Anderson Henrique da Silva
Email: andersonhs27@gmail.com
License: Proprietary - All rights reserved
Version: 1.0.0
"""

# Package metadata
__version__ = "1.0.0"
__author__ = "Anderson Henrique da Silva"
__email__ = "andersonhs27@gmail.com"
__license__ = "Proprietary - All rights reserved"
__description__ = "Sistema multi-agente de IA para transparência pública brasileira"

# Key exports for external usage
from src.core.config import get_settings
from src.core.exceptions import CidadaoAIError

# Version info tuple
VERSION = (1, 0, 0)
VERSION_INFO = {"major": 1, "minor": 0, "patch": 0, "release": "stable"}

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
    "VERSION",
    "VERSION_INFO",
    "get_settings",
    "CidadaoAIError",
]
