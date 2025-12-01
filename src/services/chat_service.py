"""
Chat service for managing conversations and intent detection
"""

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from src.agents import BaseAgent
from src.core import get_logger
from src.services.agent_routing import get_agent_for_intent as centralized_get_agent
from src.services.cache_service import cache_service
from src.utils.organization_mapping import get_organization_mapper

logger = get_logger(__name__)


class IntentType(Enum):
    """Types of user intents

    Task-specific intents:
    - INVESTIGATE: Request investigation of contracts/expenses
    - ANALYZE: Request pattern/anomaly analysis
    - REPORT: Request report generation
    - STATUS: Check investigation status

    Conversational intents:
    - GREETING: Initial greeting/salutation
    - CONVERSATION: General conversation
    - HELP_REQUEST: Request for help/guidance
    - ABOUT_SYSTEM: Questions about the system
    - SMALLTALK: Casual conversation
    - THANKS: Gratitude expressions
    - GOODBYE: Farewell expressions

    Other:
    - QUESTION: General questions
    - HELP: Help (legacy, use HELP_REQUEST)
    - UNKNOWN: Could not determine intent
    """

    # Task-specific intents
    INVESTIGATE = "investigate"
    ANALYZE = "analyze"
    REPORT = "report"
    STATUS = "status"

    # Specialized agent intents
    TEXT_ANALYSIS = "text_analysis"  # For Machado
    LEGAL_COMPLIANCE = "legal_compliance"  # For Bonifácio
    SECURITY_AUDIT = "security_audit"  # For Maria Quitéria
    VISUALIZATION = "visualization"  # For Oscar Niemeyer
    STATISTICAL = "statistical"  # For Anita
    FRAUD_DETECTION = "fraud_detection"  # For Oxóssi

    # Conversational intents
    GREETING = "greeting"
    CONVERSATION = "conversation"
    HELP_REQUEST = "help_request"
    ABOUT_SYSTEM = "about_system"
    SMALLTALK = "smalltalk"
    THANKS = "thanks"
    GOODBYE = "goodbye"

    # General
    QUESTION = "question"
    HELP = "help"  # Legacy, keeping for backward compatibility
    UNKNOWN = "unknown"

    # Data-related intents (used by chat routing)
    DATA = "data"  # Generic data request
    SEARCH = "search"  # Search/query data


@dataclass
class Intent:
    """Detected user intent"""

    type: IntentType
    entities: dict[str, Any]
    confidence: float
    suggested_agent: str

    def dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "entities": self.entities,
            "confidence": self.confidence,
            "suggested_agent": self.suggested_agent,
        }


@dataclass
class ChatSession:
    """Chat session data"""

    id: str
    user_id: str | None
    created_at: datetime
    last_activity: datetime
    current_investigation_id: str | None = None
    context: dict[str, Any] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "current_investigation_id": self.current_investigation_id,
            "context": self.context or {},
        }


class IntentDetector:
    """Detects user intent from messages"""

    def __init__(self) -> None:
        # Intent patterns in Portuguese
        self.patterns = {
            IntentType.INVESTIGATE: [
                r"investigar?\s+(\w+)",
                r"analis[ae]r?\s+contratos",
                r"verificar?\s+gastos",
                r"procurar?\s+irregularidades",
                r"detectar?\s+anomalias",
                r"buscar?\s+problemas",
                # Data listing/viewing queries
                r"listar?\s+contratos",
                r"mostrar?\s+contratos",
                r"ver\s+contratos",
                r"quais\s+contratos",
                r"contratos\s+d[oa]",
                r"gastos\s+d[oa]",
                r"despesas\s+d[oa]",
                r"licitac[õo]es\s+d[oa]",
                r"fornecedores?\s+d[oa]",
                r"listar?\s+gastos",
                r"mostrar?\s+gastos",
                r"ver\s+gastos",
                r"listar?\s+despesas",
                r"mostrar?\s+despesas",
                r"ver\s+despesas",
                r"dados\s+d[oa]",
                r"informa[çc][õo]es\s+d[oa]",
            ],
            IntentType.ANALYZE: [
                r"anomalias?\s+",
                r"padr[õo]es?\s+suspeitos",
                r"gastos?\s+excessivos",
                r"fornecedores?\s+concentrados",
                r"an[áa]lise\s+de",
                r"mostrar?\s+gr[áa]ficos",
            ],
            IntentType.REPORT: [
                r"gerar?\s+relat[óo]rio",
                r"documento\s+",
                r"resumo\s+",
                r"exportar?\s+dados",
                r"baixar?\s+",
                r"pdf\s+",
            ],
            IntentType.STATUS: [
                r"status\s+",
                r"progresso\s+",
                r"como\s+est[áa]",
                r"andamento\s+",
            ],
            IntentType.TEXT_ANALYSIS: [
                r"analis[ae]r?\s+texto",
                r"analis[ae]r?\s+contrato",
                r"verificar?\s+cl[áa]usulas",
                r"ler\s+contrato",
                r"entender\s+documento",
                r"interpretar\s+",
                r"analis[ae]r?\s+documento",
                r"revisar?\s+texto",
                r"extrair?\s+informa[çc][õo]es",
            ],
            IntentType.LEGAL_COMPLIANCE: [
                r"conformidade\s+legal",
                r"legalidade\s+",
                r"lei\s+\d",
                r"verificar?\s+lei",
                r"est[áa]\s+legal",
                r"conforme\s+a\s+lei",
                r"legisla[çc][ãa]o",
                r"normas?\s+legais",
                r"regulamenta[çc][ãa]o",
            ],
            IntentType.SECURITY_AUDIT: [
                r"auditoria\s+de\s+seguran[çc]a",
                r"verificar?\s+seguran[çc]a",
                r"vulne?r",
                r"seguran[çc]a\s+dos\s+dados",
                r"ataques?\s+",
                r"brechas?\s+",
                r"riscos?\s+de\s+seguran[çc]a",
                r"an[áa]lise\s+de\s+seguran[çc]a",
            ],
            IntentType.VISUALIZATION: [
                r"gr[áa]ficos?",
                r"visualiza[çc][ãa]o",
                r"criar?\s+gr[áa]fico",
                r"mostrar?\s+gr[áa]fico",
                r"plotar",
                r"desenhar\s+",
                r"dashboard",
                r"representa[çc][ãa]o\s+visual",
            ],
            IntentType.STATISTICAL: [
                r"estat[íi]sticas?",
                r"m[ée]dia",
                r"mediana",
                r"desvio\s+padr[ãa]o",
                r"correla[çc][ãa]o",
                r"distribui[çc][ãa]o",
                r"an[áa]lise\s+estat[íi]stica",
                r"percentual",
                r"propor[çc][ãa]o",
            ],
            IntentType.FRAUD_DETECTION: [
                r"fraude",
                r"fraudulento",
                r"esquema",
                r"corrup[çc][ãa]o",
                r"superfaturamento",
                r"favorecimento",
                r"direcionamento",
                r"cartel",
                r"conluio",
            ],
            IntentType.HELP: [
                r"como\s+funciona",
                r"ajuda",
                r"help",
                r"o\s+que\s+[ée]",
                r"explicar?",
            ],
            IntentType.GREETING: [
                r"ol[áa]",
                r"oi",
                r"bom\s+dia",
                r"boa\s+tarde",
                r"boa\s+noite",
                r"e\s+a[íi]",
                r"tudo\s+bem",
                r"como\s+vai",
            ],
            IntentType.CONVERSATION: [
                r"conversar",
                r"falar\s+sobre",
                r"me\s+conte",
                r"vamos\s+conversar",
                r"quero\s+saber",
                r"pode\s+me\s+falar",
            ],
            IntentType.HELP_REQUEST: [
                r"preciso\s+de\s+ajuda",
                r"me\s+ajud[ae]",
                r"pode\s+ajudar",
                r"n[ãa]o\s+sei\s+como",
                r"n[ãa]o\s+entendi",
                r"como\s+fa[çc]o",
            ],
            IntentType.ABOUT_SYSTEM: [
                r"o\s+que\s+[ée]\s+o\s+cidad[ãa]o",
                r"como\s+voc[êe]\s+funciona",
                r"quem\s+[ée]\s+voc[êe]",
                r"para\s+que\s+serve",
                r"o\s+que\s+voc[êe]\s+faz",
                r"qual\s+sua\s+fun[çc][ãa]o",
            ],
            IntentType.SMALLTALK: [
                r"como\s+est[áa]\s+o\s+tempo",
                r"voc[êe]\s+gosta",
                r"qual\s+sua\s+opini[ãa]o",
                r"o\s+que\s+acha",
                r"conte\s+uma\s+hist[óo]ria",
                r"voc[êe]\s+[ée]\s+brasileiro",
            ],
            IntentType.THANKS: [
                r"obrigad[oa]",
                r"muito\s+obrigad[oa]",
                r"valeu",
                r"gratid[ãa]o",
                r"agradec[çc]o",
                r"foi\s+[úu]til",
            ],
            IntentType.GOODBYE: [
                r"tchau",
                r"at[ée]\s+logo",
                r"at[ée]\s+mais",
                r"adeus",
                r"falou",
                r"tenho\s+que\s+ir",
                r"at[ée]\s+breve",
            ],
        }

        # Organ mapping
        self.organ_map = {
            "saúde": {"name": "Ministério da Saúde", "code": "26000"},
            "saude": {"name": "Ministério da Saúde", "code": "26000"},
            "educação": {"name": "Ministério da Educação", "code": "25000"},
            "educacao": {"name": "Ministério da Educação", "code": "25000"},
            "presidência": {"name": "Presidência da República", "code": "20000"},
            "presidencia": {"name": "Presidência da República", "code": "20000"},
            "justiça": {"name": "Ministério da Justiça", "code": "30000"},
            "justica": {"name": "Ministério da Justiça", "code": "30000"},
            "agricultura": {"name": "Ministério da Agricultura", "code": "22000"},
        }

    async def detect(self, message: str) -> Intent:
        """Detect intent from user message"""
        message_lower = message.lower().strip()

        # Extract entities
        entities = {
            "original_message": message,
            "organs": self._extract_organs(message_lower),
            "period": self._extract_period(message_lower),
            "values": self._extract_values(message_lower),
        }

        # Check each intent pattern
        best_match = None
        best_confidence = 0.0

        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    # Calculate confidence based on match quality
                    confidence = 0.8
                    if len(match.groups()) > 0:
                        confidence = 0.9

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = intent_type

        # Default to QUESTION if no match
        if not best_match:
            best_match = IntentType.QUESTION
            best_confidence = 0.5

        # Determine suggested agent
        suggested_agent = self._get_agent_for_intent(best_match)

        return Intent(
            type=best_match,
            entities=entities,
            confidence=best_confidence,
            suggested_agent=suggested_agent,
        )

    def _extract_organs(self, text: str) -> list[dict[str, str]]:
        """Extract government organ mentions using advanced mapper"""
        mapper = get_organization_mapper()
        organizations = mapper.extract_organizations_from_text(text)

        # Convert to expected format with code included
        return [
            {
                "name": org["name"],
                "code": org["code"],
                "matched_text": org["matched_text"],
            }
            for org in organizations
        ]

    def _extract_period(self, text: str) -> dict[str, str] | None:
        """Extract time period mentions"""
        # Look for year patterns
        year_match = re.search(r"20\d{2}", text)
        if year_match:
            year = year_match.group()
            return {"year": year, "type": "year"}

        # Look for month patterns
        months = {
            "janeiro": 1,
            "fevereiro": 2,
            "março": 3,
            "marco": 3,
            "abril": 4,
            "maio": 5,
            "junho": 6,
            "julho": 7,
            "agosto": 8,
            "setembro": 9,
            "outubro": 10,
            "novembro": 11,
            "dezembro": 12,
        }

        for month_name, month_num in months.items():
            if month_name in text:
                return {"month": month_num, "type": "month"}

        # Look for relative periods
        if "último" in text or "ultimo" in text:
            if "mês" in text or "mes" in text:
                return {"relative": "last_month", "type": "relative"}
            if "ano" in text:
                return {"relative": "last_year", "type": "relative"}

        return None

    def _extract_values(self, text: str) -> list[float]:
        """Extract monetary values"""
        values = []

        # Pattern for Brazilian currency format
        patterns = [
            r"R\$\s*([\d.,]+)",
            r"([\d.,]+)\s*reais",
            r"([\d.,]+)\s*milhões",
            r"([\d.,]+)\s*mil",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    # Clean and convert
                    value_str = match.replace(".", "").replace(",", ".")
                    value = float(value_str)

                    # Adjust for units
                    if "milhões" in text:
                        value *= 1_000_000
                    elif "mil" in text:
                        value *= 1_000

                    values.append(value)
                except (ValueError, AttributeError):
                    # Ignore invalid numeric formats
                    continue

        return values

    def _get_agent_for_intent(self, intent_type: IntentType) -> str:
        """Get the best agent for handling this intent.

        Uses centralized agent routing from agent_routing module
        for consistent behavior across all endpoints.

        Routing strategy:
        - Conversational intents -> Drummond (conversational AI)
        - Task-specific intents -> Specialized agents
        - Unknown intents -> Abaporu (master orchestrator)
        """
        # Use centralized routing function (single source of truth)
        return centralized_get_agent(intent_type.value)


class ChatService:
    """Service for managing chat sessions and conversations"""

    def __init__(self) -> None:
        self.cache = cache_service
        self.sessions: dict[str, ChatSession] = {}
        self.messages: dict[str, list[dict]] = defaultdict(list)

        # Initialize agents lazily to avoid import-time errors
        self.agents = None
        self._agents_initialized = False

    async def get_or_create_session(
        self, session_id: str, user_id: str | None = None
    ) -> ChatSession:
        """Get existing session or create new one"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.last_activity = datetime.now(UTC)
            return session

        # Create new session
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            created_at=datetime.now(UTC),
            last_activity=datetime.now(UTC),
            context={},
        )

        self.sessions[session_id] = session
        return session

    async def get_session(self, session_id: str) -> ChatSession | None:
        """Get session by ID"""
        return self.sessions.get(session_id)

    async def save_message(
        self, session_id: str, role: str, content: str, agent_id: str | None = None
    ) -> None:
        """Save message to session history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(UTC).isoformat(),
            "agent_id": agent_id,
        }

        self.messages[session_id].append(message)

        # Update session activity
        if session_id in self.sessions:
            self.sessions[session_id].last_activity = datetime.now(UTC)

    async def get_session_messages(
        self, session_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get messages for a session"""
        messages = self.messages.get(session_id, [])
        return messages[-limit:] if len(messages) > limit else messages

    async def clear_session(self, session_id: str) -> None:
        """Clear session data"""
        self.sessions.pop(session_id, None)
        self.messages.pop(session_id, None)

    async def get_agent_for_intent(self, intent: Intent) -> BaseAgent:
        """Get the appropriate agent for an intent"""
        self._ensure_agents_initialized()
        agent_id = intent.suggested_agent
        if self.agents:
            return self.agents.get(agent_id, self.agents.get("abaporu"))
        return None

    async def update_session_investigation(
        self, session_id: str, investigation_id: str
    ) -> None:
        """Update session with current investigation"""
        if session_id in self.sessions:
            self.sessions[session_id].current_investigation_id = investigation_id
            self.sessions[session_id].last_activity = datetime.now(UTC)

    def _ensure_agents_initialized(self) -> None:
        """Initialize agents on first use (lazy loading)"""
        if self._agents_initialized:
            return

        try:
            # Import here to avoid circular imports
            from src.agents import (
                AnalystAgent,
                CommunicationAgent,
                InvestigatorAgent,
                ReporterAgent,
            )

            # Create agent instances (MasterAgent requires special initialization)
            # For chat service, we use the simpler agents that don't require
            # external dependencies like maritaca_client
            agents = {
                "zumbi": InvestigatorAgent(),
                "anita": AnalystAgent(),
                "tiradentes": ReporterAgent(),
                "drummond": CommunicationAgent(),
            }

            # Use Drummond as the default/fallback agent (abaporu role)
            agents["abaporu"] = agents["drummond"]

            # Add agent_id attribute to each agent
            for agent_id, agent in agents.items():
                agent.agent_id = agent_id

            self.agents = agents
            self._agents_initialized = True
            logger.info(f"Chat service agents initialized: {list(agents.keys())}")

        except Exception as e:
            logger.error(f"Failed to initialize agents: {type(e).__name__}: {e}")
            import traceback

            logger.error(traceback.format_exc())
            # Create empty agents dict to prevent errors
            self.agents = {}
            self._agents_initialized = True
