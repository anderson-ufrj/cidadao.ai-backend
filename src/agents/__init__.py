"""
Lazy-loading agents module for better performance.
Agents are only imported when actually used, not at module import time.

This reduces startup time from ~1.3s to ~10ms.
"""

import sys
from typing import TYPE_CHECKING, Any

# Always import base classes (lightweight)
from .deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    BaseAgent,
    ReflectiveAgent,
)

# Type checking imports (zero runtime cost)
if TYPE_CHECKING:
    from .abaporu import InvestigationPlan, InvestigationResult, MasterAgent
    from .anita import AnalystAgent
    from .ayrton_senna import SemanticRouter
    from .bonifacio import BonifacioAgent
    from .ceuci import PredictiveAgent
    from .dandara import DandaraAgent
    from .drummond import CommunicationAgent
    from .lampiao import LampiaoAgent
    from .machado import MachadoAgent
    from .maria_quiteria import MariaQuiteriaAgent
    from .nana import (
        ContextMemoryAgent,
        ConversationMemory,
        EpisodicMemory,
        MemoryEntry,
        SemanticMemory,
    )
    from .obaluaie import CorruptionDetectorAgent
    from .oscar_niemeyer import OscarNiemeyerAgent
    from .oxossi import OxossiAgent
    from .santos_dumont import EducatorAgent
    from .simple_agent_pool import agent_pool, get_agent_pool
    from .tiradentes import ReporterAgent
    from .zumbi import InvestigatorAgent


# Lazy import mapping
_LAZY_IMPORTS = {
    # Abaporu (Master Agent)
    "MasterAgent": ("src.agents.abaporu", "MasterAgent"),
    "InvestigationPlan": ("src.agents.abaporu", "InvestigationPlan"),
    "InvestigationResult": ("src.agents.abaporu", "InvestigationResult"),
    # Core agents
    "InvestigatorAgent": ("src.agents.zumbi", "InvestigatorAgent"),
    "AnalystAgent": ("src.agents.anita", "AnalystAgent"),
    "ReporterAgent": ("src.agents.tiradentes", "ReporterAgent"),
    # Other specialized agents
    "SemanticRouter": ("src.agents.ayrton_senna", "SemanticRouter"),
    "BonifacioAgent": ("src.agents.bonifacio", "BonifacioAgent"),
    "PredictiveAgent": ("src.agents.ceuci", "PredictiveAgent"),
    "DandaraAgent": ("src.agents.dandara", "DandaraAgent"),
    "CommunicationAgent": ("src.agents.drummond", "CommunicationAgent"),
    "LampiaoAgent": ("src.agents.lampiao", "LampiaoAgent"),
    "MachadoAgent": ("src.agents.machado", "MachadoAgent"),
    "MariaQuiteriaAgent": ("src.agents.maria_quiteria", "MariaQuiteriaAgent"),
    "CorruptionDetectorAgent": ("src.agents.obaluaie", "CorruptionDetectorAgent"),
    "OscarNiemeyerAgent": ("src.agents.oscar_niemeyer", "OscarNiemeyerAgent"),
    "OxossiAgent": ("src.agents.oxossi", "OxossiAgent"),
    # Educator agent
    "EducatorAgent": ("src.agents.santos_dumont", "EducatorAgent"),
    # Memory agent
    "ContextMemoryAgent": ("src.agents.nana", "ContextMemoryAgent"),
    "MemoryEntry": ("src.agents.nana", "MemoryEntry"),
    "EpisodicMemory": ("src.agents.nana", "EpisodicMemory"),
    "SemanticMemory": ("src.agents.nana", "SemanticMemory"),
    "ConversationMemory": ("src.agents.nana", "ConversationMemory"),
    # Agent pool
    "agent_pool": ("src.agents.simple_agent_pool", "agent_pool"),
    "get_agent_pool": ("src.agents.simple_agent_pool", "get_agent_pool"),
}

# Agent aliases
_ALIASES = {
    "ZumbiAgent": "InvestigatorAgent",
    "AnitaAgent": "AnalystAgent",
    "TiradentesAgent": "ReporterAgent",
    "CeuciAgent": "PredictiveAgent",
    "DrummondAgent": "CommunicationAgent",
    "ObaluaieAgent": "CorruptionDetectorAgent",
    "AbaporuAgent": "MasterAgent",
    "AyrtonSennaAgent": "SemanticRouter",
    "NanaAgent": "ContextMemoryAgent",
    "SantosDumontAgent": "EducatorAgent",
}

# Agent name to class name mapping (for get_agent function)
_AGENT_NAME_TO_CLASS = {
    "zumbi": "InvestigatorAgent",
    "anita": "AnalystAgent",
    "tiradentes": "ReporterAgent",
    "ayrton_senna": "SemanticRouter",
    "bonifacio": "BonifacioAgent",
    "maria_quiteria": "MariaQuiteriaAgent",
    "machado": "MachadoAgent",
    "oxossi": "OxossiAgent",
    "lampiao": "LampiaoAgent",
    "oscar_niemeyer": "OscarNiemeyerAgent",
    "abaporu": "MasterAgent",
    "nana": "ContextMemoryAgent",
    "drummond": "CommunicationAgent",
    "ceuci": "PredictiveAgent",
    "obaluaie": "CorruptionDetectorAgent",
    "dandara": "DandaraAgent",
    "santos_dumont": "EducatorAgent",
}

# Cache for imported modules
_IMPORT_CACHE: dict[str, Any] = {}

# Cache for agent instances
_AGENT_INSTANCE_CACHE: dict[str, Any] = {}


def get_agent(agent_name: str) -> Any | None:
    """
    Get an agent instance by its name.

    Args:
        agent_name: The agent name (e.g., "zumbi", "anita", "machado")

    Returns:
        Agent instance or None if not found
    """
    # Normalize agent name
    normalized_name = agent_name.lower().strip()

    # Return from cache if already instantiated
    if normalized_name in _AGENT_INSTANCE_CACHE:
        return _AGENT_INSTANCE_CACHE[normalized_name]

    # Get class name from mapping
    class_name = _AGENT_NAME_TO_CLASS.get(normalized_name)
    if not class_name:
        return None

    try:
        # Get the agent class using lazy loading
        agent_class = __getattr__(class_name)
        # Create instance
        agent_instance = agent_class()
        # Cache and return
        _AGENT_INSTANCE_CACHE[normalized_name] = agent_instance
        return agent_instance
    except (AttributeError, ImportError):
        return None


def __getattr__(name: str):
    """
    Lazy import implementation using __getattr__.

    This function is called when an attribute is not found in the module.
    It dynamically imports the requested agent only when needed.
    """
    # Check if it's an alias first
    if name in _ALIASES:
        actual_name = _ALIASES[name]
        return __getattr__(actual_name)  # Recursively get the actual class

    # Check if it's in our lazy imports
    if name not in _LAZY_IMPORTS:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    # Return from cache if already imported
    if name in _IMPORT_CACHE:
        return _IMPORT_CACHE[name]

    # Import the module and get the attribute
    module_name, attr_name = _LAZY_IMPORTS[name]

    # Import the module
    if module_name not in sys.modules:
        __import__(module_name)

    module = sys.modules[module_name]
    obj = getattr(module, attr_name)

    # Cache it
    _IMPORT_CACHE[name] = obj

    return obj


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    base_attrs = [
        "BaseAgent",
        "ReflectiveAgent",
        "AgentContext",
        "AgentMessage",
        "AgentResponse",
    ]
    lazy_attrs = list(_LAZY_IMPORTS.keys())
    aliases = list(_ALIASES.keys())

    return base_attrs + lazy_attrs + aliases


__all__ = [
    # Base classes (always imported)
    "BaseAgent",
    "ReflectiveAgent",
    "AgentContext",
    "AgentMessage",
    "AgentResponse",
    # Master Agent (lazy)
    "MasterAgent",
    "InvestigationPlan",
    "InvestigationResult",
    # Specialized Agents (lazy)
    "InvestigatorAgent",
    "AnalystAgent",
    "ReporterAgent",
    "SemanticRouter",
    "BonifacioAgent",
    "MariaQuiteriaAgent",
    "OscarNiemeyerAgent",
    "LampiaoAgent",
    "DandaraAgent",
    "MachadoAgent",
    "CorruptionDetectorAgent",
    "OxossiAgent",
    "PredictiveAgent",
    "CommunicationAgent",
    "EducatorAgent",
    # Agent aliases (lazy)
    "ZumbiAgent",
    "AnitaAgent",
    "TiradentesAgent",
    "CeuciAgent",
    "DrummondAgent",
    "ObaluaieAgent",
    "AbaporuAgent",
    "AyrtonSennaAgent",
    "NanaAgent",
    "SantosDumontAgent",
    # Memory Agent (lazy)
    "ContextMemoryAgent",
    "MemoryEntry",
    "EpisodicMemory",
    "SemanticMemory",
    "ConversationMemory",
    # Agent Pool (lazy)
    "agent_pool",
    "get_agent_pool",
    # Agent getter function
    "get_agent",
]
