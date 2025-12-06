"""
Chat API endpoints for conversational interface
VERSION: 2025-10-17 15:00:00 - Consolidated implementation
"""

import asyncio
import random
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse, AgentStatus
from src.api.dependencies import get_current_optional_user
from src.api.models.pagination import CursorPaginationResponse
from src.api.routes.chat_drummond_factory import get_drummond_agent
from src.api.routes.chat_zumbi_integration import (
    format_investigation_message,
    run_zumbi_investigation,
)
from src.core import get_logger, json_utils
from src.core.config import get_settings
from src.services.agent_routing import resolve_agent_id
from src.services.chat_data_integration import chat_data_integration
from src.services.chat_service import IntentType
from src.services.maritaca_direct_service import (
    MaritacaChatRequest,
    MaritacaChatResponse,
    get_maritaca_service,
)
from src.services.message_sanitizer import (
    MessageValidationStatus,
    extract_safe_log_message,
    get_edge_case_response,
    sanitize_message,
)
from src.services.orchestration.models.investigation import InvestigationIntent
from src.services.orchestration.query_planner.intent_classifier import IntentClassifier

# Import investigative service for real-time contract search
try:
    from src.services.chat_investigative_service import get_investigative_service

    investigative_service = get_investigative_service()
    INVESTIGATIVE_SERVICE_AVAILABLE = True
except Exception:
    investigative_service = None
    INVESTIGATIVE_SERVICE_AVAILABLE = False

# Initialize logger BEFORE using it
logger = get_logger(__name__)

# Import DSPy Agent Service for personality-based responses
try:
    from src.services.dspy_agents import DSPY_IMPORT_ERROR, get_dspy_agent_service

    dspy_service = get_dspy_agent_service()
    # Check if DSPy is actually available and configured
    DSPY_AVAILABLE = dspy_service.is_available() if dspy_service else False
    if DSPY_AVAILABLE:
        logger.info("DSPy Agent Service loaded successfully with full LLM support")
    else:
        logger.warning(
            f"DSPy Agent Service loaded but not fully available: {DSPY_IMPORT_ERROR}"
        )
except Exception as e:
    import traceback

    logger.warning(f"DSPy Agent Service not available: {e}")
    logger.warning(f"DSPy import traceback: {traceback.format_exc()}")
    dspy_service = None
    DSPY_AVAILABLE = False

# Import Orchestrator for full multi-API investigations
try:
    from src.services.orchestration.orchestrator import InvestigationOrchestrator

    orchestrator = InvestigationOrchestrator()
    ORCHESTRATOR_AVAILABLE = True
    logger.info("InvestigationOrchestrator loaded successfully")
except Exception as e:
    logger.warning(f"InvestigationOrchestrator not available: {e}")
    orchestrator = None
    ORCHESTRATOR_AVAILABLE = False


# Import models for the simple fallback agent
class DataSourceType:
    """Simple data source type for fallback."""

    CONTRACTS = "contratos"
    SERVANTS = "servidores"
    EXPENSES = "despesas"
    BIDDINGS = "licitacoes"


class UniversalSearchRequest(BaseModel):
    """Universal search request model."""

    query: str
    data_source: str
    filters: dict[str, Any] = Field(default_factory=dict)
    max_results: int = Field(default=100)


# Simple fallback agent will be imported lazily if needed
enhanced_zumbi = None

logger = get_logger(__name__)
router = APIRouter()

# Import chat service with error handling
try:
    from src.services.chat_service_with_cache import chat_service

    if chat_service is None:
        from src.services.chat_service_with_cache import get_chat_service

        chat_service = get_chat_service()
except Exception as e:
    logger.warning(f"Failed to import chat_service: {e}")
    chat_service = None

# Services are already initialized
# Use NEW IntentClassifier with keyword detection (367x faster)
# Initialize in keyword-only mode to avoid LLM dependencies
try:
    intent_classifier = IntentClassifier(keyword_only=True)
    logger.info("IntentClassifier initialized successfully (keyword-only mode)")
except Exception as e:
    logger.error(f"Failed to initialize IntentClassifier: {e}")
    intent_classifier = None

# Agent name to import path mapping
AGENT_MAP = {
    "drummond": ("src.agents.drummond", "DrummondAgent"),
    "zumbi": (
        "src.agents.zumbi",
        "InvestigatorAgent",
    ),  # FIXED: zumbi.py exports InvestigatorAgent
    "abaporu": ("src.agents.abaporu", "AbaporuAgent"),
    "machado": ("src.agents.machado", "MachadoAgent"),
    "bonifacio": ("src.agents.bonifacio", "BonifacioAgent"),
    "maria_quiteria": ("src.agents.maria_quiteria", "MariaQuiteriaAgent"),
    "tiradentes": (
        "src.agents.tiradentes",
        "ReporterAgent",
    ),  # Fixed: was TiradentesAgent
    "oscar_niemeyer": ("src.agents.oscar_niemeyer", "OscarNiemeyerAgent"),
    "anita": ("src.agents.anita", "AnalystAgent"),  # Fixed: was AnitaAgent
    "oxossi": ("src.agents.oxossi", "OxossiAgent"),
    "santos_dumont": ("src.agents.santos_dumont", "EducatorAgent"),
}

# Cache for loaded agents
_agent_cache: dict[str, Any] = {}


async def get_agent_by_name(agent_name: str) -> Any | None:
    """
    Get agent instance by name with lazy loading.

    Args:
        agent_name: Name of the agent (e.g., 'machado', 'bonifacio')

    Returns:
        Agent instance or None if not available
    """
    # Check cache first
    if agent_name in _agent_cache:
        return _agent_cache[agent_name]

    # Special handling for Drummond (already has a factory)
    if agent_name == "drummond":
        try:
            agent = await get_drummond_agent()
            if agent:
                _agent_cache[agent_name] = agent
            return agent
        except Exception as e:
            logger.error(f"Error loading Drummond agent: {e}")
            return None

    # Get agent import info
    if agent_name not in AGENT_MAP:
        logger.warning(f"Unknown agent: {agent_name}")
        return None

    module_path, class_name = AGENT_MAP[agent_name]

    try:
        # Dynamic import
        import importlib

        module = importlib.import_module(module_path)
        agent_class = getattr(module, class_name)

        # Create instance
        agent = agent_class()
        _agent_cache[agent_name] = agent

        logger.info(f"Loaded agent: {agent_name} ({class_name})")
        return agent

    except Exception as e:
        logger.error(f"Error loading agent {agent_name}: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return None


# Agents will be initialized lazily to avoid import-time errors
master_agent = None


def get_master_agent():
    """Get or create master agent instance lazily."""
    global master_agent
    if master_agent is None:
        try:
            # MasterAgent needs llm_service and memory_agent
            # For now, return None since we don't have these dependencies
            logger.warning(
                "MasterAgent initialization skipped - dependencies not available"
            )
            return None
        except Exception as e:
            logger.error(f"Failed to initialize MasterAgent: {type(e).__name__}: {e}")
            return None
    return master_agent


class ChatRequest(BaseModel):
    """Chat message request"""

    message: str = Field(..., min_length=1, max_length=1000)
    session_id: str | None = None
    context: dict[str, Any] | None = None
    agent_id: str | None = Field(
        None,
        description="Force a specific agent (zumbi, anita, drummond, tiradentes, oxossi, dandara, machado, abaporu). If not provided, agent is auto-selected based on intent.",
    )


class ChatResponse(BaseModel):
    """Chat message response"""

    session_id: str
    message_id: str | None = None
    agent_id: str
    agent_name: str
    message: str
    confidence: float
    suggested_actions: list[str] | None = None
    follow_up_questions: list[str] | None = None
    requires_input: dict[str, str] | None = None
    metadata: dict[str, Any] = {}


class QuickAction(BaseModel):
    """Quick action suggestion"""

    id: str
    label: str
    icon: str
    action: str


# ============================================================================
# INSTANT RESPONSES - No LLM needed (performance optimization Dec 2025)
# ============================================================================
# ================================================================
# INSTANT RESPONSES WITH DRUMMOND'S POETIC PERSONALITY (Dec 2025)
# These responses are returned instantly without calling the LLM,
# reducing greeting response time from ~7s to <100ms
# Written in the style of Carlos Drummond de Andrade - poet of Itabira
# ================================================================

INSTANT_GREETING_RESPONSES = [
    "Olá, cidadão! Como o poeta que caminha pelas ruas de Itabira buscando verdades, venho ajudá-lo a desvendar os caminhos da transparência pública. O que gostaria de investigar hoje?",
    "Bom dia! No meio do caminho tinha uma pedra... mas aqui no Cidadão.AI, removemos as pedras que obscurecem os gastos públicos. Em que posso ajudá-lo?",
    "Olá! Sou Drummond, o poeta dos dados. Assim como verso a verso construo poemas, byte a byte desvendamos a transparência governamental. Qual mistério público deseja explorar?",
    "Saudações, amigo! Como dizia o poeta: 'E agora, José?' Pois bem, agora investigamos juntos os contratos públicos. O que o traz aqui hoje?",
    "Olá! Entre números e versos, encontramos a verdade. Sou seu guia na poesia da transparência pública brasileira. Como posso servi-lo?",
]

INSTANT_HELP_RESPONSES = [
    """Como poeta que decifra versos, ajudo-o a decifrar os gastos públicos:

🔍 **Investigações** - Desvendo contratos como quem lê entrelinhas de um poema
📊 **Anomalias** - Encontro versos fora da métrica nos gastos governamentais
📝 **Relatórios** - Componho documentos que contam histórias de transparência
📈 **Análises** - Revelo padrões ocultos como metáforas em prosa

Experimente: "Quero investigar contratos da saúde" - e juntos faremos poesia da transparência.""",
    """No verso e no reverso dos dados públicos, posso guiá-lo:

• **Investigar contratos** - Como garimpar ouro em Itabira, buscamos verdades
• **Detectar anomalias** - Versos destoantes na sinfonia dos gastos
• **Analisar fornecedores** - Conhecer quem escreve a história do erário
• **Gerar relatórios** - Antologias completas de transparência

Diga-me: qual capítulo da transparência brasileira deseja explorar?""",
]

INSTANT_ABOUT_RESPONSES = [
    """Como todo bom poema, o Cidadão.AI nasceu de uma inquietação. Deixe-me contar sua história:

**O Poeta por trás dos Versos:** Anderson Henrique da Silva, mineiro como eu, idealizou este sistema.

**O Palco Acadêmico:** Este é um Trabalho de Conclusão de Curso no IFSULDEMINAS, sob a batuta da Professora Aracele Garcia de Oliveira Fassbinder.

**Nossa Trupe de 16 Agentes:** Somos personagens da história brasileira - Zumbi dos Palmares investiga, Anita Garibaldi analisa, Tiradentes reporta, e eu, Drummond, comunico.

**Parceiros Essenciais:** Este projeto só foi possível graças ao incentivo à pesquisa e à generosa cessão de créditos gratuitos da **Maritaca AI**, que acredita no potencial da IA brasileira para transformar a sociedade. Nosso sincero agradecimento!

Juntos, fazemos da transparência nossa poesia coletiva. E agora, cidadão? Que versos escrevemos hoje?""",
]

INSTANT_THANKS_RESPONSES = [
    "A gratidão é a poesia do coração! Fico feliz em ajudar. Se precisar desvendar mais mistérios públicos, cá estarei, entre versos e dados.",
    "Como dizia o poeta: o tempo é a minha matéria. E foi um prazer dedicar este tempo a você. Volte sempre que a transparência chamar!",
    "De nada, amigo! Na luta pela transparência, cada cidadão informado é um verso de esperança. Conte comigo sempre.",
]

INSTANT_GOODBYE_RESPONSES = [
    "Até breve! Como no fim de um poema, deixo reticências... pois nossa história com a transparência continua. Volte sempre!",
    "Adeus por ora! Lembre-se: a transparência é direito do povo, e a poesia está em exercê-lo. Até a próxima investigação!",
    "Vá em paz, cidadão! E como escreveu o poeta: 'De tudo fica um pouco.' Que fique em você a semente da transparência. Até logo!",
]

# ================================================================
# VERIFIED AGENT LIST - Dec 2025 (Prevents LLM hallucination)
# This is the AUTHORITATIVE list of agents in the system
# ================================================================
INSTANT_AGENTS_RESPONSE = """Nossa trupe conta com **16 agentes especializados**, cada um com sua missão na transparência:

🎨 **Abaporu** - Orquestrador Master, coordena investigações complexas
🔍 **Zumbi dos Palmares** - Investigador, detecta anomalias e irregularidades
📊 **Anita Garibaldi** - Analista, analisa padrões e tendências estatísticas
📝 **Tiradentes** - Relator, gera relatórios detalhados
✍️ **Carlos Drummond de Andrade** - Comunicador, sou eu! Interface conversacional
📚 **Machado de Assis** - Analista Textual, analisa documentos e contratos
⚖️ **José Bonifácio** - Especialista Legal, verifica conformidade com leis
🛡️ **Maria Quitéria** - Auditora de Segurança, análise de vulnerabilidades
🏹 **Oxóssi** - Caçador de Dados, busca informações em múltiplas fontes
📐 **Oscar Niemeyer** - Visualizador, cria gráficos e dashboards
✊ **Dandara** - Justiça Social, avalia equidade e inclusão
🌵 **Lampião** - Investigador Regional, foco em dados do Nordeste
🌙 **Nanã** - Memória, gerencia contexto e histórico
🔮 **Ceuci** - Preditivo, análises preditivas e ETL
🔥 **Obaluaiê** - Detector de Corrupção, identifica padrões suspeitos
🏎️ **Ayrton Senna** - Roteador Semântico, direciona consultas rapidamente

Cada agente traz sua expertise única. Juntos, somos uma orquestra pela transparência!"""

# Keywords that indicate user is asking about agents
AGENT_QUESTION_KEYWORDS = [
    "quais agentes",
    "quem são os agentes",
    "quem sao os agentes",
    "lista de agentes",
    "listar agentes",
    "agentes do sistema",
    "agentes existem",
    "agentes disponíveis",
    "agentes disponiveis",
    "quantos agentes",
    "todos os agentes",
    "conhecer os agentes",
    "apresente os agentes",
    "me apresente os agentes",
]

# ================================================================
# VERIFIED RESPONSES FOR KEY TOPICS (Dec 2025)
# Prevents LLM hallucination about project stakeholders
# ================================================================

INSTANT_CREATOR_RESPONSE = """**Anderson Henrique da Silva** é o criador e idealizador do Cidadão.AI.

Mineiro de coração, Anderson é estudante do **IFSULDEMINAS** (Instituto Federal do Sul de Minas Gerais) e desenvolveu este sistema como seu Trabalho de Conclusão de Curso (TCC).

Sua visão: criar uma ferramenta que democratize o acesso à informação pública, usando IA para ajudar cidadãos a entenderem como o dinheiro público é gasto.

O projeto conta com a orientação da **Professora Aracele Garcia de Oliveira Fassbinder** e foi viabilizado pelo apoio da **Maritaca AI**, que cedeu créditos gratuitos acreditando no potencial da pesquisa brasileira.

Anderson sonha que o Cidadão.AI inspire mais projetos de transparência e engajamento cívico no Brasil! 🇧🇷"""

INSTANT_ADVISOR_RESPONSE = """**Aracele Garcia de Oliveira Fassbinder** é a orientadora do projeto Cidadão.AI.

Professora do **IFSULDEMINAS**, ela tem sido fundamental para o desenvolvimento deste Trabalho de Conclusão de Curso, oferecendo:

📚 **Orientação Acadêmica** - Direcionamento metodológico e científico
🎯 **Visão Estratégica** - Ajudando a definir escopo e objetivos
✅ **Rigor Técnico** - Garantindo qualidade e consistência do trabalho

Sua experiência e dedicação são pilares essenciais para que o Cidadão.AI alcance seus objetivos de promover transparência governamental através da tecnologia.

O projeto é uma parceria entre a visão do estudante Anderson Henrique da Silva e a expertise acadêmica da Professora Aracele! 🎓"""

INSTANT_IFSULDEMINAS_RESPONSE = """O **IFSULDEMINAS** (Instituto Federal de Educação, Ciência e Tecnologia do Sul de Minas Gerais) é o berço acadêmico do Cidadão.AI!

🏛️ **Instituição de Excelência** - Referência em educação pública de qualidade no sul de Minas Gerais

📖 **Contexto do Projeto** - O Cidadão.AI é um Trabalho de Conclusão de Curso (TCC) desenvolvido por Anderson Henrique da Silva, sob orientação da Professora Aracele Garcia de Oliveira Fassbinder

🌟 **Importância** - O IFSULDEMINAS proporciona o ambiente acadêmico e o suporte necessário para que projetos inovadores como este possam florescer

🤝 **Parceria** - Junto com o apoio da Maritaca AI (créditos gratuitos para pesquisa), o instituto possibilita que a pesquisa brasileira em IA avance!

O Cidadão.AI é prova de que a educação pública brasileira pode gerar inovação de impacto social! 🇧🇷"""

INSTANT_MARITACA_RESPONSE = """A **Maritaca AI** é uma parceira essencial do projeto Cidadão.AI!

🤖 **Quem são** - Empresa brasileira de Inteligência Artificial, criadora dos modelos Sabiá (otimizados para português brasileiro)

🎁 **Apoio ao Projeto** - A Maritaca AI cedeu **créditos gratuitos** para pesquisa, viabilizando o desenvolvimento do Cidadão.AI

💡 **Por que é importante** - Sem esse apoio, seria muito mais difícil para um projeto acadêmico (TCC) ter acesso a modelos de linguagem de alta qualidade

🇧🇷 **Visão** - A Maritaca acredita no potencial da IA brasileira para transformar a sociedade, e o Cidadão.AI é um exemplo dessa transformação

**Nosso sincero agradecimento à Maritaca AI** por acreditar na pesquisa e na educação brasileira! O Cidadão.AI não seria possível sem esse incentivo. 🙏"""

# Keywords for each topic
CREATOR_KEYWORDS = [
    "anderson",
    "criador",
    "quem criou",
    "quem fez",
    "idealizador",
    "desenvolvedor",
    "autor do projeto",
    "fale sobre o anderson",
    "me fale sobre anderson",
    "quem é o anderson",
]

ADVISOR_KEYWORDS = [
    "aracele",
    "orientadora",
    "orientador",
    "professora",
    "fassbinder",
    "quem orienta",
    "orientação",
]

IFSULDEMINAS_KEYWORDS = [
    "ifsuldeminas",
    "instituto federal",
    "sul de minas",
    "onde foi criado",
    "onde nasceu",
    "instituição",
    "faculdade",
    "universidade",
]

MARITACA_KEYWORDS = [
    "maritaca",
    "maritaca ai",
    "sabia",
    "sabiá",
    "modelo de linguagem",
    "llm usado",
    "qual ia",
    "qual modelo",
    "parceiro",
    "patrocinador",
    "apoio",
]


def _is_agent_list_question(message: str) -> bool:
    """Check if user is asking about the list of agents."""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in AGENT_QUESTION_KEYWORDS)


def _is_creator_question(message: str) -> bool:
    """Check if user is asking about the creator (Anderson)."""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in CREATOR_KEYWORDS)


def _is_advisor_question(message: str) -> bool:
    """Check if user is asking about the advisor (Aracele)."""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in ADVISOR_KEYWORDS)


def _is_ifsuldeminas_question(message: str) -> bool:
    """Check if user is asking about IFSULDEMINAS."""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in IFSULDEMINAS_KEYWORDS)


def _is_maritaca_question(message: str) -> bool:
    """Check if user is asking about Maritaca AI."""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in MARITACA_KEYWORDS)


def _needs_verified_response(message: str) -> bool:
    """Check if message needs a verified (hardcoded) response to prevent hallucination."""
    return (
        _is_agent_list_question(message)
        or _is_creator_question(message)
        or _is_advisor_question(message)
        or _is_ifsuldeminas_question(message)
        or _is_maritaca_question(message)
    )


def get_instant_response(intent_type: IntentType, message: str = "") -> str | None:
    """
    Get an instant response for simple intents (no LLM needed).

    Returns None if the intent requires LLM processing.

    Args:
        intent_type: The detected intent type
        message: The original user message (for additional context checks)

    Note: Uses random.choice for variety - not security-critical (S311).
    """
    # ================================================================
    # PRIORITY CHECKS: Verified responses to prevent LLM hallucination
    # These must come FIRST to intercept specific questions
    # ================================================================

    if message:
        # Check for agent list questions
        if _is_agent_list_question(message):
            logger.info("Detected agent list question - using verified response")
            return INSTANT_AGENTS_RESPONSE

        # Check for creator (Anderson) questions
        if _is_creator_question(message):
            logger.info("Detected creator question - using verified response")
            return INSTANT_CREATOR_RESPONSE

        # Check for advisor (Aracele) questions
        if _is_advisor_question(message):
            logger.info("Detected advisor question - using verified response")
            return INSTANT_ADVISOR_RESPONSE

        # Check for IFSULDEMINAS questions
        if _is_ifsuldeminas_question(message):
            logger.info("Detected IFSULDEMINAS question - using verified response")
            return INSTANT_IFSULDEMINAS_RESPONSE

        # Check for Maritaca AI questions
        if _is_maritaca_question(message):
            logger.info("Detected Maritaca AI question - using verified response")
            return INSTANT_MARITACA_RESPONSE

    # ================================================================
    # INTENT-BASED RESPONSES
    # ================================================================

    if intent_type == IntentType.GREETING:
        return random.choice(INSTANT_GREETING_RESPONSES)  # noqa: S311
    if intent_type in [IntentType.HELP, IntentType.HELP_REQUEST]:
        return random.choice(INSTANT_HELP_RESPONSES)  # noqa: S311
    if intent_type == IntentType.ABOUT_SYSTEM:
        return random.choice(INSTANT_ABOUT_RESPONSES)  # noqa: S311
    if intent_type == IntentType.THANKS:
        return random.choice(INSTANT_THANKS_RESPONSES)  # noqa: S311
    if intent_type == IntentType.GOODBYE:
        return random.choice(INSTANT_GOODBYE_RESPONSES)  # noqa: S311
    return None


# Contract search detection keywords
CONTRACT_SEARCH_KEYWORDS = [
    "contrato",
    "contratos",
    "buscar contrato",
    "pesquisar contrato",
    "mostrar contrato",
    "listar contrato",
    "encontrar contrato",
    "ver contrato",
    "ministério",
    "ministerio",
    "órgão",
    "orgao",
    "saúde",
    "saude",
    "educação",
    "educacao",
    "defesa",
    "justiça",
    "justica",
    "fazenda",
    "infraestrutura",
    "meio ambiente",
]


def _is_contract_search_query(message: str, intent_type: IntentType) -> bool:
    """
    Detect if the user query is asking to search/list contracts.

    Args:
        message: User message
        intent_type: Detected intent type

    Returns:
        True if this is a contract search query
    """
    message_lower = message.lower()

    # Check if it's an investigation intent AND mentions contracts/organizations
    if intent_type == IntentType.INVESTIGATE:
        for keyword in CONTRACT_SEARCH_KEYWORDS:
            if keyword in message_lower:
                return True

    # Explicit contract search patterns
    explicit_patterns = [
        "buscar contrato",
        "pesquisar contrato",
        "listar contrato",
        "mostrar contrato",
        "encontrar contrato",
        "contratos do",
        "contratos da",
        "contratos de",
        "investigar contrato",
    ]

    for pattern in explicit_patterns:
        if pattern in message_lower:
            return True

    return False


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest, current_user=Depends(get_current_optional_user)
) -> ChatResponse:
    """
    Process a chat message and return agent response
    """
    try:
        # ================================================================
        # EDGE CASE HANDLING: Validate and sanitize message (Dec 2025)
        # ================================================================
        validation = sanitize_message(request.message)
        session_id = request.session_id or str(uuid.uuid4())

        # Log with safe message content
        logger.info(
            f"Chat request: {extract_safe_log_message(request.message)}",
            extra={
                "session_id": session_id,
                "validation_status": validation.status.value,
            },
        )

        # Handle edge cases with instant responses
        if validation.status != MessageValidationStatus.VALID:
            edge_response = get_edge_case_response(validation.status)
            if edge_response:
                logger.info(f"Edge case handled: {validation.status.value}")
                return ChatResponse(
                    session_id=session_id,
                    message_id=str(uuid.uuid4()),
                    agent_id="drummond",
                    agent_name="Carlos Drummond de Andrade",
                    message=validation.suggested_response or edge_response["message"],
                    confidence=1.0,
                    suggested_actions=edge_response.get("suggested_actions"),
                    follow_up_questions=None,
                    requires_input=None,
                    metadata={
                        "edge_case": validation.status.value,
                        "warning": validation.warning,
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                )

        # Use sanitized message for processing
        sanitized_message = validation.sanitized_message

        # Check if chat service is available
        if chat_service is None:
            logger.error("Chat service not available")
            return ChatResponse(
                session_id=session_id,
                message_id=str(uuid.uuid4()),
                agent_id="system",
                agent_name="Sistema",
                message="Desculpe, o serviço de chat está temporariamente indisponível.",
                confidence=0.0,
                suggested_actions=["retry"],
                metadata={"error": "service_unavailable"},
            )
        session = await chat_service.get_or_create_session(
            session_id, user_id=current_user.id if current_user else None
        )

        # Detect intent from message using keyword-based classifier
        intent_type_str = "unknown"
        confidence = 0.5

        try:
            if intent_classifier is not None:
                # Use sanitized message for intent detection
                intent_result = await intent_classifier.classify(sanitized_message)
                detected_intent = intent_result["intent"]
                confidence = intent_result["confidence"]
                method = intent_result.get("method", "unknown")

                # Get intent value (string) - handles both InvestigationIntent enum and raw strings
                intent_value = (
                    detected_intent.value
                    if hasattr(detected_intent, "value")
                    else str(detected_intent)
                )

                logger.info(
                    f"[{method.upper()}] Detected intent: {intent_value} with confidence {confidence:.2f}"
                )

                # Convert InvestigationIntent to "investigate" string for routing
                if detected_intent in [
                    InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
                    InvestigationIntent.SUPPLIER_INVESTIGATION,
                    InvestigationIntent.CORRUPTION_INDICATORS,
                    InvestigationIntent.BUDGET_ANALYSIS,
                    InvestigationIntent.HEALTH_BUDGET_ANALYSIS,
                    InvestigationIntent.EDUCATION_PERFORMANCE,
                ]:
                    intent_type_str = "investigate"
                else:
                    # For non-investigation intents (greeting, thanks, goodbye, help_request, about_system)
                    # or GENERAL_QUERY, use the value directly
                    intent_type_str = intent_value
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")

        # Create simple intent object for compatibility
        class Intent:
            def __init__(self, type_str: str, conf: float, agent_id: str):
                self.type = (
                    IntentType(type_str)
                    if type_str in [e.value for e in IntentType]
                    else IntentType.UNKNOWN
                )
                self.confidence = conf
                self.suggested_agent = agent_id
                self.entities: dict[str, Any] = {}

            def dict(self) -> dict[str, Any]:
                return {
                    "type": self.type.value,
                    "confidence": self.confidence,
                    "suggested_agent": self.suggested_agent,
                }

        # Use centralized agent routing (single source of truth)
        # This respects user's agent_id choice or uses Abaporu as default
        target_agent, _target_agent_name = resolve_agent_id(
            requested_agent_id=request.agent_id,
            intent_type=intent_type_str,
            intent_confidence=confidence,
        )

        intent = Intent(intent_type_str, confidence, target_agent)
        logger.info(
            f"Message routing: intent={intent.type.value}, agent={target_agent}"
        )

        # ================================================================
        # SHORT-CIRCUIT: Instant responses for simple intents (Dec 2025)
        # This optimization reduces greeting response from ~7s to <100ms
        # Also intercepts questions about project stakeholders to prevent hallucination
        # ================================================================
        if (confidence >= 0.7 and request.agent_id is None) or _needs_verified_response(
            sanitized_message
        ):
            instant_response = get_instant_response(intent.type, sanitized_message)
            if instant_response:
                logger.info(f"Using instant response for intent: {intent.type.value}")

                # Save to chat history
                await chat_service.save_message(
                    session_id=session_id, role="user", content=sanitized_message
                )
                await chat_service.save_message(
                    session_id=session_id,
                    role="assistant",
                    content=instant_response,
                    agent_id="drummond",
                )

                # Get suggested actions based on intent
                suggested_actions = []
                if intent.type == IntentType.GREETING:
                    suggested_actions = [
                        "start_investigation",
                        "learn_more",
                        "view_examples",
                    ]
                elif intent.type in [IntentType.HELP, IntentType.HELP_REQUEST]:
                    suggested_actions = [
                        "investigate_contracts",
                        "detect_anomalies",
                        "generate_report",
                    ]
                elif intent.type == IntentType.ABOUT_SYSTEM:
                    suggested_actions = [
                        "start_investigation",
                        "meet_agents",
                        "view_capabilities",
                    ]
                elif intent.type == IntentType.THANKS:
                    suggested_actions = ["new_investigation", "learn_more"]
                elif intent.type == IntentType.GOODBYE:
                    suggested_actions = ["restart_chat"]

                return ChatResponse(
                    session_id=session_id,
                    message_id=str(uuid.uuid4()),
                    agent_id="drummond",
                    agent_name="Carlos Drummond de Andrade",
                    message=instant_response,
                    confidence=confidence,
                    suggested_actions=suggested_actions,
                    follow_up_questions=(
                        [
                            "Quer investigar algum contrato específico?",
                            "Posso ajudar com análise de gastos?",
                        ]
                        if intent.type in [IntentType.GREETING, IntentType.HELP_REQUEST]
                        else None
                    ),
                    requires_input=None,
                    metadata={
                        "intent_type": intent.type.value,
                        "message_id": str(uuid.uuid4()),
                        "timestamp": datetime.now(UTC).isoformat(),
                        "is_demo_mode": False,
                        "processing_time_ms": 0,  # Instant!
                        "instant_response": True,
                        "orchestration": {
                            "target_agent": "drummond",
                            "agent_id": "drummond",
                            "agent_name": "Carlos Drummond de Andrade",
                            "routing_reason": f"Instant response for {intent.type.value}",
                            "confidence": confidence,
                        },
                    },
                )

        # Check if user is asking for specific government data
        portal_data = None
        message_lower = sanitized_message.lower()
        data_keywords = [
            "contratos",
            "gastos",
            "despesas",
            "licitação",
            "fornecedor",
            "servidor",
            "órgão",
            "ministério",
            "prefeitura",
            "cnpj",
            "valor",
            "empresa",
        ]

        should_fetch_data = any(keyword in message_lower for keyword in data_keywords)

        # If user is asking for data and intent suggests investigation/analysis
        # Try to use full Orchestrator (30+ APIs, multi-agent analysis)
        if should_fetch_data and intent.type in [
            IntentType.INVESTIGATE,
            IntentType.ANALYZE,
            IntentType.UNKNOWN,
        ]:
            # Prefer Orchestrator for comprehensive analysis
            if ORCHESTRATOR_AVAILABLE:
                try:
                    logger.info(
                        f"Using InvestigationOrchestrator for comprehensive analysis: {extract_safe_log_message(sanitized_message)}"
                    )

                    # Run full investigation (30+ APIs, multi-agent)
                    investigation_result = await orchestrator.investigate(
                        query=sanitized_message,
                        user_id=current_user.id if current_user else "anonymous",
                        session_id=session_id,
                    )

                    # Store investigation result in portal_data for agent processing
                    portal_data = {
                        "investigation_id": investigation_result.investigation_id,
                        "intent": investigation_result.intent.value,
                        "data": {
                            "type": "investigation",
                            "entities_found": investigation_result.entities_found,
                            "stage_results": investigation_result.stage_results,
                            "total_duration": investigation_result.total_duration_seconds,
                        },
                        "metadata": investigation_result.metadata,
                        "confidence": investigation_result.confidence_score,
                    }

                    logger.info(
                        f"Orchestrator completed: {len(investigation_result.entities_found)} entities found, "
                        f"{len(investigation_result.stage_results)} stages executed"
                    )
                except Exception as e:
                    logger.error(
                        f"Orchestrator failed, falling back to simple integration: {e}"
                    )
                    # Fall back to simple integration
                    try:
                        portal_result = await chat_data_integration.process_user_query(
                            sanitized_message, request.context
                        )
                        if portal_result and portal_result.get("data"):
                            portal_data = portal_result
                    except Exception as e2:
                        logger.warning(f"Simple integration also failed: {e2}")
            else:
                # Orchestrator not available, use simple integration
                try:
                    logger.info(
                        f"Fetching data from Portal da Transparência (Orchestrator not available): {extract_safe_log_message(sanitized_message)}"
                    )
                    portal_result = await chat_data_integration.process_user_query(
                        sanitized_message, request.context
                    )
                    if portal_result and portal_result.get("data"):
                        portal_data = portal_result
                        logger.info(
                            f"Found {portal_result.get('data', {}).get('total', 0)} records from Portal da Transparência"
                        )
                except Exception as e:
                    logger.warning(f"Portal da Transparência integration failed: {e}")

        # Create agent message with Portal data if available
        payload_data = {
            "user_message": sanitized_message,
            "intent": intent.dict(),
            "context": request.context or {},
            "session": session.to_dict(),
        }

        if portal_data:
            payload_data["portal_data"] = portal_data

        agent_message = AgentMessage(
            sender="user",
            recipient=target_agent,
            action="process_chat",
            payload=payload_data,
            context={
                "investigation_id": session.current_investigation_id,
                "user_id": session.user_id,
                "session_id": session_id,
            },
        )

        # Create agent context
        agent_context = AgentContext(
            investigation_id=session.current_investigation_id,
            user_id=session.user_id,
            session_id=session_id,
        )

        # Route to appropriate agent based on intent
        logger.info(f"Target agent: {target_agent}")

        if target_agent == "drummond":
            # Use Drummond for conversational intents
            drummond_loaded = False
            try:
                drummond_agent = await get_drummond_agent()

                if drummond_agent:
                    response = await drummond_agent.process(
                        agent_message, agent_context
                    )
                    drummond_loaded = True
                else:
                    raise Exception("Drummond agent not available")
                agent_id = "drummond"
                agent_name = "Carlos Drummond de Andrade"
                logger.info(f"Drummond response received: {response}")
            except Exception as e:
                logger.error(f"Error processing with Drummond: {e}")
                import traceback

                traceback.print_exc()
                # Fall through to simple responses

            # If Drummond failed, use simple responses
            if not drummond_loaded:
                logger.info("Using fallback responses for conversational intents")

                # Simple responses based on intent
                if intent.type == IntentType.GREETING:
                    message = "Olá! Sou o Cidadão.AI. Como posso ajudá-lo com transparência governamental?"
                elif intent.type == IntentType.HELP_REQUEST:
                    message = "Posso ajudar você a investigar contratos, analisar gastos públicos e detectar anomalias. Experimente perguntar 'quero investigar contratos da saúde'!"
                elif intent.type == IntentType.ABOUT_SYSTEM:
                    message = (
                        "O Cidadão.AI é um sistema multi-agente de inteligência artificial "
                        "para análise de transparência governamental brasileira.\n\n"
                        "**Criador e Idealizador:** Anderson Henrique da Silva\n\n"
                        "**Contexto Acadêmico:** Este projeto é um Trabalho de Conclusão de Curso (TCC) "
                        "desenvolvido no Instituto Federal do Sul de Minas Gerais (IFSULDEMINAS), "
                        "sob orientação da Professora Aracele Garcia de Oliveira Fassbinder.\n\n"
                        "**O que fazemos:** Temos 16 agentes especializados com identidades culturais brasileiras "
                        "(Zumbi, Anita Garibaldi, Tiradentes, Drummond, entre outros) que trabalham juntos para "
                        "investigar contratos públicos, detectar anomalias, analisar gastos e promover a "
                        "transparência governamental.\n\n"
                        "Como posso ajudá-lo hoje?"
                    )
                elif intent.type == IntentType.THANKS:
                    message = "De nada! Estou sempre aqui para ajudar com a transparência pública."
                elif intent.type == IntentType.GOODBYE:
                    message = "Até logo! Volte sempre que precisar de informações sobre gastos públicos."
                else:
                    message = "Interessante sua pergunta! Posso ajudá-lo a investigar contratos ou analisar gastos públicos. O que gostaria de explorar?"

                response = AgentResponse(
                    agent_name="Drummond (Simplificado)",
                    status=AgentStatus.COMPLETED,
                    result={
                        "message": message,
                        "intent_type": intent.type.value,
                        "status": "fallback",
                    },
                    metadata={"confidence": 0.8, "simplified": True},
                )
                agent_id = "drummond"
                agent_name = "Carlos Drummond de Andrade"
        elif target_agent == "abaporu" and (
            intent.type == IntentType.INVESTIGATE
            or (
                intent.type
                in [IntentType.QUESTION, IntentType.UNKNOWN, IntentType.ANALYZE]
                and should_fetch_data
            )
        ):
            # Handle investigation requests with Zumbi
            # This includes explicit INVESTIGATE intents and QUESTION/UNKNOWN intents
            # that contain data-related keywords (contracts, expenses, etc.)
            try:
                logger.info(
                    f"Routing to Zumbi agent (intent: {intent.type}, has_data_keywords: {should_fetch_data})"
                )

                # Extract what to investigate from the message
                search_query = sanitized_message.lower()
                data_source = DataSourceType.CONTRACTS  # Default

                # Detect data source from keywords
                if any(
                    word in search_query
                    for word in ["servidor", "salário", "funcionário"]
                ):
                    data_source = DataSourceType.SERVANTS
                elif any(
                    word in search_query for word in ["despesa", "gasto", "pagamento"]
                ):
                    data_source = DataSourceType.EXPENSES
                elif any(word in search_query for word in ["licitação", "pregão"]):
                    data_source = DataSourceType.BIDDINGS

                # Run investigation with Zumbi agent
                logger.info("Running Zumbi investigation with dados.gov.br integration")

                # Extract organization codes from intent entities if available
                org_codes = None
                if intent.entities and isinstance(intent.entities, dict):
                    # intent.entities is a dict[str, Any], not a list of objects
                    orgs = intent.entities.get("organization", [])
                    if orgs:
                        # Ensure it's a list
                        org_codes = orgs if isinstance(orgs, list) else [orgs]

                # Run investigation with dados.gov.br enabled
                investigation_result = await run_zumbi_investigation(
                    query=sanitized_message,
                    organization_codes=org_codes,
                    enable_open_data=True,  # Always enable dados.gov.br search
                    session_id=session_id,
                    user_id=session.user_id,
                )

                if investigation_result["status"] == "error":
                    # Return error response
                    return ChatResponse(
                        session_id=session_id,
                        agent_id="zumbi",
                        agent_name="Zumbi dos Palmares",
                        message=f"❌ Erro na investigação: {investigation_result['error']}",
                        confidence=0.0,
                        metadata={
                            "status": "error",
                            "error": investigation_result["error"],
                        },
                    )

                # Format response using the integration helper
                message = format_investigation_message(investigation_result)

                # Add suggested actions if anomalies were found
                suggested_actions = []
                if investigation_result["anomalies_found"] > 0:
                    suggested_actions.append("🔍 Ver detalhes das anomalias")
                    suggested_actions.append("📊 Gerar relatório completo")
                    if investigation_result.get("open_data_available"):
                        suggested_actions.append(
                            "📂 Explorar dados abertos relacionados"
                        )
                else:
                    suggested_actions.append("🔎 Refinar busca")
                    suggested_actions.append("📈 Analisar outros períodos")

                response = AgentResponse(
                    agent_name="Zumbi dos Palmares",
                    status=AgentStatus.COMPLETED,
                    result={
                        "message": message,
                        "investigation_summary": {
                            "anomalies_found": investigation_result["anomalies_found"],
                            "records_analyzed": investigation_result[
                                "records_analyzed"
                            ],
                            "open_data_available": investigation_result.get(
                                "open_data_available", False
                            ),
                            "datasets_count": len(
                                investigation_result.get("related_datasets", [])
                            ),
                        },
                        "status": "completed",
                        "suggested_actions": suggested_actions,
                    },
                    metadata={
                        "confidence": 0.9,
                        "investigation_id": session.current_investigation_id,
                        "dados_gov_enabled": True,
                    },
                )
                agent_id = "zumbi"
                agent_name = "Zumbi dos Palmares"

            except Exception as e:
                logger.error(f"Investigation error: {e}")
                response = AgentResponse(
                    agent_name="Sistema",
                    status=AgentStatus.ERROR,
                    result={
                        "message": "Erro ao processar investigação. Por favor, tente novamente.",
                        "error": str(e),
                    },
                    metadata={"confidence": 0.0},
                )
                agent_id = "system"
                agent_name = "Sistema"
        elif target_agent in AGENT_MAP:
            # Handle specialized agents (machado, bonifacio, maria_quiteria, etc.)
            try:
                logger.info(f"Loading specialized agent: {target_agent}")
                specialized_agent = await get_agent_by_name(target_agent)

                if specialized_agent:
                    # Process with specialized agent
                    response = await specialized_agent.process(
                        agent_message, agent_context
                    )
                    agent_id = target_agent
                    agent_name = getattr(
                        specialized_agent, "name", target_agent.title()
                    )
                    logger.info(
                        f"Specialized agent {target_agent} completed successfully"
                    )
                else:
                    # Agent not available - fallback to error
                    raise Exception(f"{target_agent} agent not available")

            except Exception as e:
                logger.error(
                    f"Error processing with {target_agent}: {type(e).__name__}: {e}"
                )
                import traceback

                traceback.print_exc()

                # Fallback response
                response = AgentResponse(
                    agent_name="Sistema",
                    status=AgentStatus.ERROR,
                    result={
                        "message": f"Desculpe, o agente {target_agent} não está disponível no momento. Por favor, tente novamente.",
                        "error": str(e),
                        "agent_requested": target_agent,
                    },
                    metadata={"confidence": 0.0, "fallback": True},
                )
                agent_id = "system"
                agent_name = "Sistema"
        else:
            # Intelligent fallback: Try to fetch Portal data if query contains data keywords
            logger.warning(
                f"No agent handler matched. Target: {target_agent}, Intent: {intent.type}, HasDataKeywords: {should_fetch_data}"
            )

            # If user is asking for data but we haven't fetched it yet, try now
            if should_fetch_data and portal_data is None:
                try:
                    logger.info("Attempting Portal data fetch in fallback handler")
                    portal_result = await chat_data_integration.process_user_query(
                        sanitized_message, request.context
                    )
                    if portal_result and portal_result.get("data"):
                        portal_data = portal_result
                        logger.info(
                            f"Fallback successfully fetched {portal_result.get('data', {}).get('total', 0)} records"
                        )
                except Exception as e:
                    logger.warning(f"Fallback Portal data fetch failed: {e}")

            # If we have Portal data, return it with a simple message
            if portal_data and portal_data.get("data"):
                data_info = portal_data.get("data", {})
                total_records = data_info.get("total", 0)
                data_type = portal_data.get("data_type", "dados")

                message = f"Encontrei {total_records} registros de {data_type}. "
                if total_records > 0:
                    message += (
                        "Os dados foram coletados do Portal da Transparência Federal. "
                    )
                    message += "Posso analisar esses dados em busca de anomalias ou padrões suspeitos. "
                    message += "Gostaria de uma análise detalhada?"
                else:
                    message += (
                        "Não encontrei registros para os critérios especificados. "
                    )
                    message += (
                        "Tente ajustar sua busca ou consultar outro período/órgão."
                    )

                response = AgentResponse(
                    agent_name="Sistema de Dados",
                    status=AgentStatus.COMPLETED,
                    result={
                        "message": message,
                        "data_summary": {
                            "total": total_records,
                            "type": data_type,
                            "source": "Portal da Transparência",
                        },
                        "status": "data_fetched",
                    },
                    metadata={"confidence": 0.7, "has_portal_data": True},
                )
                agent_id = "system"
                agent_name = "Sistema de Dados"
            else:
                # No data available - return maintenance message
                debug_info = ""
                if target_agent == "drummond":
                    debug_info = " (Drummond not initialized)"
                elif should_fetch_data:
                    debug_info = " (Portal data not available)"

                response = AgentResponse(
                    agent_name="Sistema",
                    status=AgentStatus.COMPLETED,
                    result={
                        "message": f"Desculpe, estou em manutenção. Por favor, tente novamente em alguns instantes.{debug_info}",
                        "status": "maintenance",
                        "debug": (
                            "Drummond not available"
                            if target_agent == "drummond"
                            else "No data handler available"
                        ),
                    },
                    metadata={"confidence": 0.0},
                )
                agent_id = "system"
                agent_name = "Sistema"

        # Save to chat history (use sanitized message for security)
        await chat_service.save_message(
            session_id=session_id, role="user", content=sanitized_message
        )

        # Get content from response
        response_content = (
            response.result if hasattr(response, "result") else str(response)
        )

        await chat_service.save_message(
            session_id=session_id,
            role="assistant",
            content=response_content,
            agent_id=agent_id,
        )

        # Prepare suggested actions based on response
        suggested_actions = []

        # Check if response has custom suggested actions
        if hasattr(response, "result") and isinstance(response.result, dict):
            custom_actions = response.result.get("suggested_actions", [])
            if custom_actions:
                suggested_actions = custom_actions

        # Fall back to default actions if no custom ones
        if not suggested_actions:
            if (
                intent.type == IntentType.INVESTIGATE
                and not session.current_investigation_id
            ):
                suggested_actions = [
                    "start_investigation",
                    "view_examples",
                    "learn_more",
                ]
            elif session.current_investigation_id:
                suggested_actions = [
                    "view_progress",
                    "generate_report",
                    "new_investigation",
                ]

        # Extract message from response
        if hasattr(response, "result") and isinstance(response.result, dict):
            message_text = response.result.get("message", str(response.result))
            requires_input = response.result.get("requires_input")
        elif hasattr(response, "result"):
            message_text = str(response.result)
            requires_input = None
        else:
            message_text = str(response)
            requires_input = None

        # If we have Portal data and no agent processed it, use the Portal response
        if portal_data and portal_data.get("response") and agent_id == "system":
            message_text = portal_data["response"]
            agent_id = "portal_transparencia"
            agent_name = "Portal da Transparência"

        # CRITICAL: Validate message is not empty
        if not message_text or len(message_text.strip()) < 5:
            logger.error(
                f"Empty or invalid message detected! Agent: {agent_id}, Response: {response}, "
                f"Intent: {intent.type}, Portal data: {bool(portal_data)}"
            )

            # Generate intelligent fallback based on intent
            if intent.type == IntentType.GREETING:
                message_text = (
                    "Olá! Sou o Cidadão.AI, seu assistente para análise de transparência governamental. "
                    "Posso ajudar você a investigar contratos, analisar gastos públicos, detectar anomalias "
                    "em licitações, ou gerar relatórios detalhados. O que você gostaria de explorar?"
                )
            elif intent.type == IntentType.INVESTIGATE:
                message_text = (
                    "Entendo que você quer investigar algo. Para que eu possa ajudar melhor, "
                    "você poderia ser mais específico? Por exemplo: 'Quero investigar contratos do "
                    "Ministério da Saúde em 2024' ou 'Analisar gastos da Educação com fornecedor X'."
                )
            elif intent.type == IntentType.HELP_REQUEST:
                message_text = (
                    "Posso ajudar você de várias formas:\n\n"
                    "🔍 **Investigações**: Analiso contratos, licitações e gastos públicos\n"
                    "📊 **Detecção de Anomalias**: Identifico padrões suspeitos e irregularidades\n"
                    "📝 **Relatórios**: Gero documentos detalhados sobre suas investigações\n"
                    "📈 **Análises Estatísticas**: Forneço insights sobre tendências e padrões\n\n"
                    "Experimente perguntar: 'Quero investigar contratos da saúde' ou 'Mostre anomalias recentes'"
                )
            else:
                message_text = (
                    "Estou processando sua solicitação. Enquanto isso, posso ajudar você com:\n\n"
                    "• Investigação de contratos e licitações públicas\n"
                    "• Análise de gastos e despesas governamentais\n"
                    "• Detecção de anomalias e irregularidades\n"
                    "• Geração de relatórios detalhados\n\n"
                    "Por favor, reformule sua pergunta de forma mais específica para que eu possa ajudar melhor."
                )

        # Build comprehensive metadata
        start_time = datetime.now(UTC)
        processing_time = (
            response.metadata.get("processing_time", 0)
            if hasattr(response, "metadata")
            else 0
        )

        # Check if we have real API key configured
        settings = get_settings()
        has_transparency_key = bool(settings.transparency_api_key)

        metadata = {
            # Basic info
            "intent_type": intent.type.value,
            "message_id": str(uuid.uuid4()),
            "timestamp": start_time.isoformat(),
            "is_demo_mode": not has_transparency_key,  # False if API key configured
            # Processing details
            "processing_time_ms": processing_time,
            "model_used": "maritaca-sabia-3",  # TODO: Get from actual LLM config
            "tokens_used": (
                response.metadata.get("tokens_used", 0)
                if hasattr(response, "metadata")
                else 0
            ),
            # Orchestration info
            "orchestration": {
                "target_agent": target_agent,
                "agent_id": agent_id,
                "agent_name": agent_name,
                "routing_reason": f"Intent {intent.type.value} routed to {target_agent}",
                "confidence": (
                    response.metadata.get("confidence", intent.confidence)
                    if hasattr(response, "metadata")
                    else intent.confidence
                ),
            },
            # Request context
            "session_info": {
                "session_id": session_id,
                "investigation_id": session.current_investigation_id,
                "user_id": session.user_id if session.user_id else "anonymous",
            },
        }

        # Add Portal da Transparência data to metadata if available
        if portal_data:
            metadata["portal_data"] = {
                "type": portal_data.get("data_type"),
                "entities_found": portal_data.get("entities", {}),
                "total_records": (
                    portal_data.get("data", {}).get("total", 0)
                    if portal_data.get("data")
                    else 0
                ),
                "has_data": bool(portal_data.get("data")),
            }

        # Add follow-up questions based on intent
        follow_up_questions = []
        if intent.type == IntentType.GREETING:
            follow_up_questions = [
                "Você gostaria de iniciar uma investigação?",
                "Quer saber sobre algum órgão específico?",
                "Precisa de ajuda para navegar no sistema?",
            ]
        elif intent.type == IntentType.INVESTIGATE:
            follow_up_questions = [
                "Gostaria de filtrar por período específico?",
                "Quer incluir análise de anomalias?",
                "Precisa de um relatório detalhado?",
            ]

        return ChatResponse(
            session_id=session_id,
            message_id=metadata.get("message_id"),
            agent_id=agent_id,
            agent_name=agent_name,
            message=message_text,
            confidence=(
                response.metadata.get("confidence", intent.confidence)
                if hasattr(response, "metadata")
                else intent.confidence
            ),
            suggested_actions=suggested_actions,
            follow_up_questions=follow_up_questions,
            requires_input=requires_input,
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar mensagem")


@router.post("/stream")
async def stream_message(request: ChatRequest):
    """
    Stream chat response using Server-Sent Events (SSE)
    """

    # Sanitize input message before processing
    validation = sanitize_message(request.message)
    sanitized_message = validation.sanitized_message

    # Handle edge cases with streaming responses
    if validation.status != MessageValidationStatus.VALID:
        edge_response = get_edge_case_response(validation.status)
        if edge_response and validation.suggested_response:

            async def edge_case_generator():
                yield f"data: {json_utils.dumps({'type': 'start', 'timestamp': datetime.now(UTC).isoformat()})}\n\n"
                yield f"data: {json_utils.dumps({'type': 'edge_case', 'status': validation.status.value})}\n\n"

                # Stream the response in chunks
                response_text = validation.suggested_response
                words = response_text.split()
                chunk = ""
                for i, word in enumerate(words):
                    chunk += word + " "
                    if i % 4 == 0:
                        yield f"data: {json_utils.dumps({'type': 'chunk', 'content': chunk.strip()})}\n\n"
                        chunk = ""
                        await asyncio.sleep(0.05)
                if chunk:
                    yield f"data: {json_utils.dumps({'type': 'chunk', 'content': chunk.strip()})}\n\n"

                yield f"data: {json_utils.dumps({'type': 'complete', 'agent_id': 'drummond', 'agent_name': 'Carlos Drummond de Andrade', 'edge_case': True, 'suggested_actions': edge_response.get('suggested_actions', [])})}\n\n"

            return EventSourceResponse(edge_case_generator())

    async def generate():
        try:
            # Send initial event
            yield f"data: {json_utils.dumps({'type': 'start', 'timestamp': datetime.now(UTC).isoformat()})}\n\n"

            # Detect intent using NEW keyword-based classifier
            yield f"data: {json_utils.dumps({'type': 'detecting', 'message': 'Analisando sua mensagem...'})}\n\n"
            await asyncio.sleep(0.5)

            # Detect intent using keyword-based classifier
            intent_type_str = "unknown"
            confidence = 0.5

            try:
                if intent_classifier is not None:
                    intent_result = await intent_classifier.classify(sanitized_message)
                    detected_intent = intent_result["intent"]
                    confidence = intent_result["confidence"]

                    # Convert InvestigationIntent to string for routing
                    if detected_intent in [
                        InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
                        InvestigationIntent.SUPPLIER_INVESTIGATION,
                        InvestigationIntent.CORRUPTION_INDICATORS,
                        InvestigationIntent.BUDGET_ANALYSIS,
                        InvestigationIntent.HEALTH_BUDGET_ANALYSIS,
                        InvestigationIntent.EDUCATION_PERFORMANCE,
                    ]:
                        intent_type_str = "investigate"
                    else:
                        intent_type_str = (
                            detected_intent.value
                            if hasattr(detected_intent, "value")
                            else str(detected_intent)
                        )
            except Exception as e:
                logger.error(f"Error in streaming intent classification: {e}")

            # Create simple intent object for compatibility
            class Intent:
                def __init__(self, type_str: str, conf: float):
                    self.type = (
                        IntentType(type_str)
                        if type_str in [e.value for e in IntentType]
                        else IntentType.UNKNOWN
                    )
                    self.confidence = conf

            intent = Intent(intent_type_str, confidence)

            yield f"data: {json_utils.dumps({'type': 'intent', 'intent': intent.type.value, 'confidence': intent.confidence})}\n\n"

            # Use centralized agent routing (single source of truth)
            agent_id, agent_name = resolve_agent_id(
                requested_agent_id=request.agent_id,
                intent_type=intent.type.value,
                intent_confidence=intent.confidence,
            )

            logger.info(f"Stream routing: intent={intent.type.value}, agent={agent_id}")

            yield f"data: {json_utils.dumps({'type': 'agent_selected', 'agent_id': agent_id, 'agent_name': agent_name})}\n\n"
            await asyncio.sleep(0.1)

            # ================================================================
            # SHORT-CIRCUIT: Instant responses for simple intents (Dec 2025)
            # Also intercepts questions about project stakeholders
            # ================================================================
            if (
                intent.confidence >= 0.7 and request.agent_id is None
            ) or _needs_verified_response(sanitized_message):
                instant_response = get_instant_response(intent.type, sanitized_message)
                if instant_response:
                    logger.info(
                        f"Using instant streaming response for intent: {intent.type.value}"
                    )

                    # Stream the response in chunks for natural effect
                    words = instant_response.split()
                    chunk = ""
                    for i, word in enumerate(words):
                        chunk += word + " "
                        if i % 4 == 3:  # Send every 4 words
                            yield f"data: {json_utils.dumps({'type': 'chunk', 'content': chunk.strip()})}\n\n"
                            chunk = ""
                            await asyncio.sleep(0.03)  # Very fast streaming

                    if chunk:
                        yield f"data: {json_utils.dumps({'type': 'chunk', 'content': chunk.strip()})}\n\n"

                    # Send completion
                    yield f"data: {json_utils.dumps({'type': 'complete', 'agent_id': agent_id, 'agent_name': agent_name, 'instant_response': True, 'suggested_actions': ['start_investigation', 'learn_more']})}\n\n"
                    return  # Exit the generator early

            # Check if this is a contract search query that should use real data
            is_contract_search = _is_contract_search_query(
                sanitized_message, intent.type
            )

            # If contract search intent and investigative service available, use real data
            if (
                is_contract_search
                and INVESTIGATIVE_SERVICE_AVAILABLE
                and investigative_service
            ):
                yield f"data: {json_utils.dumps({'type': 'thinking', 'message': f'{agent_name} está buscando contratos reais...'})}\n\n"

                # Stream real contract search
                contracts_found = []
                async for event in investigative_service.search_contracts_streaming(
                    message=sanitized_message,
                    max_results=5,
                ):
                    # Forward search events
                    if event["type"] in ["thinking", "searching", "found"]:
                        yield f"data: {json_utils.dumps(event)}\n\n"
                    elif event["type"] == "contract":
                        contracts_found.append(event["data"])
                        yield f"data: {json_utils.dumps(event)}\n\n"
                    elif event["type"] == "complete":
                        yield f"data: {json_utils.dumps(event)}\n\n"

                # Generate agent summary if contracts found
                if contracts_found:
                    total_value = sum(c.get("valor", 0) for c in contracts_found)
                    summary = (
                        f"Encontrei {len(contracts_found)} contratos "
                        f"totalizando R$ {total_value:,.2f}. "
                        f"Você pode baixar os dados completos nos formatos JSON, CSV ou TXT."
                    )
                    yield f"data: {json_utils.dumps({'type': 'chunk', 'content': summary})}\n\n"
                    yield f"data: {json_utils.dumps({'type': 'complete', 'agent_id': agent_id, 'agent_name': agent_name, 'contracts': contracts_found, 'download_available': True, 'suggested_actions': ['download_json', 'download_csv', 'analyze_anomalies']})}\n\n"
                else:
                    yield f"data: {json_utils.dumps({'type': 'chunk', 'content': 'Não encontrei contratos com esses critérios. Tente refinar sua busca.'})}\n\n"
                    yield f"data: {json_utils.dumps({'type': 'complete', 'agent_id': agent_id, 'agent_name': agent_name, 'suggested_actions': ['try_again', 'change_filters']})}\n\n"

            # Use DSPy for personality-based responses if available
            elif DSPY_AVAILABLE and dspy_service:
                yield f"data: {json_utils.dumps({'type': 'thinking', 'message': f'{agent_name} está pensando...'})}\n\n"

                # Stream response from DSPy agent
                async for chunk_data in dspy_service.chat_stream(
                    agent_id=agent_id,
                    message=sanitized_message,
                    intent_type=intent.type.value,
                    context="",
                ):
                    if chunk_data.get("type") == "chunk":
                        yield f"data: {json_utils.dumps(chunk_data)}\n\n"
                        await asyncio.sleep(0.05)
                    elif chunk_data.get("type") == "complete":
                        yield f"data: {json_utils.dumps({'type': 'complete', 'agent_id': agent_id, 'agent_name': agent_name, 'suggested_actions': ['start_investigation', 'learn_more']})}\n\n"
            else:
                # Fallback to static response if DSPy not available
                response_text = f"Olá! Sou {agent_name} e vou ajudá-lo com sua solicitação sobre {intent.type.value}."

                # Send response in chunks
                words = response_text.split()
                chunk = ""
                for i, word in enumerate(words):
                    chunk += word + " "
                    if i % 3 == 0:  # Send every 3 words
                        yield f"data: {json_utils.dumps({'type': 'chunk', 'content': chunk.strip()})}\n\n"
                        chunk = ""
                        await asyncio.sleep(0.1)

                if chunk:  # Send remaining words
                    yield f"data: {json_utils.dumps({'type': 'chunk', 'content': chunk.strip()})}\n\n"

                # Send completion
                yield f"data: {json_utils.dumps({'type': 'complete', 'suggested_actions': ['start_investigation', 'learn_more']})}\n\n"

        except Exception as e:
            logger.error(f"Stream error: {str(e)}", exc_info=True)
            yield f"data: {json_utils.dumps({'type': 'error', 'message': str(e), 'fallback_endpoint': '/api/v1/chat/message'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/suggestions")
async def get_suggestions() -> list[QuickAction]:
    """
    Get quick action suggestions for the chat
    """
    return [
        QuickAction(
            id="investigate",
            label="Investigar contratos",
            icon="search",
            action="Quero investigar contratos do Ministério da Saúde",
        ),
        QuickAction(
            id="anomalies",
            label="Ver anomalias recentes",
            icon="alert-circle",
            action="Mostre as principais anomalias detectadas",
        ),
        QuickAction(
            id="report",
            label="Gerar relatório",
            icon="file-text",
            action="Gere um relatório das últimas investigações",
        ),
        QuickAction(
            id="help",
            label="Como funciona?",
            icon="help-circle",
            action="Como o Cidadão.AI funciona?",
        ),
    ]


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str, limit: int = 50, current_user=Depends(get_current_optional_user)
) -> dict[str, Any]:
    """
    Get chat history for a session
    """
    session = await chat_service.get_session(session_id)

    # Verify user has access to this session
    if session.user_id and current_user and session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    messages = await chat_service.get_session_messages(session_id, limit)

    return {
        "session_id": session_id,
        "messages": messages,
        "total_messages": len(messages),
        "current_investigation_id": session.current_investigation_id,
    }


@router.get("/history/{session_id}/paginated")
async def get_chat_history_paginated(
    session_id: str,
    cursor: str | None = None,
    limit: int = 50,
    direction: str = "prev",
    current_user=Depends(get_current_optional_user),
) -> CursorPaginationResponse[dict[str, Any]]:
    """
    Get paginated chat history using cursor pagination.

    This is more efficient for large chat histories and real-time updates.

    Args:
        session_id: Session identifier
        cursor: Pagination cursor from previous request
        limit: Number of messages per page (max: 100)
        direction: "next" for newer messages, "prev" for older (default)
    """
    session = await chat_service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    # Verify user has access to this session
    if session.user_id and current_user and session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    # Get paginated messages
    paginated_response = await chat_service.get_session_messages_paginated(
        session_id=session_id,
        cursor=cursor,
        limit=min(limit, 100),  # Cap at 100
        direction=direction,
    )

    # Add session info to metadata
    paginated_response.metadata.update(
        {
            "session_id": session_id,
            "investigation_id": session.current_investigation_id,
            "session_created": session.created_at.isoformat() if session else None,
        }
    )

    return paginated_response


@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str, current_user=Depends(get_current_optional_user)
) -> dict[str, str]:
    """
    Clear chat history for a session
    """
    session = await chat_service.get_session(session_id)

    # Verify user has access
    if session.user_id and current_user and session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    await chat_service.clear_session(session_id)

    return {"message": "Histórico limpo com sucesso"}


@router.get("/cache/stats")
async def get_cache_stats(
    current_user=Depends(get_current_optional_user),
) -> dict[str, Any]:
    """
    Get cache statistics (admin only in production)
    """
    try:
        return await chat_service.get_cache_stats()
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"error": "Unable to get cache statistics"}


@router.get("/agents")
async def get_available_agents() -> list[dict[str, Any]]:
    """
    Get list of available agents for chat
    """
    return [
        {
            "id": "abaporu",
            "name": "Abaporu",
            "avatar": "🎨",
            "role": "Orquestrador Master",
            "description": "Coordena investigações complexas",
            "status": "active",
        },
        {
            "id": "zumbi",
            "name": "Zumbi dos Palmares",
            "avatar": "🔍",
            "role": "Investigador",
            "description": "Detecta anomalias e irregularidades",
            "status": "active",
        },
        {
            "id": "anita",
            "name": "Anita Garibaldi",
            "avatar": "📊",
            "role": "Analista",
            "description": "Analisa padrões e tendências",
            "status": "active",
        },
        {
            "id": "tiradentes",
            "name": "Tiradentes",
            "avatar": "📝",
            "role": "Relator",
            "description": "Gera relatórios detalhados",
            "status": "active",
        },
        {
            "id": "machado",
            "name": "Machado de Assis",
            "avatar": "📚",
            "role": "Analista Textual",
            "description": "Analisa documentos e contratos",
            "status": "active",
        },
        {
            "id": "dandara",
            "name": "Dandara",
            "avatar": "⚖️",
            "role": "Justiça Social",
            "description": "Avalia equidade e inclusão",
            "status": "active",
        },
    ]


@router.get("/debug/drummond-status")
async def debug_drummond_status():
    """Debug endpoint to check Drummond agent status"""
    return {
        "drummond_initialized": True,  # Factory handles initialization
        "drummond_error": None,
        "drummond_type": "Factory managed",
        "has_process_method": True,
        "intent_types_for_drummond": [
            "GREETING",
            "CONVERSATION",
            "HELP_REQUEST",
            "ABOUT_SYSTEM",
            "SMALLTALK",
            "THANKS",
            "GOODBYE",
        ],
    }


@router.get("/test-portal/{query}")
async def test_portal_integration(query: str):
    """
    Test endpoint to verify Portal da Transparência integration
    Example: /api/v1/chat/test-portal/contratos%20ministerio%20saude
    """
    try:
        result = await chat_data_integration.process_user_query(query)
        return {
            "success": True,
            "query": query,
            "data_type": result.get("data_type"),
            "entities_found": result.get("entities"),
            "total_records": (
                result.get("data", {}).get("total", 0) if result.get("data") else 0
            ),
            "response": result.get("response"),
            "sample_data": (
                result.get("data", {}).get("dados", [])[:3]
                if result.get("data")
                else []
            ),
        }
    except Exception as e:
        return {"success": False, "query": query, "error": str(e)}


@router.get("/debug/portal-status")
async def debug_portal_status():
    """Debug endpoint to check Portal da Transparência configuration"""
    import os

    from src.core.config import settings

    # Check environment variable
    env_key = os.getenv("TRANSPARENCY_API_KEY")

    # Check settings
    settings_key = None
    if hasattr(settings, "transparency_api_key") and settings.transparency_api_key:
        settings_key = "Configured"

    # Check service
    service_key = None
    if (
        hasattr(chat_data_integration, "portal")
        and chat_data_integration.portal.api_key
    ):
        service_key = "Loaded"

    return {
        "env_variable": "Found" if env_key else "Not Found",
        "settings_config": settings_key or "Not Configured",
        "service_loaded": service_key or "Not Loaded",
        "portal_base_url": (
            chat_data_integration.portal.BASE_URL
            if hasattr(chat_data_integration, "portal")
            else "Not initialized"
        ),
    }


# ============================================================================
# DIRECT MARITACA.AI CHAT ENDPOINTS
# ============================================================================


@router.post("/direct/maritaca", response_model=MaritacaChatResponse)
async def chat_with_maritaca_direct(
    request: MaritacaChatRequest,
    current_user=Depends(get_current_optional_user),
) -> MaritacaChatResponse:
    """
    Direct chat completion with Maritaca.ai language model.

    This endpoint provides unfiltered access to Maritaca.ai's language models
    for testing, benchmarking, and partnership demonstrations.

    **Use Cases**:
    - Testing Maritaca.ai model capabilities
    - Comparing responses with other LLM providers
    - Demonstrating Brazilian Portuguese language understanding
    - Partnership evaluation and benchmarking

    **Features**:
    - Direct access to Sabiá-3 and Sabiazinho-3 models
    - Temperature control for response creativity
    - Token limit configuration
    - Non-streaming synchronous responses

    **Request Example**:
    ```json
    {
      "messages": [
        {"role": "system", "content": "Você é um assistente útil."},
        {"role": "user", "content": "Explique licitações públicas no Brasil"}
      ],
      "temperature": 0.7,
      "max_tokens": 1024
    }
    ```

    **Response Example**:
    ```json
    {
      "id": "maritaca-1234567890",
      "model": "sabiazinho-3",
      "content": "Licitações públicas são processos...",
      "usage": {
        "prompt_tokens": 25,
        "completion_tokens": 150,
        "total_tokens": 175
      },
      "created_at": "2025-10-28T15:30:00Z",
      "finish_reason": "stop"
    }
    ```

    Args:
        request: Chat request with messages and parameters
        current_user: Optional authenticated user

    Returns:
        Chat completion response with content and metadata

    Raises:
        HTTPException: If Maritaca API is unavailable or request fails
    """
    try:
        maritaca_service = get_maritaca_service()

        logger.info(
            f"Direct Maritaca chat request: {len(request.messages)} messages, "
            f"user={current_user.id if current_user else 'anonymous'}"
        )

        response = await maritaca_service.chat_completion(request)

        logger.info(
            f"Direct Maritaca response: {len(response.content)} chars, "
            f"tokens={response.usage.get('total_tokens') if response.usage else 'unknown'}"
        )

        return response

    except Exception as e:
        logger.error(f"Direct Maritaca chat failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao comunicar com Maritaca.ai: {str(e)}",
        )


@router.post("/direct/maritaca/stream")
async def chat_with_maritaca_stream(
    request: MaritacaChatRequest,
    current_user=Depends(get_current_optional_user),
):
    """
    Streaming chat completion with Maritaca.ai language model.

    Returns Server-Sent Events (SSE) stream for real-time response generation.

    **Use Cases**:
    - Real-time chat interfaces
    - Live response generation
    - Better user experience for long responses

    **Features**:
    - Server-Sent Events (SSE) streaming
    - Real-time token generation
    - Progressive content delivery
    - Lower perceived latency

    **Example cURL**:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/chat/direct/maritaca/stream" \\
      -H "Content-Type: application/json" \\
      -d '{
        "messages": [
          {"role": "user", "content": "Conte uma história sobre transparência"}
        ],
        "stream": true
      }' \\
      --no-buffer
    ```

    Args:
        request: Chat request with messages and streaming enabled
        current_user: Optional authenticated user

    Returns:
        StreamingResponse with SSE events

    Raises:
        HTTPException: If Maritaca API is unavailable or request fails
    """

    async def generate_stream():
        """Generate SSE stream from Maritaca API."""
        try:
            maritaca_service = get_maritaca_service()

            logger.info(
                f"Direct Maritaca streaming: {len(request.messages)} messages, "
                f"user={current_user.id if current_user else 'anonymous'}"
            )

            # Force streaming mode
            request.stream = True

            async for chunk in maritaca_service.chat_completion_stream(request):
                # Send as SSE event
                yield f"data: {json_utils.dumps({'content': chunk})}\n\n"

            # Send completion marker
            yield f"data: {json_utils.dumps({'done': True})}\n\n"

            logger.info("Direct Maritaca streaming completed")

        except Exception as e:
            logger.error(f"Direct Maritaca streaming failed: {e}")
            error_data = {"error": str(e), "done": True}
            yield f"data: {json_utils.dumps(error_data)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/direct/maritaca/health")
async def maritaca_health_check() -> dict[str, Any]:
    """
    Check Maritaca.ai API health and availability.

    Useful for monitoring, debugging, and partnership demonstrations.

    **Response Example**:
    ```json
    {
      "status": "healthy",
      "model": "sabiazinho-3",
      "api_base": "https://chat.maritaca.ai/api",
      "response_received": true,
      "checked_at": "2025-10-28T15:30:00Z"
    }
    ```

    Returns:
        Health status information

    Raises:
        HTTPException: If health check fails
    """
    try:
        maritaca_service = get_maritaca_service()
        health_status = await maritaca_service.health_check()
        return health_status

    except Exception as e:
        logger.error(f"Maritaca health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Maritaca API não disponível: {str(e)}",
        )


@router.get("/direct/maritaca/models")
async def list_maritaca_models() -> dict[str, Any]:
    """
    List available Maritaca.ai models for frontend model selector.

    Returns information about available models including:
    - Model ID and name
    - Context window size
    - Recommended use cases
    - Pricing tier
    - Performance characteristics

    **Response Example**:
    ```json
    {
      "models": [
        {
          "id": "sabiazinho-3",
          "name": "Sabiazinho-3",
          "description": "Fast, efficient model for general use",
          "context_window": 8192,
          "recommended_for": ["chat", "quick_responses", "general_qa"],
          "tier": "standard",
          "is_default": true
        },
        {
          "id": "sabia-3",
          "name": "Sabiá-3",
          "description": "Most capable model with advanced reasoning",
          "context_window": 32768,
          "recommended_for": ["analysis", "complex_reasoning", "long_context"],
          "tier": "premium",
          "is_default": false
        }
      ],
      "default_model": "sabiazinho-3"
    }
    ```

    Returns:
        List of available models with metadata

    Note:
        Frontend can use this to populate a model selector dropdown
    """
    settings = get_settings()

    models = [
        {
            "id": "sabiazinho-3",
            "name": "Sabiazinho-3",
            "description": "Modelo rápido e eficiente para uso geral",
            "context_window": 8192,
            "recommended_for": ["chat", "respostas_rapidas", "perguntas_gerais"],
            "tier": "standard",
            "is_default": settings.maritaca_model == "sabiazinho-3",
            "icon": "⚡",
            "color": "#00D9FF",
        },
        {
            "id": "sabia-3",
            "name": "Sabiá-3",
            "description": "Modelo mais avançado com raciocínio complexo",
            "context_window": 32768,
            "recommended_for": ["analise", "raciocinio_complexo", "contexto_longo"],
            "tier": "premium",
            "is_default": settings.maritaca_model == "sabia-3",
            "icon": "🧠",
            "color": "#FF6B35",
        },
    ]

    return {
        "models": models,
        "default_model": settings.maritaca_model,
        "provider": "maritaca",
        "provider_name": "Maritaca AI",
        "provider_url": "https://maritaca.ai",
    }
