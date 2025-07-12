"""Memory system for Cidadão.AI agents.

This module provides memory management capabilities for AI agents including:
- Episodic memory for specific events and investigations
- Semantic memory for knowledge and patterns
- Conversational memory for chat contexts

Status: Stub implementation - Full implementation planned for database integration phase.
"""

from .base import BaseMemory
from .episodic import EpisodicMemory
from .semantic import SemanticMemory
from .conversational import ConversationalMemory

__all__ = [
    "BaseMemory",
    "EpisodicMemory", 
    "SemanticMemory",
    "ConversationalMemory"
]