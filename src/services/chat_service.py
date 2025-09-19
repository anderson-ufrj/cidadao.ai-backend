"""
Chat service for managing conversations and intent detection
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import re
import json
from collections import defaultdict

from src.core import get_logger
from src.services.cache_service import cache_service
from src.agents import (
    MasterAgent, InvestigatorAgent, AnalystAgent, 
    ReporterAgent, BaseAgent
)

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

@dataclass
class Intent:
    """Detected user intent"""
    type: IntentType
    entities: Dict[str, Any]
    confidence: float
    suggested_agent: str
    
    def dict(self):
        return {
            "type": self.type.value,
            "entities": self.entities,
            "confidence": self.confidence,
            "suggested_agent": self.suggested_agent
        }

@dataclass
class ChatSession:
    """Chat session data"""
    id: str
    user_id: Optional[str]
    created_at: datetime
    last_activity: datetime
    current_investigation_id: Optional[str] = None
    context: Dict[str, Any] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "current_investigation_id": self.current_investigation_id,
            "context": self.context or {}
        }

class IntentDetector:
    """Detects user intent from messages"""
    
    def __init__(self):
        # Intent patterns in Portuguese
        self.patterns = {
            IntentType.INVESTIGATE: [
                r"investigar?\s+(\w+)",
                r"analis[ae]r?\s+contratos",
                r"verificar?\s+gastos",
                r"procurar?\s+irregularidades",
                r"detectar?\s+anomalias",
                r"buscar?\s+problemas"
            ],
            IntentType.ANALYZE: [
                r"anomalias?\s+",
                r"padr[õo]es?\s+suspeitos",
                r"gastos?\s+excessivos",
                r"fornecedores?\s+concentrados",
                r"an[áa]lise\s+de",
                r"mostrar?\s+gr[áa]ficos"
            ],
            IntentType.REPORT: [
                r"gerar?\s+relat[óo]rio",
                r"documento\s+",
                r"resumo\s+",
                r"exportar?\s+dados",
                r"baixar?\s+",
                r"pdf\s+"
            ],
            IntentType.STATUS: [
                r"status\s+",
                r"progresso\s+",
                r"como\s+est[áa]",
                r"andamento\s+"
            ],
            IntentType.HELP: [
                r"como\s+funciona",
                r"ajuda",
                r"help",
                r"o\s+que\s+[ée]",
                r"explicar?"
            ],
            IntentType.GREETING: [
                r"ol[áa]",
                r"oi",
                r"bom\s+dia",
                r"boa\s+tarde",
                r"boa\s+noite",
                r"e\s+a[íi]",
                r"tudo\s+bem",
                r"como\s+vai"
            ],
            IntentType.CONVERSATION: [
                r"conversar",
                r"falar\s+sobre",
                r"me\s+conte",
                r"vamos\s+conversar",
                r"quero\s+saber",
                r"pode\s+me\s+falar"
            ],
            IntentType.HELP_REQUEST: [
                r"preciso\s+de\s+ajuda",
                r"me\s+ajud[ae]",
                r"pode\s+ajudar",
                r"n[ãa]o\s+sei\s+como",
                r"n[ãa]o\s+entendi",
                r"como\s+fa[çc]o"
            ],
            IntentType.ABOUT_SYSTEM: [
                r"o\s+que\s+[ée]\s+o\s+cidad[ãa]o",
                r"como\s+voc[êe]\s+funciona",
                r"quem\s+[ée]\s+voc[êe]",
                r"para\s+que\s+serve",
                r"o\s+que\s+voc[êe]\s+faz",
                r"qual\s+sua\s+fun[çc][ãa]o"
            ],
            IntentType.SMALLTALK: [
                r"como\s+est[áa]\s+o\s+tempo",
                r"voc[êe]\s+gosta",
                r"qual\s+sua\s+opini[ãa]o",
                r"o\s+que\s+acha",
                r"conte\s+uma\s+hist[óo]ria",
                r"voc[êe]\s+[ée]\s+brasileiro"
            ],
            IntentType.THANKS: [
                r"obrigad[oa]",
                r"muito\s+obrigad[oa]",
                r"valeu",
                r"gratid[ãa]o",
                r"agradec[çc]o",
                r"foi\s+[úu]til"
            ],
            IntentType.GOODBYE: [
                r"tchau",
                r"at[ée]\s+logo",
                r"at[ée]\s+mais",
                r"adeus",
                r"falou",
                r"tenho\s+que\s+ir",
                r"at[ée]\s+breve"
            ]
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
            "agricultura": {"name": "Ministério da Agricultura", "code": "22000"}
        }
    
    async def detect(self, message: str) -> Intent:
        """Detect intent from user message"""
        message_lower = message.lower().strip()
        
        # Extract entities
        entities = {
            "original_message": message,
            "organs": self._extract_organs(message_lower),
            "period": self._extract_period(message_lower),
            "values": self._extract_values(message_lower)
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
            suggested_agent=suggested_agent
        )
    
    def _extract_organs(self, text: str) -> List[Dict[str, str]]:
        """Extract government organ mentions"""
        found = []
        for keyword, info in self.organ_map.items():
            if keyword in text:
                found.append(info)
        return found
    
    def _extract_period(self, text: str) -> Optional[Dict[str, str]]:
        """Extract time period mentions"""
        # Look for year patterns
        year_match = re.search(r"20\d{2}", text)
        if year_match:
            year = year_match.group()
            return {"year": year, "type": "year"}
        
        # Look for month patterns
        months = {
            "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3,
            "abril": 4, "maio": 5, "junho": 6,
            "julho": 7, "agosto": 8, "setembro": 9,
            "outubro": 10, "novembro": 11, "dezembro": 12
        }
        
        for month_name, month_num in months.items():
            if month_name in text:
                return {"month": month_num, "type": "month"}
        
        # Look for relative periods
        if "último" in text or "ultimo" in text:
            if "mês" in text or "mes" in text:
                return {"relative": "last_month", "type": "relative"}
            elif "ano" in text:
                return {"relative": "last_year", "type": "relative"}
        
        return None
    
    def _extract_values(self, text: str) -> List[float]:
        """Extract monetary values"""
        values = []
        
        # Pattern for Brazilian currency format
        patterns = [
            r"R\$\s*([\d.,]+)",
            r"([\d.,]+)\s*reais",
            r"([\d.,]+)\s*milhões",
            r"([\d.,]+)\s*mil"
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
                except:
                    pass
        
        return values
    
    def _get_agent_for_intent(self, intent_type: IntentType) -> str:
        """Get the best agent for handling this intent
        
        Routing strategy:
        - Conversational intents -> Drummond (conversational AI)
        - Task-specific intents -> Specialized agents
        - Unknown intents -> Abaporu (master orchestrator)
        """
        mapping = {
            # Task-specific routing
            IntentType.INVESTIGATE: "abaporu",      # Master for investigations
            IntentType.ANALYZE: "anita",            # Analyst for patterns
            IntentType.REPORT: "tiradentes",        # Reporter for documents
            IntentType.STATUS: "abaporu",           # Master for status
            
            # Conversational routing to Drummond
            IntentType.GREETING: "drummond",        # Carlos handles greetings
            IntentType.CONVERSATION: "drummond",    # Carlos handles conversation
            IntentType.HELP_REQUEST: "drummond",    # Carlos provides help
            IntentType.ABOUT_SYSTEM: "drummond",    # Carlos explains system
            IntentType.SMALLTALK: "drummond",       # Carlos handles small talk
            IntentType.THANKS: "drummond",          # Carlos receives thanks
            IntentType.GOODBYE: "drummond",         # Carlos handles farewells
            
            # General routing
            IntentType.QUESTION: "drummond",        # Carlos handles general questions
            IntentType.HELP: "drummond",            # Legacy help -> Carlos
            IntentType.UNKNOWN: "drummond"          # Unknown -> Carlos first
        }
        return mapping.get(intent_type, "abaporu")

class ChatService:
    """Service for managing chat sessions and conversations"""
    
    def __init__(self):
        self.cache = cache_service
        self.sessions: Dict[str, ChatSession] = {}
        self.messages: Dict[str, List[Dict]] = defaultdict(list)
        
        # Agents will be initialized lazily when needed
        self.agents = {}
    
    async def get_or_create_session(
        self, 
        session_id: str, 
        user_id: Optional[str] = None
    ) -> ChatSession:
        """Get existing session or create new one"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.last_activity = datetime.utcnow()
            return session
        
        # Create new session
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            context={}
        )
        
        self.sessions[session_id] = session
        return session
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        agent_id: Optional[str] = None
    ):
        """Save message to session history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id
        }
        
        self.messages[session_id].append(message)
        
        # Update session activity
        if session_id in self.sessions:
            self.sessions[session_id].last_activity = datetime.utcnow()
    
    async def get_session_messages(
        self, 
        session_id: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get messages for a session"""
        messages = self.messages.get(session_id, [])
        return messages[-limit:] if len(messages) > limit else messages
    
    async def clear_session(self, session_id: str):
        """Clear session data"""
        self.sessions.pop(session_id, None)
        self.messages.pop(session_id, None)
    
    async def get_agent_for_intent(self, intent: Intent) -> BaseAgent:
        """Get the appropriate agent for an intent"""
        agent_id = intent.suggested_agent
        return self.agents.get(agent_id, self.agents["abaporu"])
    
    async def update_session_investigation(
        self, 
        session_id: str, 
        investigation_id: str
    ):
        """Update session with current investigation"""
        if session_id in self.sessions:
            self.sessions[session_id].current_investigation_id = investigation_id
            self.sessions[session_id].last_activity = datetime.utcnow()