"""
Centralized agent routing module.

This module provides a single source of truth for agent selection logic,
ensuring consistent behavior across all chat endpoints.

Architecture:
- When no agent_id is specified: Abaporu (master orchestrator) decides
- When agent_id is specified: Use the requested agent directly
- Abaporu delegates to specialized agents based on intent analysis
"""

from enum import Enum
from typing import Any

from src.core import get_logger

logger = get_logger(__name__)


class AgentRole(Enum):
    """Agent roles and their responsibilities."""

    ORCHESTRATOR = "orchestrator"  # Abaporu - coordinates complex tasks
    INVESTIGATOR = "investigator"  # Zumbi - detects anomalies
    ANALYST = "analyst"  # Anita - analyzes patterns
    REPORTER = "reporter"  # Tiradentes - generates reports
    COMMUNICATOR = "communicator"  # Drummond - handles conversation
    TEXT_ANALYST = "text_analyst"  # Machado - analyzes documents
    LEGAL = "legal"  # Bonifácio - legal compliance
    SECURITY = "security"  # Maria Quitéria - security audit
    DATA_HUNTER = "data_hunter"  # Oxóssi - searches data
    VISUALIZER = "visualizer"  # Oscar Niemeyer - creates visualizations
    SOCIAL_EQUITY = "social_equity"  # Dandara - social justice analysis


# Canonical agent registry with metadata
AGENT_REGISTRY: dict[str, dict[str, Any]] = {
    "abaporu": {
        "name": "Abaporu",
        "full_name": "Abaporu",
        "role": AgentRole.ORCHESTRATOR,
        "description": "Orquestrador Master - coordena investigações complexas",
        "avatar": "🎨",
        "is_orchestrator": True,
    },
    "zumbi": {
        "name": "Zumbi dos Palmares",
        "full_name": "Zumbi dos Palmares",
        "role": AgentRole.INVESTIGATOR,
        "description": "Investigador - detecta anomalias e irregularidades",
        "avatar": "🔍",
        "is_orchestrator": False,
    },
    "anita": {
        "name": "Anita Garibaldi",
        "full_name": "Anita Garibaldi",
        "role": AgentRole.ANALYST,
        "description": "Analista - analisa padrões e tendências estatísticas",
        "avatar": "📊",
        "is_orchestrator": False,
    },
    "tiradentes": {
        "name": "Tiradentes",
        "full_name": "Joaquim José da Silva Xavier",
        "role": AgentRole.REPORTER,
        "description": "Relator - gera relatórios detalhados",
        "avatar": "📝",
        "is_orchestrator": False,
    },
    "drummond": {
        "name": "Carlos Drummond de Andrade",
        "full_name": "Carlos Drummond de Andrade",
        "role": AgentRole.COMMUNICATOR,
        "description": "Comunicador - interface conversacional amigável",
        "avatar": "💬",
        "is_orchestrator": False,
    },
    "machado": {
        "name": "Machado de Assis",
        "full_name": "Joaquim Maria Machado de Assis",
        "role": AgentRole.TEXT_ANALYST,
        "description": "Analista Textual - analisa documentos e contratos",
        "avatar": "📚",
        "is_orchestrator": False,
    },
    "bonifacio": {
        "name": "José Bonifácio",
        "full_name": "José Bonifácio de Andrada e Silva",
        "role": AgentRole.LEGAL,
        "description": "Especialista Legal - verifica conformidade com leis",
        "avatar": "⚖️",
        "is_orchestrator": False,
    },
    "maria_quiteria": {
        "name": "Maria Quitéria",
        "full_name": "Maria Quitéria de Jesus",
        "role": AgentRole.SECURITY,
        "description": "Auditora de Segurança - análise de vulnerabilidades",
        "avatar": "🛡️",
        "is_orchestrator": False,
    },
    "oxossi": {
        "name": "Oxóssi",
        "full_name": "Oxóssi",
        "role": AgentRole.DATA_HUNTER,
        "description": "Caçador de Dados - busca informações em múltiplas fontes",
        "avatar": "🏹",
        "is_orchestrator": False,
    },
    "oscar_niemeyer": {
        "name": "Oscar Niemeyer",
        "full_name": "Oscar Ribeiro de Almeida Niemeyer Soares Filho",
        "role": AgentRole.VISUALIZER,
        "description": "Visualizador - cria gráficos e dashboards",
        "avatar": "📐",
        "is_orchestrator": False,
    },
    "dandara": {
        "name": "Dandara",
        "full_name": "Dandara dos Palmares",
        "role": AgentRole.SOCIAL_EQUITY,
        "description": "Justiça Social - avalia equidade e inclusão",
        "avatar": "✊",
        "is_orchestrator": False,
    },
    "lampiao": {
        "name": "Lampião",
        "full_name": "Virgulino Ferreira da Silva",
        "role": AgentRole.INVESTIGATOR,
        "description": "Investigador Regional - foco em dados regionais",
        "avatar": "🌵",
        "is_orchestrator": False,
    },
    "nana": {
        "name": "Nanã",
        "full_name": "Nanã",
        "role": AgentRole.ORCHESTRATOR,
        "description": "Memória - gerencia contexto e histórico",
        "avatar": "🌙",
        "is_orchestrator": False,
    },
    "ceuci": {
        "name": "Ceuci",
        "full_name": "Ceuci",
        "role": AgentRole.ANALYST,
        "description": "Preditivo - análises preditivas e ETL",
        "avatar": "🔮",
        "is_orchestrator": False,
    },
    "obaluaie": {
        "name": "Obaluaiê",
        "full_name": "Obaluaiê",
        "role": AgentRole.INVESTIGATOR,
        "description": "Detector de Corrupção - identifica padrões de corrupção",
        "avatar": "🔥",
        "is_orchestrator": False,
    },
    "senna": {
        "name": "Ayrton Senna",
        "full_name": "Ayrton Senna da Silva",
        "role": AgentRole.ORCHESTRATOR,
        "description": "Roteador Semântico - direciona consultas rapidamente",
        "avatar": "🏎️",
        "is_orchestrator": False,
    },
}

# Default orchestrator when no agent is specified
DEFAULT_ORCHESTRATOR = "abaporu"

# Fallback agent for conversational/unknown intents
FALLBACK_CONVERSATIONAL = "drummond"

# Minimum confidence threshold for intent-based routing
MIN_CONFIDENCE_THRESHOLD = 0.6


def get_agent_for_intent(intent_type: str, intent_confidence: float = 0.5) -> str:
    """
    Get the most appropriate agent for a given intent type.

    This is the SINGLE SOURCE OF TRUTH for intent-to-agent mapping.
    All endpoints should use this function for consistent routing.

    Args:
        intent_type: The detected intent type (e.g., "investigate", "question")
        intent_confidence: Confidence score of the intent detection

    Returns:
        Agent ID string (e.g., "abaporu", "zumbi", "drummond")
    """
    # Normalize intent type
    intent_lower = intent_type.lower() if intent_type else "unknown"

    # Task-specific intents -> Specialized agents
    # But investigations go through Abaporu for orchestration
    task_mapping = {
        # Investigation tasks -> Abaporu orchestrates, may delegate to Zumbi
        "investigate": "abaporu",
        "contract_anomaly_detection": "abaporu",
        "supplier_investigation": "abaporu",
        "corruption_indicators": "abaporu",
        "budget_analysis": "abaporu",
        "health_budget_analysis": "abaporu",
        "education_performance": "abaporu",
        # Analysis tasks -> Anita (statistical analyst)
        "analyze": "anita",
        "statistical": "anita",
        # Report generation -> Tiradentes
        "report": "tiradentes",
        # Status checks -> Abaporu (knows overall state)
        "status": "abaporu",
        # Specialized agents for specific tasks
        "text_analysis": "machado",
        "legal_compliance": "bonifacio",
        "security_audit": "maria_quiteria",
        "visualization": "oscar_niemeyer",
        "fraud_detection": "oxossi",
        # Data hunting -> Oxóssi
        "data": "oxossi",
        "search": "oxossi",
    }

    # Conversational intents -> Drummond (friendly communicator)
    conversational_mapping = {
        "greeting": "drummond",
        "conversation": "drummond",
        "help_request": "drummond",
        "help": "drummond",
        "about_system": "drummond",
        "smalltalk": "drummond",
        "thanks": "drummond",
        "goodbye": "drummond",
        "question": "drummond",  # General questions -> Drummond first
    }

    # Check task mapping first (higher priority)
    if intent_lower in task_mapping:
        agent = task_mapping[intent_lower]
        logger.debug(f"Intent '{intent_lower}' -> task agent '{agent}'")
        return agent

    # Check conversational mapping
    if intent_lower in conversational_mapping:
        agent = conversational_mapping[intent_lower]
        logger.debug(f"Intent '{intent_lower}' -> conversational agent '{agent}'")
        return agent

    # Unknown intent with low confidence -> Drummond (friendly fallback)
    if intent_confidence < MIN_CONFIDENCE_THRESHOLD:
        logger.debug(
            f"Low confidence ({intent_confidence}) for '{intent_lower}' -> drummond"
        )
        return FALLBACK_CONVERSATIONAL

    # Unknown intent with higher confidence -> Abaporu decides
    logger.debug(f"Unknown intent '{intent_lower}' -> abaporu (orchestrator)")
    return DEFAULT_ORCHESTRATOR


def resolve_agent_id(
    requested_agent_id: str | None,
    intent_type: str | None = None,
    intent_confidence: float = 0.5,
) -> tuple[str, str]:
    """
    Resolve the final agent ID to use, considering user preference and intent.

    This is the main entry point for agent selection across all endpoints.

    Args:
        requested_agent_id: Agent ID explicitly requested by user/frontend (can be None)
        intent_type: Detected intent type (used when no agent is requested)
        intent_confidence: Confidence of intent detection

    Returns:
        Tuple of (agent_id, agent_name)
    """
    # If user explicitly requested an agent, use it (if valid)
    if requested_agent_id:
        agent_id = requested_agent_id.lower()
        if agent_id in AGENT_REGISTRY:
            agent_info = AGENT_REGISTRY[agent_id]
            logger.info(f"Using explicitly requested agent: {agent_id}")
            return agent_id, agent_info["name"]

        logger.warning(
            f"Requested agent '{requested_agent_id}' not found, using default"
        )

    # No agent specified -> Use intent-based routing
    if intent_type:
        agent_id = get_agent_for_intent(intent_type, intent_confidence)
    else:
        # No intent either -> Default orchestrator
        agent_id = DEFAULT_ORCHESTRATOR

    agent_info = AGENT_REGISTRY.get(agent_id, AGENT_REGISTRY[DEFAULT_ORCHESTRATOR])
    logger.info(
        f"Auto-selected agent: {agent_id} (intent: {intent_type}, confidence: {intent_confidence:.2f})"
    )

    return agent_id, agent_info["name"]


def get_agent_info(agent_id: str) -> dict[str, Any] | None:
    """Get full agent information by ID."""
    return AGENT_REGISTRY.get(agent_id.lower())


def list_available_agents() -> list[dict[str, Any]]:
    """List all available agents with their metadata."""
    return [
        {
            "id": agent_id,
            "name": info["name"],
            "avatar": info["avatar"],
            "role": info["role"].value,
            "description": info["description"],
            "is_orchestrator": info["is_orchestrator"],
        }
        for agent_id, info in AGENT_REGISTRY.items()
    ]


def is_valid_agent(agent_id: str) -> bool:
    """Check if an agent ID is valid."""
    return agent_id.lower() in AGENT_REGISTRY if agent_id else False
