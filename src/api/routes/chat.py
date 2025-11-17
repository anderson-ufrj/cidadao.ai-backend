"""
Chat API endpoints for conversational interface
VERSION: 2025-10-17 15:00:00 - Consolidated implementation
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Optional

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
from src.services.chat_data_integration import chat_data_integration
from src.services.chat_service import IntentType
from src.services.maritaca_direct_service import (
    MaritacaChatRequest,
    MaritacaChatResponse,
    get_maritaca_service,
)
from src.services.orchestration.models.investigation import InvestigationIntent
from src.services.orchestration.query_planner.intent_classifier import IntentClassifier

# Initialize logger BEFORE using it
logger = get_logger(__name__)

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
try:
    intent_classifier = IntentClassifier()
    logger.info("IntentClassifier initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize IntentClassifier: {e}")
    intent_classifier = None

# Agent name to import path mapping
AGENT_MAP = {
    "drummond": ("src.agents.drummond", "DrummondAgent"),
    "zumbi": ("src.agents.zumbi", "ZumbiAgent"),
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
    session_id: Optional[str] = None
    context: Optional[dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat message response"""

    session_id: str
    message_id: Optional[str] = None
    agent_id: str
    agent_name: str
    message: str
    confidence: float
    suggested_actions: Optional[list[str]] = None
    follow_up_questions: Optional[list[str]] = None
    requires_input: Optional[dict[str, str]] = None
    metadata: dict[str, Any] = {}


class QuickAction(BaseModel):
    """Quick action suggestion"""

    id: str
    label: str
    icon: str
    action: str


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest, current_user=Depends(get_current_optional_user)
) -> ChatResponse:
    """
    Process a chat message and return agent response
    """
    try:
        # Check if chat service is available
        if chat_service is None:
            logger.error("Chat service not available")
            return {
                "response": "Desculpe, o serviço de chat está temporariamente indisponível.",
                "session_id": request.session_id or str(uuid.uuid4()),
                "message_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "intent": None,
            }

        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        session = await chat_service.get_or_create_session(
            session_id, user_id=current_user.id if current_user else None
        )

        # Detect intent from message using NEW keyword-based classifier
        try:
            if intent_classifier is None:
                raise Exception("IntentClassifier not available")

            intent_result = await intent_classifier.classify(request.message)
            detected_intent = intent_result["intent"]
            confidence = intent_result["confidence"]
            method = intent_result.get("method", "unknown")

            logger.info(
                f"[{method.upper()}] Detected intent: {detected_intent.value} with confidence {confidence:.2f}"
            )

            # Convert InvestigationIntent to old IntentType for compatibility
            # Map investigation intents to IntentType.INVESTIGATE
            if detected_intent in [
                InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
                InvestigationIntent.SUPPLIER_INVESTIGATION,
                InvestigationIntent.CORRUPTION_INDICATORS,
                InvestigationIntent.BUDGET_ANALYSIS,
                InvestigationIntent.HEALTH_BUDGET_ANALYSIS,
                InvestigationIntent.EDUCATION_PERFORMANCE,
            ]:
                intent_type = IntentType.INVESTIGATE
            else:
                intent_type = IntentType.QUESTION

            # Create compatible intent object
            class Intent:
                def __init__(self, type, confidence):
                    self.type = type
                    self.confidence = confidence

            intent = Intent(intent_type, confidence)
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")

            # Fallback to INVESTIGATE for safety
            class Intent:
                def __init__(self, type, confidence):
                    self.type = type
                    self.confidence = confidence

            intent = Intent(IntentType.INVESTIGATE, 0.5)

        # Check if user is asking for specific government data
        portal_data = None
        message_lower = request.message.lower()
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
                        f"Using InvestigationOrchestrator for comprehensive analysis: {request.message}"
                    )

                    # Run full investigation (30+ APIs, multi-agent)
                    investigation_result = await orchestrator.investigate(
                        query=request.message,
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
                            request.message, request.context
                        )
                        if portal_result and portal_result.get("data"):
                            portal_data = portal_result
                    except Exception as e2:
                        logger.warning(f"Simple integration also failed: {e2}")
            else:
                # Orchestrator not available, use simple integration
                try:
                    logger.info(
                        f"Fetching data from Portal da Transparência (Orchestrator not available): {request.message}"
                    )
                    portal_result = await chat_data_integration.process_user_query(
                        request.message, request.context
                    )
                    if portal_result and portal_result.get("data"):
                        portal_data = portal_result
                        logger.info(
                            f"Found {portal_result.get('data', {}).get('total', 0)} records from Portal da Transparência"
                        )
                except Exception as e:
                    logger.warning(f"Portal da Transparência integration failed: {e}")

        # Determine target agent based on intent (uses _get_agent_for_intent mapping)
        target_agent = intent.suggested_agent
        logger.info(
            f"Routing {intent.type.value} → {target_agent} (confidence: {intent.confidence})"
        )

        # Create agent message with Portal data if available
        payload_data = {
            "user_message": request.message,
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
                    message = "O Cidadão.AI é um sistema multi-agente para análise de transparência governamental. Temos agentes especializados em investigação, análise e geração de relatórios."
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
                search_query = request.message.lower()
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
                    query=request.message,
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
                        request.message, request.context
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

        # Save to chat history
        await chat_service.save_message(
            session_id=session_id, role="user", content=request.message
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
        start_time = datetime.utcnow()
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

    async def generate():
        try:
            # Send initial event
            yield f"data: {json_utils.dumps({'type': 'start', 'timestamp': datetime.utcnow().isoformat()})}\n\n"

            # Detect intent using NEW keyword-based classifier
            yield f"data: {json_utils.dumps({'type': 'detecting', 'message': 'Analisando sua mensagem...'})}\n\n"
            await asyncio.sleep(0.5)

            try:
                if intent_classifier is None:
                    raise Exception("IntentClassifier not available")

                intent_result = await intent_classifier.classify(request.message)
                detected_intent = intent_result["intent"]
                confidence = intent_result["confidence"]

                # Convert to IntentType
                if detected_intent in [
                    InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
                    InvestigationIntent.SUPPLIER_INVESTIGATION,
                    InvestigationIntent.CORRUPTION_INDICATORS,
                    InvestigationIntent.BUDGET_ANALYSIS,
                    InvestigationIntent.HEALTH_BUDGET_ANALYSIS,
                    InvestigationIntent.EDUCATION_PERFORMANCE,
                ]:
                    intent_type = IntentType.INVESTIGATE
                else:
                    intent_type = IntentType.QUESTION

                class Intent:
                    def __init__(self, type, confidence):
                        self.type = type
                        self.confidence = confidence

                intent = Intent(intent_type, confidence)
            except Exception as e:
                logger.error(f"Error in streaming intent classification: {e}")

                class Intent:
                    def __init__(self, type, confidence):
                        self.type = type
                        self.confidence = confidence

                intent = Intent(IntentType.INVESTIGATE, 0.5)

            yield f"data: {json_utils.dumps({'type': 'intent', 'intent': intent.type.value, 'confidence': intent.confidence})}\n\n"

            # Select agent
            agent = (
                await chat_service.get_agent_for_intent(intent)
                if chat_service
                else None
            )

            # Check if agent was successfully retrieved
            if not agent:
                logger.warning(f"No agent available for intent: {intent.type}")
                yield f"data: {json_utils.dumps({'type': 'error', 'message': 'Serviço temporariamente indisponível', 'fallback_endpoint': '/api/v1/chat/message'})}\n\n"
                return

            yield f"data: {json_utils.dumps({'type': 'agent_selected', 'agent_id': getattr(agent, 'agent_id', 'unknown'), 'agent_name': getattr(agent, 'name', 'Sistema')})}\n\n"
            await asyncio.sleep(0.3)

            # Process message in chunks (simulate typing)
            agent_name = getattr(agent, "name", "Sistema")
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
    cursor: Optional[str] = None,
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
