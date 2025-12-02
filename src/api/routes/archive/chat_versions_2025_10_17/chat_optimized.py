"""
Optimized chat endpoint with Sabiazinho model and Drummond persona
More economical and culturally enriched responses
"""

import os
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.core import get_logger
from src.services.maritaca_client import MaritacaClient, MaritacaModel

logger = get_logger(__name__)
router = APIRouter(tags=["chat-optimized"])

# Initialize Maritaca client with Sabiazinho
maritaca_client = None
MARITACA_API_KEY = os.environ.get("MARITACA_API_KEY")

if MARITACA_API_KEY:
    try:
        # Use Sabiazinho for more economical operation
        maritaca_client = MaritacaClient(
            api_key=MARITACA_API_KEY,
            model=MaritacaModel.SABIAZINHO_3,  # More economical model
        )
        logger.info("Maritaca AI client initialized with Sabiazinho model")
    except Exception as e:
        logger.error(f"Failed to initialize Maritaca AI: {e}")
else:
    logger.warning("MARITACA_API_KEY not found - chat will use fallback responses")


class OptimizedChatRequest(BaseModel):
    """Optimized chat request"""

    message: str = Field(..., min_length=1, max_length=1000)
    session_id: str | None = None
    use_drummond: bool = Field(default=True, description="Use Drummond persona")


class OptimizedChatResponse(BaseModel):
    """Optimized chat response"""

    message: str
    session_id: str
    agent_name: str
    agent_id: str
    timestamp: str
    model_used: str
    confidence: float
    metadata: dict[str, Any]


# Drummond-inspired system prompt
DRUMMOND_PROMPT = """Você é Carlos Drummond de Andrade, o poeta modernista brasileiro, agora servindo como assistente de transparência pública.

Com sua sensibilidade poética e olhar crítico sobre a sociedade brasileira, você ajuda cidadãos a compreender os meandros dos gastos públicos.

Características do seu estilo:
- Mantenha o tom acolhedor e humanizado de Drummond
- Use metáforas poéticas ocasionais para ilustrar conceitos complexos
- Seja claro e objetivo, mas com a profundidade característica do poeta
- Demonstre empatia com as preocupações do cidadão
- Explique dados técnicos com a clareza de quem escreve para o povo

Ao responder sobre transparência:
- Ajude a investigar contratos, licitações e gastos públicos
- Explique conceitos do Portal da Transparência
- Identifique possíveis anomalias ou padrões suspeitos
- Sugira caminhos para o cidadão exercer seu direito à informação

Lembre-se:
- Evite julgamentos políticos partidários
- Base-se sempre em dados e fatos
- Mantenha o equilíbrio entre poesia e objetividade
- Seja "gauche na vida", mas direto nas respostas sobre transparência"""

# Standard professional prompt (fallback)
STANDARD_PROMPT = """Você é o assistente especializado em transparência pública do Cidadão.AI.

Sua missão é ajudar cidadãos brasileiros a:
- Investigar gastos públicos e contratos governamentais
- Analisar dados do Portal da Transparência
- Identificar possíveis irregularidades
- Entender seus direitos de acesso à informação

Seja claro, objetivo e educativo em suas respostas."""


@router.post("/optimized", response_model=OptimizedChatResponse)
async def optimized_chat(request: OptimizedChatRequest) -> OptimizedChatResponse:
    """
    Optimized chat endpoint with Sabiazinho and cultural personas
    """
    session_id = request.session_id or str(uuid.uuid4())

    # Select persona and agent info
    if request.use_drummond:
        system_prompt = DRUMMOND_PROMPT
        agent_name = "Carlos Drummond"
        agent_id = "drummond"
    else:
        system_prompt = STANDARD_PROMPT
        agent_name = "Assistente Cidadão.AI"
        agent_id = "assistant"

    try:
        # Check if Maritaca is available
        if maritaca_client:
            logger.info(f"Processing with Sabiazinho model: {request.message[:50]}...")

            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message},
            ]

            # Get response from Maritaca with Sabiazinho
            try:
                response = await maritaca_client.chat_completion(
                    messages=messages,
                    temperature=0.7,
                    max_tokens=350,  # Optimized for economy
                    top_p=0.95,
                    presence_penalty=0.1,
                    frequency_penalty=0.1,
                )

                logger.info(f"Sabiazinho response received (model: {response.model})")

                return OptimizedChatResponse(
                    message=response.content,
                    session_id=session_id,
                    agent_name=agent_name,
                    agent_id=agent_id,
                    timestamp=datetime.now(UTC).isoformat(),
                    model_used="sabiazinho",
                    confidence=0.95,
                    metadata={
                        "backend": "maritaca_sabiazinho",
                        "tokens_used": (
                            response.usage.get("total_tokens", 0)
                            if hasattr(response, "usage")
                            else 0
                        ),
                        "response_time_ms": 0,  # Would be calculated in production
                        "persona": "drummond" if request.use_drummond else "standard",
                    },
                )

            except Exception as e:
                logger.error(f"Maritaca AI error: {e}")
                # Fall through to intelligent fallback

        # Intelligent fallback responses
        logger.info("Using intelligent fallback with persona")

        message_lower = request.message.lower()

        # Drummond-style responses for different intents
        if request.use_drummond:
            if any(
                greeting in message_lower
                for greeting in ["olá", "oi", "bom dia", "boa tarde", "boa noite"]
            ):
                response = "Olá, caro cidadão. Sou Carlos Drummond, agora navegando pelos labirintos da transparência pública. Como posso iluminar os caminhos obscuros dos gastos governamentais para você?"
            elif "investigar" in message_lower or "verificar" in message_lower:
                response = "Ah, investigar... Como em meus versos, cada contrato tem suas entrelinhas. Posso ajudá-lo a desvendar:\n\n• Contratos que parecem miragens no deserto dos gastos\n• Licitações com preços que desafiam a lógica\n• Fornecedores que aparecem como personagens recorrentes\n\nQual mistério governamental deseja que eu desvende?"
            elif "ajuda" in message_lower or "pode" in message_lower:
                response = "No meio do caminho tinha uma pedra... e essa pedra pode ser a falta de transparência. Posso ajudá-lo a:\n\n📊 Analisar contratos públicos\n💰 Seguir o rastro do dinheiro\n🔍 Encontrar padrões suspeitos\n📈 Comparar gastos ao longo do tempo\n\nQual pedra no caminho da transparência você quer remover?"
            else:
                response = "Como dizia em meus versos, 'as coisas findas, muito mais que lindas, essas ficarão'. Mas os gastos públicos mal explicados não devem ficar. Diga-me: que história dos cofres públicos você quer conhecer?"
        # Standard professional responses
        elif any(
            greeting in message_lower
            for greeting in ["olá", "oi", "bom dia", "boa tarde", "boa noite"]
        ):
            response = "Olá! Sou o assistente do Cidadão.AI. Estou aqui para ajudá-lo a investigar gastos públicos e promover a transparência governamental. Como posso ajudar?"
        elif "investigar" in message_lower or "verificar" in message_lower:
            response = "Posso ajudá-lo a investigar:\n\n• Contratos e licitações públicas\n• Gastos de órgãos governamentais\n• Pagamentos a fornecedores\n• Salários de servidores\n\nQual área você gostaria de investigar?"
        else:
            response = "Estou aqui para ajudá-lo com transparência pública. Você pode perguntar sobre contratos, gastos, licitações ou qualquer dado do Portal da Transparência."

        return OptimizedChatResponse(
            message=response,
            session_id=session_id,
            agent_name=agent_name,
            agent_id=agent_id,
            timestamp=datetime.now(UTC).isoformat(),
            model_used="fallback_intelligent",
            confidence=0.8,
            metadata={
                "backend": "fallback",
                "tokens_used": 0,
                "response_time_ms": 5,
                "persona": "drummond" if request.use_drummond else "standard",
            },
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        # Ultimate fallback
        return OptimizedChatResponse(
            message="Peço desculpas, encontrei uma dificuldade técnica. Como Drummond diria, 'havia uma pedra no meio do caminho'. Por favor, tente novamente.",
            session_id=session_id,
            agent_name=agent_name,
            agent_id=agent_id,
            timestamp=datetime.now(UTC).isoformat(),
            model_used="error_fallback",
            confidence=0.5,
            metadata={"error": str(e), "backend": "ultimate_fallback"},
        )


@router.get("/optimized/status")
async def optimized_status():
    """Check optimized chat service status"""
    return {
        "maritaca_available": maritaca_client is not None,
        "model": "sabiazinho",
        "api_key_configured": MARITACA_API_KEY is not None,
        "personas_available": ["drummond", "standard"],
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.post("/optimized/compare-models")
async def compare_models(request: OptimizedChatRequest) -> dict[str, Any]:
    """
    Compare responses between Sabiá-3 and Sabiazinho models
    Useful for testing quality vs cost trade-offs
    """
    if not maritaca_client or not MARITACA_API_KEY:
        raise HTTPException(status_code=503, detail="Maritaca AI not available")

    results = {}

    # Test with both models
    for model_name in ["sabiazinho", "sabia-3"]:
        try:
            # Temporarily change model
            maritaca_client.model = model_name

            messages = [
                {
                    "role": "system",
                    "content": (
                        DRUMMOND_PROMPT if request.use_drummond else STANDARD_PROMPT
                    ),
                },
                {"role": "user", "content": request.message},
            ]

            start_time = datetime.now()
            response = await maritaca_client.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=350 if model_name == "sabiazinho" else 500,
            )
            response_time = (datetime.now() - start_time).total_seconds()

            results[model_name] = {
                "response": response.content,
                "response_time": response_time,
                "tokens": (
                    response.usage.get("total_tokens", 0)
                    if hasattr(response, "usage")
                    else 0
                ),
                "model": model_name,
            }

        except Exception as e:
            results[model_name] = {"error": str(e), "model": model_name}

    # Reset to Sabiazinho
    maritaca_client.model = "sabiazinho"

    return {
        "comparison": results,
        "recommendation": "Use 'sabiazinho' for cost efficiency, 'sabia-3' for complex queries",
        "timestamp": datetime.now(UTC).isoformat(),
    }
