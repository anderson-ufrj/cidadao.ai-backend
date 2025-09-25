"""
Module: agents
Description: Multi-agent system for Cidadao.AI
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from .deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    BaseAgent,
    ReflectiveAgent,
)
from .nana import (
    ContextMemoryAgent,
    ConversationMemory,
    EpisodicMemory,
    MemoryEntry,
    SemanticMemory,
)
from .abaporu import (
    InvestigationPlan,
    InvestigationResult,
    MasterAgent,
)
from .zumbi import InvestigatorAgent
from .anita import AnalystAgent
from .tiradentes import ReporterAgent

# Agent aliases for new naming convention
ZumbiAgent = InvestigatorAgent
AnitaAgent = AnalystAgent
TiradentesAgent = ReporterAgent
from .ayrton_senna import SemanticRouter
from .bonifacio import BonifacioAgent
from .maria_quiteria import MariaQuiteriaAgent
# Commenting out drummond import to avoid import-time issues on HuggingFace Spaces
# from .drummond import CommunicationAgent
from .agent_pool import agent_pool, get_agent_pool

__all__ = [
    # Base classes
    "BaseAgent",
    "ReflectiveAgent",
    "AgentContext",
    "AgentMessage", 
    "AgentResponse",
    # Master Agent
    "MasterAgent",
    "InvestigationPlan",
    "InvestigationResult",
    # Specialized Agents
    "InvestigatorAgent",
    "AnalystAgent",
    "ReporterAgent",
    "SemanticRouter",
    "BonifacioAgent",
    "MariaQuiteriaAgent",
    # Agent aliases
    "ZumbiAgent",
    "AnitaAgent", 
    "TiradentesAgent",
    # "CommunicationAgent",  # Commented out to avoid import issues
    # Memory Agent
    "ContextMemoryAgent",
    "MemoryEntry",
    "EpisodicMemory",
    "SemanticMemory",
    "ConversationMemory",
    # Agent Pool
    "agent_pool",
    "get_agent_pool",
]