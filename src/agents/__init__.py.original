"""
Module: agents
Description: Multi-agent system for Cidadao.AI
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from .abaporu import InvestigationPlan, InvestigationResult, MasterAgent
from .simple_agent_pool import agent_pool, get_agent_pool
from .anita import AnalystAgent
from .ayrton_senna import SemanticRouter
from .bonifacio import BonifacioAgent
from .ceuci import PredictiveAgent
from .dandara import DandaraAgent
from .deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    BaseAgent,
    ReflectiveAgent,
)
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
from .tiradentes import ReporterAgent
from .zumbi import InvestigatorAgent

# Agent aliases for new naming convention
ZumbiAgent = InvestigatorAgent
AnitaAgent = AnalystAgent
TiradentesAgent = ReporterAgent
CeuciAgent = PredictiveAgent
DrummondAgent = CommunicationAgent
ObaluaieAgent = CorruptionDetectorAgent
AbaporuAgent = MasterAgent
AyrtonSennaAgent = SemanticRouter
NanaAgent = ContextMemoryAgent

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
    "OscarNiemeyerAgent",
    "LampiaoAgent",
    "DandaraAgent",
    "MachadoAgent",
    "CorruptionDetectorAgent",
    "OxossiAgent",
    # Agent aliases
    "ZumbiAgent",
    "AnitaAgent",
    "TiradentesAgent",
    "CommunicationAgent",
    "DrummondAgent",
    "CeuciAgent",
    "PredictiveAgent",
    "ObaluaieAgent",
    "AbaporuAgent",
    "AyrtonSennaAgent",
    "NanaAgent",
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
