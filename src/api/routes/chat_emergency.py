"""
Emergency chat endpoint - Minimal dependencies, maximum reliability
This endpoint ensures the chat always works, even if other services fail
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx
import random

from src.core import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat-emergency"])

# Request/Response models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    agent_id: str = "assistant"
    agent_name: str = "Assistente Cidadão.AI"
    message: str
    confidence: float = 0.95
    suggested_actions: List[str] = []
    metadata: Dict[str, Any] = {}

# Professional responses for common queries
RESPONSES = {
    "greeting": [
        "Olá! Sou o assistente do Cidadão.AI. Estou aqui para ajudar você a entender e investigar gastos públicos. Como posso ajudar?",
        "Bem-vindo ao Cidadão.AI! Posso ajudar você a analisar contratos, investigar gastos e entender melhor a transparência pública.",
        "Oi! Sou especializado em transparência pública. Posso investigar contratos, analisar gastos governamentais e muito mais. O que você gostaria de saber?"
    ],
    "investigation": [
        "Vou ajudar você a investigar. Posso analisar:\n• Contratos e licitações\n• Gastos por órgão público\n• Pagamentos a fornecedores\n• Evolução temporal de despesas\n\nQual área específica você quer investigar?",
        "Entendi que você quer investigar gastos públicos. Tenho acesso a dados de contratos, fornecedores e órgãos públicos. Por onde gostaria de começar?",
        "Perfeito! Posso investigar contratos suspeitos, analisar padrões de gastos e identificar anomalias. Me dê mais detalhes sobre o que você procura."
    ],
    "help": [
        "Posso ajudar você com:\n\n📊 **Análise de Contratos**: Investigar licitações e contratos públicos\n💰 **Gastos Públicos**: Acompanhar despesas governamentais\n🔍 **Detecção de Anomalias**: Identificar padrões irregulares\n📈 **Relatórios**: Gerar análises detalhadas\n\nO que você gostaria de fazer?",
        "O Cidadão.AI oferece várias funcionalidades:\n• Investigar contratos específicos\n• Analisar gastos de órgãos públicos\n• Comparar fornecedores\n• Detectar anomalias em pagamentos\n• Gerar relatórios de transparência\n\nComo posso ajudar?",
        "Aqui está o que posso fazer por você:\n1. Buscar informações sobre contratos\n2. Analisar tendências de gastos\n3. Identificar fornecedores frequentes\n4. Detectar possíveis irregularidades\n5. Criar visualizações de dados\n\nQual dessas opções te interessa?"
    ],
    "default": [
        "Entendi sua pergunta. Para te ajudar melhor com transparência pública, você pode:\n• Pedir para investigar contratos específicos\n• Solicitar análise de gastos de um órgão\n• Buscar informações sobre fornecedores\n\nComo posso ajudar?",
        "Interessante sua questão! No contexto de transparência pública, posso ajudar você a entender gastos governamentais, contratos e licitações. Que tipo de informação você procura?",
        "Certo! Como assistente de transparência, posso investigar dados públicos, analisar contratos e identificar padrões. Me conte mais sobre o que você quer descobrir."
    ]
}

def detect_intent(message: str) -> str:
    """Simple intent detection based on keywords"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["olá", "oi", "bom dia", "boa tarde", "boa noite", "prazer"]):
        return "greeting"
    elif any(word in message_lower for word in ["investigar", "verificar", "analisar", "buscar", "procurar"]):
        return "investigation"
    elif any(word in message_lower for word in ["ajuda", "ajudar", "pode", "consegue", "o que", "como"]):
        return "help"
    else:
        return "default"

async def try_maritaca(message: str) -> Optional[str]:
    """Try to get response from Maritaca AI"""
    api_key = os.getenv("MARITACA_API_KEY")
    if not api_key:
        return None
        
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://chat.maritaca.ai/api/chat/inference",
                headers={"authorization": f"Bearer {api_key}"},
                json={
                    "messages": [
                        {
                            "role": "system", 
                            "content": "Você é um assistente especializado em transparência pública brasileira. Ajude os cidadãos a entender gastos governamentais, contratos e licitações. Seja claro, objetivo e sempre sugira ações específicas."
                        },
                        {"role": "user", "content": message}
                    ],
                    "model": "sabia-3",
                    "temperature": 0.7,
                    "max_tokens": 400
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("answer", None)
                
    except Exception as e:
        logger.warning(f"Maritaca request failed: {e}")
    
    return None

@router.post("/emergency", response_model=ChatResponse)
async def chat_emergency(request: ChatRequest) -> ChatResponse:
    """
    Emergency chat endpoint - Always returns a valid response
    Tries Maritaca AI first, falls back to intelligent responses
    """
    session_id = request.session_id or f"emergency_{datetime.now().timestamp()}"
    
    # Try Maritaca first
    maritaca_response = await try_maritaca(request.message)
    
    if maritaca_response:
        return ChatResponse(
            session_id=session_id,
            agent_id="maritaca",
            agent_name="Assistente Cidadão.AI (Maritaca)",
            message=maritaca_response,
            confidence=0.95,
            suggested_actions=["investigate_contracts", "analyze_expenses", "generate_report"],
            metadata={
                "model": "sabia-3",
                "backend": "maritaca_ai",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Fallback to intelligent responses
    intent = detect_intent(request.message)
    response_list = RESPONSES.get(intent, RESPONSES["default"])
    selected_response = random.choice(response_list)
    
    # Determine suggested actions based on intent
    if intent == "greeting":
        actions = ["start_investigation", "view_recent_contracts", "help"]
    elif intent == "investigation":
        actions = ["search_contracts", "analyze_supplier", "view_timeline"]
    elif intent == "help":
        actions = ["examples", "start_investigation", "documentation"]
    else:
        actions = ["help", "start_investigation", "search"]
    
    return ChatResponse(
        session_id=session_id,
        agent_id="system",
        agent_name="Assistente Cidadão.AI",
        message=selected_response,
        confidence=0.85,
        suggested_actions=actions,
        metadata={
            "backend": "intelligent_fallback",
            "intent": intent,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@router.get("/emergency/health")
async def emergency_health():
    """Health check for emergency endpoint"""
    maritaca_available = bool(os.getenv("MARITACA_API_KEY"))
    
    return {
        "status": "operational",
        "endpoint": "/api/v1/chat/emergency",
        "maritaca_configured": maritaca_available,
        "fallback_ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }