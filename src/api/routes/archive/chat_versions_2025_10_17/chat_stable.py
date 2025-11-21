"""
Stable Chat API with multiple fallback layers
Ensures 100% availability with Maritaca AI integration
"""

import os
from datetime import UTC, datetime
from typing import Any, Optional

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.core import get_logger

logger = get_logger(__name__)
from src.services.chat_data_integration import chat_data_integration
from src.services.chat_service import IntentDetector, IntentType
from src.services.maritaca_client import MaritacaClient, MaritacaModel

router = APIRouter(prefix="/api/v1/chat")


@router.get("/health")
async def chat_stable_health():
    """Simple health check for chat stable router"""
    return {"status": "ok", "router": "chat_stable", "portal_integration": "enabled"}


# Initialize services with lazy loading
maritaca_client = None
intent_detector = None


def get_maritaca_client():
    """Lazy load Maritaca client"""
    global maritaca_client
    if maritaca_client is None:
        api_key = os.getenv("MARITACA_API_KEY")
        if api_key:
            maritaca_client = MaritacaClient(
                api_key=api_key,
                model=MaritacaModel.SABIAZINHO_3,  # Using efficient model for cost optimization
            )
    return maritaca_client


def get_intent_detector():
    """Lazy load intent detector"""
    global intent_detector
    if intent_detector is None:
        intent_detector = IntentDetector()
    return intent_detector


# Request/Response models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    context: Optional[dict[str, Any]] = None


class ChatResponse(BaseModel):
    session_id: str
    agent_id: str
    agent_name: str
    message: str
    confidence: float
    suggested_actions: Optional[list[str]] = None
    metadata: dict[str, Any] = {}


# Fallback responses for different scenarios
FALLBACK_RESPONSES = {
    IntentType.GREETING: [
        "Olá! Sou seu assistente de transparência pública. Como posso ajudar você hoje?",
        "Oi! Estou aqui para ajudar com informações sobre gastos governamentais. Em que posso ser útil?",
        "Bem-vindo! Posso ajudar você a entender melhor os gastos públicos. O que gostaria de saber?",
    ],
    IntentType.INVESTIGATE: [
        "Entendi que você quer investigar gastos públicos. Posso ajudar você a buscar informações sobre contratos, licitações e despesas governamentais. Qual área específica você gostaria de investigar?",
        "Vou ajudar você a investigar os gastos públicos. Temos dados sobre contratos, fornecedores e órgãos públicos. Por onde gostaria de começar?",
        "Perfeito! Posso analisar contratos e despesas públicas. Me diga qual órgão, período ou tipo de gasto você quer investigar.",
    ],
    IntentType.ANALYZE: [
        "Vou analisar essas informações para você. Nossa plataforma examina padrões de gastos, identifica anomalias e fornece insights sobre transparência pública.",
        "Certo, vou fazer uma análise detalhada. Posso examinar tendências, comparar fornecedores e identificar possíveis irregularidades nos dados públicos.",
        "Entendido! Farei uma análise completa dos dados solicitados, incluindo padrões de gastos e possíveis pontos de atenção.",
    ],
    IntentType.HELP: [
        "Posso ajudar você de várias formas:\n• Investigar contratos e licitações\n• Analisar gastos de órgãos públicos\n• Identificar padrões suspeitos\n• Comparar fornecedores\n• Gerar relatórios de transparência\n\nO que você gostaria de fazer?",
        "Aqui estão algumas coisas que posso fazer:\n• Buscar informações sobre contratos específicos\n• Analisar gastos por órgão ou período\n• Detectar anomalias em pagamentos\n• Rastrear histórico de fornecedores\n\nComo posso ajudar?",
        "Sou especializado em transparência pública. Posso:\n• Investigar despesas governamentais\n• Analisar contratos suspeitos\n• Monitorar licitações\n• Gerar insights sobre gastos públicos\n\nQual informação você precisa?",
    ],
    IntentType.REPORT: [
        "Vou preparar um relatório detalhado com as informações solicitadas. O documento incluirá análises, gráficos e recomendações sobre os dados públicos.",
        "Certo! Prepararei um relatório completo com todos os dados relevantes, incluindo visualizações e insights sobre possíveis irregularidades.",
        "Entendido! Seu relatório será gerado com análise detalhada dos gastos, comparações relevantes e indicadores de transparência.",
    ],
    IntentType.UNKNOWN: [
        "Interessante sua pergunta! Como assistente de transparência pública, posso ajudar com investigações sobre gastos governamentais, contratos e licitações. Como posso ajudar você com isso?",
        "Não tenho certeza se entendi completamente. Posso ajudar você a investigar gastos públicos, analisar contratos ou buscar informações sobre transparência governamental. O que você gostaria de saber?",
        "Hmm, deixe-me reformular. Sou especializado em dados de transparência pública. Posso investigar contratos, analisar gastos de órgãos públicos ou identificar padrões suspeitos. Como posso ser útil?",
    ],
}


def get_fallback_response(
    intent_type: IntentType, context: Optional[dict] = None
) -> str:
    """Get appropriate fallback response based on intent"""
    import random

    responses = FALLBACK_RESPONSES.get(
        intent_type, FALLBACK_RESPONSES[IntentType.UNKNOWN]
    )
    return random.choice(responses)


async def process_with_maritaca(
    message: str,
    intent_type: IntentType,
    session_id: str,
    context: Optional[dict] = None,
) -> dict[str, Any]:
    """Process message with Maritaca AI with multiple fallback layers and Portal da Transparência integration"""

    # Check if user is asking for specific government data
    message_lower = message.lower()
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
    portal_data = None

    # If user is asking for data, fetch from Portal da Transparência
    if should_fetch_data and (
        intent_type in [IntentType.INVESTIGATE, IntentType.ANALYZE, IntentType.UNKNOWN]
    ):
        try:
            logger.info(
                f"Fetching real data from Portal da Transparência for query: {message}"
            )
            portal_result = await chat_data_integration.process_user_query(
                message, context
            )
            if portal_result and portal_result.get("data"):
                portal_data = portal_result
                # If we have data, return the formatted response directly
                if portal_result.get("response"):
                    return {
                        "message": portal_result["response"],
                        "agent_used": "portal_transparencia_ai",
                        "model": "sabiazinho-3",
                        "success": True,
                        "data": portal_result.get("data"),
                        "entities": portal_result.get("entities"),
                        "data_type": portal_result.get("data_type"),
                    }
        except Exception as e:
            logger.warning(f"Portal da Transparência integration failed: {str(e)}")

    # Layer 1: Try Maritaca AI
    client = get_maritaca_client()
    if client:
        try:
            # Prepare context based on intent
            system_prompt = """Você é um assistente especializado em transparência pública brasileira.
            Seu papel é ajudar cidadãos a entender e investigar gastos governamentais.
            Seja claro, objetivo e sempre forneça informações úteis sobre transparência fiscal.
            Quando apropriado, sugira ações específicas como investigar contratos ou analisar gastos."""

            if intent_type == IntentType.INVESTIGATE:
                system_prompt += "\nO usuário quer investigar gastos. Seja específico sobre como você pode ajudar."
            elif intent_type == IntentType.ANALYZE:
                system_prompt += "\nO usuário quer uma análise. Explique que tipo de análise você pode fornecer."

            # Add portal data context if available
            if portal_data and portal_data.get("data"):
                system_prompt += f"\n\nDados reais do Portal da Transparência: {str(portal_data['data'])[:1000]}"

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ]

            response = await client.chat_completion(
                messages=messages, temperature=0.7, max_tokens=300
            )

            if response:
                result = {
                    "message": (
                        response.content
                        if hasattr(response, "content")
                        else str(response)
                    ),
                    "agent_used": "maritaca_ai",
                    "model": (
                        response.model if hasattr(response, "model") else "sabiazinho-3"
                    ),
                    "success": True,
                }
                # Add portal data if available
                if portal_data:
                    result.update(
                        {
                            "data": portal_data.get("data"),
                            "entities": portal_data.get("entities"),
                            "data_type": portal_data.get("data_type"),
                        }
                    )
                return result
        except Exception as e:
            logger.warning(f"Maritaca AI failed: {str(e)}")

    # Layer 2: Try simple HTTP request to Maritaca
    if os.getenv("MARITACA_API_KEY"):
        try:
            async with httpx.AsyncClient(timeout=5.0) as http_client:
                response = await http_client.post(
                    "https://chat.maritaca.ai/api/chat/inference",
                    headers={
                        "authorization": f"Bearer {os.getenv('MARITACA_API_KEY')}"
                    },
                    json={
                        "messages": [{"role": "user", "content": message}],
                        "model": "sabiazinho-3",
                        "temperature": 0.7,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    result = {
                        "message": data.get(
                            "answer", get_fallback_response(intent_type)
                        ),
                        "agent_used": "maritaca_direct",
                        "model": "sabiazinho-3",
                        "success": True,
                    }
                    if portal_data:
                        result.update(
                            {
                                "data": portal_data.get("data"),
                                "entities": portal_data.get("entities"),
                                "data_type": portal_data.get("data_type"),
                            }
                        )
                    return result
        except Exception as e:
            logger.warning(f"Direct Maritaca request failed: {str(e)}")

    # Layer 3: Smart fallback based on intent
    result = {
        "message": get_fallback_response(intent_type, {"session_id": session_id}),
        "agent_used": "fallback_intelligent",
        "model": "rule_based",
        "success": True,
    }
    if portal_data:
        result.update(
            {
                "data": portal_data.get("data"),
                "entities": portal_data.get("entities"),
                "data_type": portal_data.get("data_type"),
            }
        )
    return result


@router.post("/stable", response_model=ChatResponse)
async def chat_stable(request: ChatRequest) -> ChatResponse:
    """
    Ultra-stable chat endpoint with multiple fallback layers
    Guarantees response even if all AI services fail
    """
    session_id = request.session_id or f"session_{datetime.now().timestamp()}"

    try:
        # Detect intent with fallback
        detector = get_intent_detector()
        if detector:
            try:
                intent = await detector.detect(request.message)
                intent_type = intent.type
                confidence = intent.confidence
            except:
                # Fallback intent detection
                message_lower = request.message.lower()
                if any(
                    word in message_lower
                    for word in ["oi", "olá", "bom dia", "boa tarde", "boa noite"]
                ):
                    intent_type = IntentType.GREETING
                elif any(
                    word in message_lower
                    for word in ["investigar", "verificar", "buscar", "procurar"]
                ):
                    intent_type = IntentType.INVESTIGATE
                elif any(
                    word in message_lower
                    for word in ["analisar", "análise", "examinar"]
                ):
                    intent_type = IntentType.ANALYZE
                elif any(
                    word in message_lower for word in ["ajuda", "help", "como", "o que"]
                ):
                    intent_type = IntentType.HELP
                else:
                    intent_type = IntentType.UNKNOWN
                confidence = 0.6
        else:
            intent_type = IntentType.UNKNOWN
            confidence = 0.5

        # Process with Maritaca and fallbacks
        result = await process_with_maritaca(
            message=request.message,
            intent_type=intent_type,
            session_id=session_id,
            context=request.context,
        )

        # Determine agent info based on intent
        agent_info = {
            IntentType.GREETING: ("drummond", "Carlos Drummond"),
            IntentType.INVESTIGATE: ("zumbi", "Zumbi dos Palmares"),
            IntentType.ANALYZE: ("anita", "Anita Garibaldi"),
            IntentType.HELP: ("drummond", "Carlos Drummond"),
            IntentType.REPORT: ("tiradentes", "Tiradentes"),
            IntentType.UNKNOWN: ("drummond", "Carlos Drummond"),
        }

        agent_id, agent_name = agent_info.get(
            intent_type, ("drummond", "Carlos Drummond")
        )

        # Prepare suggested actions
        suggested_actions = {
            IntentType.GREETING: [
                "investigate_contracts",
                "view_recent_expenses",
                "help",
            ],
            IntentType.INVESTIGATE: [
                "filter_by_date",
                "filter_by_agency",
                "view_suppliers",
            ],
            IntentType.ANALYZE: ["generate_report", "view_charts", "compare_periods"],
            IntentType.HELP: ["start_investigation", "learn_more", "examples"],
            IntentType.REPORT: ["download_pdf", "share_report", "new_analysis"],
            IntentType.UNKNOWN: ["help", "examples", "start_investigation"],
        }

        # Build metadata with Portal data if available
        metadata = {
            "intent_type": intent_type.value,
            "processing_time": 0,
            "agent_used": result["agent_used"],
            "model": result["model"],
            "timestamp": datetime.now(UTC).isoformat(),
            "stable_version": True,
        }

        # Add Portal da Transparência data to metadata if available
        if result.get("data"):
            metadata["portal_data"] = {
                "type": result.get("data_type"),
                "entities_found": result.get("entities", {}),
                "total_records": result.get("data", {}).get("total", 0),
                "has_data": True,
            }

        return ChatResponse(
            session_id=session_id,
            agent_id=agent_id,
            agent_name=agent_name,
            message=result["message"],
            confidence=confidence,
            suggested_actions=suggested_actions.get(intent_type, ["help"]),
            metadata=metadata,
        )

    except Exception as e:
        # Ultimate fallback - always return a valid response
        logger.error(f"Critical error in stable chat: {str(e)}")
        return ChatResponse(
            session_id=session_id,
            agent_id="system",
            agent_name="Sistema",
            message="Olá! Sou seu assistente de transparência pública. Estou aqui para ajudar você a investigar gastos governamentais, analisar contratos e entender melhor como o dinheiro público é utilizado. Como posso ajudar?",
            confidence=1.0,
            suggested_actions=["investigate_contracts", "view_expenses", "help"],
            metadata={
                "error": str(e),
                "fallback": "ultimate",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )


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
