"""
Chat service for managing conversations and intent detection
"""

import re
from dataclasses import dataclass
from datetime import UTC, datetime


def _utcnow() -> datetime:
    """Naive UTC datetime compatible with 'timestamp without time zone' columns."""
    return datetime.now(UTC).replace(tzinfo=None)
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



class IntentDetector:
    """Detects user intent from messages"""

    def __init__(self) -> None:
        # Intent patterns in Portuguese - EXPANDED VERSION (Dec 2025)
        # Based on production test results showing 87% "unknown" classification
        self.patterns = {
            IntentType.INVESTIGATE: [
                # Core investigation verbs
                r"investigar?\b",
                r"investiga[çc][ãa]o",
                r"analis[ae]r?\s+contratos",
                r"verificar?\s+gastos",
                r"procurar?\s+irregularidades",
                r"detectar?\s+anomalias",
                r"buscar?\s+problemas",
                r"fiscalizar?\b",
                r"auditar?\b",
                # Contract-related (high priority)
                r"\bcontratos?\b",
                r"\blicita[çc][ãa]o",
                r"\blicita[çc][õo]es",
                r"\bpreg[ãa]o\b",
                r"\bdispensa\b.*licita",
                r"\binexigibilidade\b",
                # Data listing/viewing queries
                r"listar?\s+\w+",
                r"mostrar?\s+\w+",
                r"ver\s+\w+",
                r"quais\s+\w+",
                r"encontrar?\s+\w+",
                r"pesquisar?\s+\w+",
                r"buscar?\s+\w+",
                r"procurar?\s+\w+",
                # Specific targets
                r"contratos\s+d[oae]",
                r"gastos\s+d[oae]",
                r"despesas\s+d[oae]",
                r"licitac[õo]es\s+d[oae]",
                r"fornecedores?\s+d[oae]",
                r"dados\s+d[oae]",
                r"informa[çc][õo]es\s+d[oae]",
                # Government entities (broad)
                r"minist[ée]rio",
                r"[óo]rg[ãa]o",
                r"governo",
                r"prefeitura",
                r"federal",
                r"estadual",
                r"municipal",
                r"secretaria",
                # Money/values indicators
                r"acima\s+de",
                r"maior\s+que",
                r"milh[ãa]o",
                r"milh[õo]es",
                r"\bmil\b",
                r"R\$",
                r"reais",
                r"valor",
                # Temporal queries
                r"em\s+20\d{2}",
                r"[úu]ltimos?\s+\d+\s+anos?",
                r"este\s+ano",
                r"ano\s+passado",
            ],
            IntentType.ANALYZE: [
                r"anomalias?\b",
                r"padr[õo]es?\s+suspeitos?",
                r"gastos?\s+excessivos?",
                r"fornecedores?\s+concentrados?",
                r"an[áa]lise\s+de",
                r"analisar?\b",
                r"comparar?\b",
                r"compara[çc][ãa]o",
                r"mostrar?\s+gr[áa]ficos",
                r"tend[êe]ncia",
                r"evolu[çc][ãa]o",
                r"ranking",
                r"maiores?",
                r"menores?",
                r"principais?",
                r"top\s+\d+",
            ],
            IntentType.REPORT: [
                r"gerar?\s+relat[óo]rio",
                r"relat[óo]rio",
                r"documento\b",
                r"resumo\b",
                r"exportar?\s+dados",
                r"baixar?\b",
                r"download",
                r"\bpdf\b",
                r"\bcsv\b",
                r"\bexcel\b",
                r"imprimir",
            ],
            IntentType.STATUS: [
                r"\bstatus\b",
                r"progresso\b",
                r"como\s+est[áa]",
                r"andamento\b",
                r"situa[çc][ãa]o",
            ],
            IntentType.TEXT_ANALYSIS: [
                r"analis[ae]r?\s+texto",
                r"analis[ae]r?\s+contrato",
                r"verificar?\s+cl[áa]usulas",
                r"ler\s+contrato",
                r"entender\s+documento",
                r"interpretar?\b",
                r"analis[ae]r?\s+documento",
                r"revisar?\s+texto",
                r"extrair?\s+informa[çc][õo]es",
            ],
            IntentType.LEGAL_COMPLIANCE: [
                r"conformidade\s+legal",
                r"legalidade\b",
                r"\blei\s+\d",
                r"\blei\s+n",
                r"verificar?\s+lei",
                r"est[áa]\s+legal",
                r"conforme\s+a\s+lei",
                r"legisla[çc][ãa]o",
                r"normas?\s+legais?",
                r"regulamenta[çc][ãa]o",
                r"\blai\b",  # Lei de Acesso à Informação
                r"constitucional",
            ],
            IntentType.SECURITY_AUDIT: [
                r"auditoria\s+de\s+seguran[çc]a",
                r"verificar?\s+seguran[çc]a",
                r"vulne?rabilidade",
                r"seguran[çc]a\s+dos\s+dados",
                r"ataques?\b",
                r"brechas?\b",
                r"riscos?\s+de\s+seguran[çc]a",
                r"an[áa]lise\s+de\s+seguran[çc]a",
            ],
            IntentType.VISUALIZATION: [
                r"gr[áa]ficos?\b",
                r"visualiza[çc][ãa]o",
                r"criar?\s+gr[áa]fico",
                r"mostrar?\s+gr[áa]fico",
                r"plotar?\b",
                r"desenhar?\b",
                r"\bdashboard\b",
                r"representa[çc][ãa]o\s+visual",
                r"mapa\b",
                r"chart\b",
            ],
            IntentType.STATISTICAL: [
                r"estat[íi]sticas?\b",
                r"\bm[ée]dia\b",
                r"\bmediana\b",
                r"desvio\s+padr[ãa]o",
                r"correla[çc][ãa]o",
                r"distribui[çc][ãa]o",
                r"an[áa]lise\s+estat[íi]stica",
                r"percentual",
                r"propor[çc][ãa]o",
                r"\btotal\b",
                r"quantidade",
                r"quantos?",
            ],
            IntentType.FRAUD_DETECTION: [
                r"\bfraude\b",
                r"fraudulento",
                r"\besquema\b",
                r"corrup[çc][ãa]o",
                r"superfaturamento",
                r"sobrepreço",
                r"favorecimento",
                r"direcionamento",
                r"\bcartel\b",
                r"conluio",
                r"irregular",
                r"suspeito",
                r"il[íi]cito",
            ],
            IntentType.HELP: [
                r"como\s+funciona",
                r"\bajuda\b",
                r"\bhelp\b",
                r"o\s+que\s+[ée]\b",
                r"explicar?\b",
                r"tutorial",
                r"instru[çc][õo]es",
                r"guia\b",
            ],
            IntentType.GREETING: [
                # Standard greetings
                r"^ol[áa]\b",
                r"^oi\b",
                r"^bom\s+dia\b",
                r"^boa\s+tarde\b",
                r"^boa\s+noite\b",
                # Regional variations
                r"^e\s*a[íi]\b",
                r"^fala\b",
                r"^salve\b",
                r"^opa\b",
                r"^eae\b",
                r"^eai\b",
                # Informal
                r"tudo\s+bem",
                r"tudo\s+bom",
                r"tudo\s+certo",
                r"como\s+vai",
                r"beleza\??$",
                r"blz\??$",
                # English (common in tech)
                r"^hi\b",
                r"^hello\b",
                r"^hey\b",
                # With qualifiers
                r"^ol[áa].*cidad[ãa]o",
                r"^oi.*sistema",
                r"^oi.*ajud",
            ],
            IntentType.CONVERSATION: [
                r"conversar?\b",
                r"falar\s+sobre",
                r"me\s+conte",
                r"vamos\s+conversar",
                r"quero\s+saber",
                r"pode\s+me\s+falar",
                r"pode\s+me\s+contar",
                r"bater\s+papo",
            ],
            IntentType.HELP_REQUEST: [
                r"preciso\s+de\s+ajuda",
                r"me\s+ajud[ae]",
                r"pode\s+ajudar",
                r"n[ãa]o\s+sei\s+como",
                r"n[ãa]o\s+entendi",
                r"como\s+fa[çc]o",
                r"como\s+usar",
                r"n[ãa]o\s+consigo",
                r"est[áa]\s+dif[íi]cil",
                r"me\s+ensina",
                r"pode\s+explicar",
            ],
            IntentType.ABOUT_SYSTEM: [
                # System identity
                r"o\s+que\s+[ée]\s+o\s+cidad[ãa]o",
                r"o\s+que\s+[ée]\s+isso",
                r"como\s+voc[êe]\s+funciona",
                r"quem\s+[ée]\s+voc[êe]",
                r"para\s+que\s+serve",
                r"o\s+que\s+voc[êe]\s+faz",
                r"qual\s+sua\s+fun[çc][ãa]o",
                r"suas?\s+capacidades?",
                r"suas?\s+funcionalidades?",
                r"o\s+que\s+pode\s+fazer",
                # Creator/Author queries
                r"quem\s+criou",
                r"quem\s+desenvolveu",
                r"quem\s+fez",
                r"quem\s+idealizou",
                r"criador\s+d[oa]",
                r"autor\s+d[oa]",
                r"desenvolvedor\s+d[oa]",
                r"fundador\s+d[oa]",
                r"respons[áa]vel\s+pel[oa]",
                # Project info
                r"sobre\s+o\s+projeto",
                r"sobre\s+o\s+cidad[ãa]o",
                r"hist[óo]ria\s+d[oa]\s+cidad[ãa]o",
                r"\btcc\b",
                r"trabalho\s+de\s+conclus[ãa]o",
                r"maritaca\s+ai\s+criou",
                r"foi\s+feito\s+por",
                r"empresa\s+que\s+fez",
                # Agents
                r"quais\s+agentes",
                r"agentes?\s+dispon[íi]veis?",
                r"quantos?\s+agentes?",
            ],
            IntentType.SMALLTALK: [
                r"como\s+est[áa]\s+o\s+tempo",
                r"voc[êe]\s+gosta",
                r"qual\s+sua\s+opini[ãa]o",
                r"o\s+que\s+acha",
                r"conte\s+uma\s+hist[óo]ria",
                r"voc[êe]\s+[ée]\s+brasileiro",
                r"gosta\s+de\s+futebol",
                r"voc[êe]\s+[ée]\s+intelig[êe]ncia",
                r"voc[êe]\s+[ée]\s+rob[ôo]",
                r"voc[êe]\s+[ée]\s+humano",
            ],
            IntentType.THANKS: [
                r"obrigad[oa]",
                r"muito\s+obrigad[oa]",
                r"\bvaleu\b",
                r"gratid[ãa]o",
                r"agrade[çc]o",  # Fixed: was agradec[çc]o, but "agradeço" has ç before o
                r"foi\s+[úu]til",
                r"ajudou\s+muito",
                r"perfeito",
                r"excelente",
                r"\bthanks\b",
                r"thank\s+you",
            ],
            IntentType.GOODBYE: [
                r"\btchau\b",
                r"at[ée]\s+logo",
                r"at[ée]\s+mais",
                r"\badeus\b",
                r"\bfalou\b",
                r"tenho\s+que\s+ir",
                r"at[ée]\s+breve",
                r"\bbye\b",
                r"flw\b",
                r"vlw\s+flw",
                r"fuii?\b",
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
    """Service for managing chat sessions and conversations.

    Persists sessions and messages to PostgreSQL via SQLAlchemy.
    """

    def __init__(self) -> None:
        self.cache = cache_service

        # Initialize agents lazily to avoid import-time errors
        self.agents = None
        self._agents_initialized = False

    async def get_or_create_session(
        self, session_id: str, user_id: str | None = None
    ):
        """Get existing session or create new one (persisted to DB)."""
        from sqlalchemy import select

        from src.db.simple_session import get_db_session
        from src.models.chat import ChatSession as DBChatSession

        async with get_db_session() as db:
            result = await db.execute(
                select(DBChatSession).where(DBChatSession.id == session_id)
            )
            session = result.scalar_one_or_none()

            if session:
                session.updated_at = _utcnow()
                return session

            session = DBChatSession(
                id=session_id,
                user_id=user_id,
                status="active",
                context={},
                message_count=0,
            )
            db.add(session)
            await db.flush()
            await db.refresh(session)
            return session

    async def get_session(self, session_id: str):
        """Get session by ID from DB."""
        from sqlalchemy import select

        from src.db.simple_session import get_db_session
        from src.models.chat import ChatSession as DBChatSession

        async with get_db_session() as db:
            result = await db.execute(
                select(DBChatSession).where(DBChatSession.id == session_id)
            )
            return result.scalar_one_or_none()

    async def save_message(
        self, session_id: str, role: str, content: str, agent_id: str | None = None
    ) -> None:
        """Save message to DB and update session metadata."""
        import json as json_mod

        from sqlalchemy import select

        from src.db.simple_session import get_db_session
        from src.models.chat import ChatMessage as DBChatMessage
        from src.models.chat import ChatSession as DBChatSession

        # Serialize dict content
        if isinstance(content, dict):
            content_str = json_mod.dumps(content, ensure_ascii=False, default=str)
        else:
            content_str = str(content) if content else ""

        async with get_db_session() as db:
            message = DBChatMessage(
                session_id=session_id,
                role=role,
                content=content_str,
                agent_id=agent_id,
            )
            db.add(message)

            # Update session metadata
            result = await db.execute(
                select(DBChatSession).where(DBChatSession.id == session_id)
            )
            session = result.scalar_one_or_none()
            if session:
                now = _utcnow()
                session.last_message_at = now
                session.updated_at = now
                session.message_count = (session.message_count or 0) + 1

                # Auto-generate title from first user message
                if session.message_count == 1 and role == "user":
                    session.title = self._generate_title(content_str)

    async def get_session_messages(
        self, session_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get messages for a session from DB, ordered chronologically."""
        from sqlalchemy import select

        from src.db.simple_session import get_db_session
        from src.models.chat import ChatMessage as DBChatMessage

        async with get_db_session() as db:
            result = await db.execute(
                select(DBChatMessage)
                .where(DBChatMessage.session_id == session_id)
                .order_by(DBChatMessage.created_at.asc())
                .limit(limit)
            )
            messages = result.scalars().all()

            return [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": (
                        msg.created_at.isoformat() if msg.created_at else None
                    ),
                    "agent_id": msg.agent_id,
                }
                for msg in messages
            ]

    async def clear_session(self, session_id: str) -> None:
        """Soft-delete session and remove its messages."""
        from sqlalchemy import delete, select

        from src.db.simple_session import get_db_session
        from src.models.chat import ChatMessage as DBChatMessage
        from src.models.chat import ChatSession as DBChatSession

        async with get_db_session() as db:
            # Delete messages (FK CASCADE would also handle this)
            await db.execute(
                delete(DBChatMessage).where(
                    DBChatMessage.session_id == session_id
                )
            )
            # Mark session as cleared
            result = await db.execute(
                select(DBChatSession).where(DBChatSession.id == session_id)
            )
            session = result.scalar_one_or_none()
            if session:
                session.status = "cleared"
                session.message_count = 0

    async def get_user_sessions(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        """List sessions for a user, ordered by most recent activity."""
        from sqlalchemy import select

        from src.db.simple_session import get_db_session
        from src.models.chat import ChatSession as DBChatSession

        async with get_db_session() as db:
            result = await db.execute(
                select(DBChatSession)
                .where(
                    DBChatSession.user_id == user_id,
                    DBChatSession.status != "cleared",
                )
                .order_by(DBChatSession.updated_at.desc())
                .offset(offset)
                .limit(limit)
            )
            sessions = result.scalars().all()
            return [s.to_dict() for s in sessions]

    async def delete_session(self, session_id: str) -> None:
        """Hard-delete a session and all its messages."""
        from sqlalchemy import delete

        from src.db.simple_session import get_db_session
        from src.models.chat import ChatMessage as DBChatMessage
        from src.models.chat import ChatSession as DBChatSession

        async with get_db_session() as db:
            await db.execute(
                delete(DBChatMessage).where(
                    DBChatMessage.session_id == session_id
                )
            )
            await db.execute(
                delete(DBChatSession).where(DBChatSession.id == session_id)
            )

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
        """Update session with current investigation ID in DB."""
        from sqlalchemy import select

        from src.db.simple_session import get_db_session
        from src.models.chat import ChatSession as DBChatSession

        async with get_db_session() as db:
            result = await db.execute(
                select(DBChatSession).where(DBChatSession.id == session_id)
            )
            session = result.scalar_one_or_none()
            if session:
                session.current_investigation_id = investigation_id
                session.updated_at = _utcnow()

    @staticmethod
    def _generate_title(content: str) -> str:
        """Generate a session title from the first user message."""
        title = content.strip()
        if len(title) > 80:
            title = title[:77] + "..."
        return title

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
