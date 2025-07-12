"""
Module: agents
Description: Multi-agent system for Cidadao.AI
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from .base_agent import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    BaseAgent,
    ReflectiveAgent,
)
from .context_memory_agent import (
    ContextMemoryAgent,
    ConversationMemory,
    EpisodicMemory,
    MemoryEntry,
    SemanticMemory,
)
from .master_agent import (
    InvestigationPlan,
    InvestigationResult,
    MasterAgent,
)
from .investigator_agent import InvestigatorAgent
from .analyst_agent import AnalystAgent
from .reporter_agent import ReporterAgent

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
    # Memory Agent
    "ContextMemoryAgent",
    "MemoryEntry",
    "EpisodicMemory",
    "SemanticMemory",
    "ConversationMemory",
]