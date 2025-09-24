"""
Simple chat endpoint for Maritaca AI integration
Focused on making the chat work with minimal dependencies
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
from src.core import json_utils
import uuid
from datetime import datetime

from src.core import get_logger
from src.services.maritaca_client import MaritacaClient, MaritacaModel

logger = get_logger(__name__)
router = APIRouter(tags=["chat-simple"])

# Initialize Maritaca client
maritaca_client = None
MARITACA_API_KEY = os.environ.get("MARITACA_API_KEY")

if MARITACA_API_KEY:
    try:
        maritaca_client = MaritacaClient(
            api_key=MARITACA_API_KEY,
            model=MaritacaModel.SABIA_3
        )
        logger.info("Maritaca AI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Maritaca AI: {e}")
else:
    logger.warning("MARITACA_API_KEY not found - chat will use fallback responses")

class SimpleChatRequest(BaseModel):
    """Simple chat request"""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None

class SimpleChatResponse(BaseModel):
    """Simple chat response"""
    message: str
    session_id: str
    timestamp: str
    model_used: str = "fallback"

# System prompt for Cidadão.AI
SYSTEM_PROMPT = """Você é o assistente virtual do Cidadão.AI, uma plataforma de transparência pública brasileira.

Sua missão é ajudar cidadãos a entender gastos governamentais, contratos públicos e dados de transparência.

Características:
- Seja claro, objetivo e educativo
- Use linguagem acessível ao cidadão comum
- Quando perguntado sobre investigações, sugira exemplos como "investigar contratos de saúde" ou "analisar gastos com educação"
- Mantenha um tom profissional mas amigável
- Foque em transparência e accountability governamental

Você NÃO deve:
- Fazer análises políticas partidárias
- Expressar opiniões pessoais
- Fazer acusações sem base em dados"""

@router.post("/simple", response_model=SimpleChatResponse)
async def simple_chat(request: SimpleChatRequest) -> SimpleChatResponse:
    """
    Simple chat endpoint with Maritaca AI integration
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Check if Maritaca is available
        if maritaca_client:
            logger.info(f"Processing message with Maritaca AI: {request.message[:50]}...")
            
            # Prepare messages for Maritaca
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ]
            
            # Get response from Maritaca
            try:
                response = await maritaca_client.chat_completion(
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                
                logger.info("Maritaca AI response received successfully")
                
                return SimpleChatResponse(
                    message=response.content,
                    session_id=session_id,
                    timestamp=datetime.utcnow().isoformat(),
                    model_used=response.model
                )
                
            except Exception as e:
                logger.error(f"Maritaca AI error: {e}")
                # Fall through to fallback responses
        
        # Fallback responses when Maritaca is not available
        logger.info("Using fallback responses")
        
        message_lower = request.message.lower()
        
        # Simple intent detection
        if any(greeting in message_lower for greeting in ["olá", "oi", "bom dia", "boa tarde", "boa noite"]):
            response = "Olá! Sou o assistente do Cidadão.AI. Posso ajudá-lo a investigar gastos públicos, contratos governamentais e dados de transparência. Como posso ajudar?"
        elif "investigar" in message_lower or "analisar" in message_lower:
            response = "Para investigar dados públicos, você pode tentar:\n\n• 'Investigar contratos de saúde em São Paulo'\n• 'Analisar gastos com educação em 2024'\n• 'Verificar salários de servidores do Ministério da Saúde'\n\nQual área você gostaria de explorar?"
        elif "ajuda" in message_lower or "help" in message_lower:
            response = "O Cidadão.AI oferece:\n\n📊 **Análise de Contratos**: Investigue licitações e contratos públicos\n💰 **Gastos Públicos**: Acompanhe despesas governamentais\n👥 **Servidores**: Consulte salários e cargos públicos\n🔍 **Detecção de Anomalias**: Identifique padrões irregulares\n\nDigite o que deseja investigar!"
        elif "transparência" in message_lower or "portal" in message_lower:
            response = "O Portal da Transparência é a principal fonte de dados do governo federal brasileiro. Através do Cidadão.AI, você pode acessar esses dados de forma mais inteligente, com análises automáticas e detecção de anomalias. Que tipo de dado gostaria de explorar?"
        else:
            response = "Entendi sua pergunta. Para melhor ajudá-lo, você pode:\n\n1. Pedir para investigar contratos ou gastos específicos\n2. Solicitar análises de órgãos públicos\n3. Buscar informações sobre servidores\n\nPor exemplo: 'Quero investigar contratos do Ministério da Saúde'"
        
        return SimpleChatResponse(
            message=response,
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat(),
            model_used="fallback"
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar mensagem. Por favor, tente novamente."
        )

@router.get("/simple/status")
async def chat_status():
    """Check chat service status"""
    return {
        "maritaca_available": maritaca_client is not None,
        "api_key_configured": MARITACA_API_KEY is not None,
        "timestamp": datetime.utcnow().isoformat()
    }